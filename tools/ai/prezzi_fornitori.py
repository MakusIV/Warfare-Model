#!/usr/bin/env python3
"""Criterio di scelta dei fornitori OpenRouter basato SOLO sul costo effettivo.

Perche': i prezzi dei fornitori cambiano da un giorno all'altro (Baidu 0813: 0,145 $/M il 22/10, 1,32 $/M
il 23/10) e `sort: price` di OpenRouter non basta: il 95% dei nostri token e' lettura di cache, quindi un
fornitore con prompt economico ma cache cara (Relace, Wafer) costa 4-5 volte il minimo.

Cosa fa: legge gli endpoint del modello dall'API pubblica di OpenRouter (nessuna chiave), calcola il costo
di una sessione tipo con il mix di token misurato, tiene i fornitori ammessi entro TOL % dal minimo e
produce `options.provider` per `opencode.json`: `order` (i fornitori entro la soglia, dal piu' economico
per costo effettivo) con `allow_fallbacks: false`, e `max_price` (tetto in $/M su prompt e completion: se
un prezzo sale oltre la soglia, il fornitore esce dal routing e la richiesta non costa di piu'; se
escono tutti, la richiesta fallisce). Non si usa `sort: price` perche' ordina sul prezzo del prompt e,
fra i fornitori ammessi, metterebbe per primo il piu' economico in ingresso e non nel costo effettivo.

  python3 tools/ai/prezzi_fornitori.py                  mostra classifica e configurazione proposta
  python3 tools/ai/prezzi_fornitori.py --apply          riscrive opencode.json (provider e cost del modello)
  python3 tools/ai/prezzi_fornitori.py --tol 30 --ammessi streamlake,baidu

Ricontrollare prima di ogni delega OpenCode. Il mix di token e' una MISURA (sessione F8c1, 23/10/2026),
non un dato tarato per altre attivita': si cambia con --mix.
"""
import argparse
import json
import math
import re
import sys
import urllib.request
from pathlib import Path

MODELLO = "deepseek/deepseek-v4-pro-0813"
AMMESSI = "streamlake,sail-research,novita,baidu,deepseek"   # candidati: i primi tre fp8/fp4 provati o da provare
TOLLERANZA = 50.0                                             # [%] sopra il costo minimo
# Mix MISURATO (OpenRouter, F8c1 di oc-developer, 23/10/2026): token non in cache, in cache, di output.
MIX = (466785, 9354240, 64535)
UPTIME_MIN = 97.0                                             # [%] ultime 24 h
OPENCODE_JSON = Path(__file__).resolve().parents[2] / "opencode.json"


def endpoint_modello(modello):
    url = f"https://openrouter.ai/api/v1/models/{modello}/endpoints"
    with urllib.request.urlopen(url, timeout=30) as risposta:
        dati = json.load(risposta)
    return dati.get("data", dati)["endpoints"]


def costo_sessione(prezzi, mix):
    """Costo [$] del mix (non in cache, in cache, output) con i prezzi per token dell'endpoint."""
    non_cache, cache, uscita = mix
    return (non_cache * float(prezzi.get("prompt") or 0)
            + cache * float(prezzi.get("input_cache_read") or 0)
            + uscita * float(prezzi.get("completion") or 0))


def raggruppa(endpoint, mix):
    """Un record per fornitore (slug = tag fino alla '/'): il costo e' il PEGGIORE fra le sue varianti,
    perche' `only` ammette lo slug intero e non si sa quale variante risponde."""
    per_slug = {}
    for e in endpoint:
        slug = e["tag"].split("/")[0]
        prezzi = e["pricing"]
        record = dict(
            slug=slug, nome=e["provider_name"], tag=e["tag"], costo=costo_sessione(prezzi, mix),
            prompt=float(prezzi.get("prompt") or 0) * 1e6, completion=float(prezzi.get("completion") or 0) * 1e6,
            cache=float(prezzi.get("input_cache_read") or 0) * 1e6, quant=e.get("quantization") or "?",
            uptime=e.get("uptime_last_1d"), stato=e.get("status"),
            tool=bool((e.get("supports_tool_choice") or {}).get("auto")) and "tools" in (e.get("supported_parameters") or []))
        precedente = per_slug.get(slug)
        if precedente is None or record["costo"] > precedente["costo"]:
            per_slug[slug] = record
    return per_slug


def scegli(per_slug, ammessi, tolleranza):
    """(classifica completa, ammessi entro la soglia). Un fornitore e' escluso se non risponde (stato != 0), se
    l'uptime e' sotto UPTIME_MIN, o se non supporta i tool; il minimo e' calcolato sui candidati utilizzabili."""
    classifica = sorted(per_slug.values(), key=lambda r: r["costo"])
    usabili = [r for r in classifica if r["slug"] in ammessi and r["tool"] and r["stato"] == 0
               and (r["uptime"] is None or r["uptime"] >= UPTIME_MIN)]
    if not usabili:
        return classifica, []
    soglia = usabili[0]["costo"] * (1 + tolleranza / 100)
    return classifica, [r for r in usabili if r["costo"] <= soglia * (1 + 1e-9)]


def arrotonda_su(valore, cifre=3):
    fattore = 10 ** cifre
    return math.ceil(valore * fattore - 1e-9) / fattore


def configurazione(scelti):
    return {
        "order": [r["slug"] for r in scelti],
        "allow_fallbacks": False,
        "max_price": {"prompt": arrotonda_su(max(r["prompt"] for r in scelti)),
                      "completion": arrotonda_su(max(r["completion"] for r in scelti))},
    }


def stampa(classifica, ammessi, scelti, mix):
    minimo = scelti[0]["costo"] if scelti else None
    print(f"Mix (non in cache / in cache / output): {mix[0]:,} / {mix[1]:,} / {mix[2]:,} token")
    print(f"{'fornitore':<14}{'prompt':>8}{'cache':>8}{'output':>8}  {'quant':<7}{'uptime':>7}  {'$ sessione':>10}  {'vs min':>7}  stato")
    for r in classifica:
        nota = []
        if r["slug"] not in ammessi:
            nota.append("non candidato")
        elif r in scelti:
            nota.append("AMMESSO")
        else:
            nota.append("oltre soglia / non utilizzabile")
        rel = f"{(r['costo'] / minimo - 1) * 100:+.0f}%" if minimo else ""
        uptime = f"{r['uptime']:.1f}%" if r["uptime"] is not None else "n/d"
        print(f"{r['slug']:<14}{r['prompt']:>8.3f}{r['cache']:>8.3f}{r['completion']:>8.2f}  {r['quant']:<7}{uptime:>7}  "
              f"{r['costo']:>10.3f}  {rel:>7}  {', '.join(nota)}")


def compatta(testo):
    """Array brevi di sole stringhe (fino a 60 caratteri) su una riga, come `order` in opencode.json; la
    `whitelist`, piu' lunga, resta su piu' righe."""
    def riga(m):
        voci = re.findall(r'"[^"\n]*"', m.group(1))
        compatto = "[" + ", ".join(voci) + "]"
        return compatto if len(compatto) <= 60 else m.group(0)
    return re.sub(r'\[\s+((?:"[^"\]\n]*",?\s*)+)\]', riga, testo)


def applica(modello, provider, cost):
    percorso = OPENCODE_JSON
    configurazione_json = json.loads(percorso.read_text(encoding="utf-8"))
    modelli = configurazione_json["provider"]["openrouter"]["models"]
    voce = modelli.setdefault(modello, {})
    voce["cost"] = cost
    voce.setdefault("options", {})["provider"] = provider
    percorso.write_text(compatta(json.dumps(configurazione_json, indent=2, ensure_ascii=False)) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--modello", default=MODELLO)
    parser.add_argument("--ammessi", default=AMMESSI, help="slug dei fornitori candidati, separati da virgola")
    parser.add_argument("--tol", type=float, default=TOLLERANZA, help="[%%] sopra il costo minimo (default %(default)s)")
    parser.add_argument("--mix", default=",".join(str(v) for v in MIX), help="token non in cache,in cache,output")
    parser.add_argument("--apply", action="store_true", help="riscrive opencode.json")
    args = parser.parse_args()

    mix = tuple(int(v) for v in args.mix.split(","))
    ammessi = [s.strip() for s in args.ammessi.split(",") if s.strip()]
    classifica, scelti = scegli(raggruppa(endpoint_modello(args.modello), mix), ammessi, args.tol)
    stampa(classifica, ammessi, scelti, mix)

    if not scelti:
        print("\nNessun fornitore utilizzabile fra i candidati: opencode.json NON toccato.")
        return 1

    provider = configurazione(scelti)
    primo = scelti[0]
    cost = {"input": round(primo["prompt"], 6), "output": round(primo["completion"], 6),
            "cache_read": round(primo["cache"], 6)}
    print(f"\nTolleranza {args.tol:g}% sul minimo ({scelti[0]['slug']}, {scelti[0]['costo']:.3f} $ a sessione).")
    print(f"options.provider = {json.dumps(provider)}")
    print(f"cost (del piu' economico) = {json.dumps(cost)}")

    if args.apply:
        applica(args.modello, provider, cost)
        print(f"\nScritto {OPENCODE_JSON}")
    else:
        print("\nDry-run: aggiungi --apply per scrivere opencode.json.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

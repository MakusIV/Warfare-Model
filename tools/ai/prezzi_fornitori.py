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
  python3 tools/ai/prezzi_fornitori.py --tol 30 --solo streamlake,baidu
  bash tools/ai/oc-delega.sh --command esegui "<compito>"   aggiorna opencode.json e poi lancia `oc run`

Candidati: TUTTI i fornitori del modello che supportano i tool, rispondono (stato 0) e hanno uptime >= UPTIME_MIN,
meno ESCLUSI e meno quelli a bassa precisione (fp4 e simili) non elencati in APPROVATI_FP4: un fornitore con uno
sconto entra da solo al lancio successivo. Qualita': un fornitore a bassa precisione approvato sta sempre IN CODA
a `order` (solo ripiego), anche se costa meno, perche' i pesi fp4 danno risultati meno affidabili sui compiti lunghi e
precisi (tool call con argomenti esatti, codice che compila); non c'e' una misura di questo effetto su DeepSeek V4 Pro.

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
ESCLUSI = ""                                                  # slug mai da usare (es. un fornitore che sbaglia i tool call)
APPROVATI_FP4 = "sail-research"                               # bassa precisione approvata dall'utente (23/10/2026), solo in coda
QUANT_BASSA = ("fp4", "mxfp4", "nvfp4", "int4", "fp6")        # quantizzazioni considerate a bassa precisione
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
        record["bassa"] = any(q in (record["quant"] or "").lower() for q in QUANT_BASSA)
        precedente = per_slug.get(slug)
        if precedente is None:
            per_slug[slug] = record
            continue
        # `only`/`order` ammettono lo slug intero: vale la variante peggiore per costo, precisione e uptime.
        bassa = precedente["bassa"] or record["bassa"]
        if record["costo"] > precedente["costo"]:
            record["bassa"] = bassa
            per_slug[slug] = record
        else:
            precedente["bassa"] = bassa
    return per_slug


def motivo_esclusione(r, solo, esclusi, approvati_fp4):
    """None se il fornitore e' utilizzabile, altrimenti il motivo (per la tabella)."""
    if solo and r["slug"] not in solo:
        return "fuori da --solo"
    if r["slug"] in esclusi:
        return "escluso"
    if not r["tool"]:
        return "senza tool call"
    if r["stato"] != 0:
        return "non risponde"
    if r["uptime"] is not None and r["uptime"] < UPTIME_MIN:
        return f"uptime < {UPTIME_MIN:g}%"
    if r["bassa"] and r["slug"] not in approvati_fp4:
        return "bassa precisione non approvata"
    return None


def scegli(per_slug, solo, esclusi, approvati_fp4, tolleranza):
    """(classifica completa, ammessi entro la soglia, in ordine di preferenza).

    Utilizzabile = `motivo_esclusione` None. Il minimo e' il costo del piu' economico fra gli utilizzabili. Ordine
    finale: prima quelli a precisione piena o sconosciuta, per costo; poi (solo ripiego) i bassa precisione
    approvati, per costo."""
    classifica = sorted(per_slug.values(), key=lambda r: r["costo"])
    usabili = [r for r in classifica if motivo_esclusione(r, solo, esclusi, approvati_fp4) is None]
    if not usabili:
        return classifica, []
    soglia = usabili[0]["costo"] * (1 + tolleranza / 100)
    entro = [r for r in usabili if r["costo"] <= soglia * (1 + 1e-9)]
    return classifica, sorted(entro, key=lambda r: (r["bassa"], r["costo"]))


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


def stampa(classifica, scelti, mix, solo, esclusi, approvati_fp4):
    minimo = min(r["costo"] for r in scelti) if scelti else None
    print(f"Mix (non in cache / in cache / output): {mix[0]:,} / {mix[1]:,} / {mix[2]:,} token")
    print(f"{'fornitore':<14}{'prompt':>8}{'cache':>8}{'output':>8}  {'quant':<7}{'uptime':>7}  {'$ sessione':>10}  {'vs min':>7}  stato")
    for r in classifica:
        motivo = motivo_esclusione(r, solo, esclusi, approvati_fp4)
        if motivo:
            nota = motivo
        elif r in scelti:
            nota = f"AMMESSO #{scelti.index(r) + 1}" + (" (ripiego: bassa precisione)" if r["bassa"] else "")
        else:
            nota = "oltre la soglia"
        rel = f"{(r['costo'] / minimo - 1) * 100:+.0f}%" if minimo else ""
        uptime = f"{r['uptime']:.1f}%" if r["uptime"] is not None else "n/d"
        print(f"{r['slug']:<14}{r['prompt']:>8.3f}{r['cache']:>8.3f}{r['completion']:>8.2f}  {r['quant']:<7}{uptime:>7}  "
              f"{r['costo']:>10.3f}  {rel:>7}  {nota}")


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
    parser.add_argument("--solo", default="", help="restringe i candidati a questi slug (default: tutti)")
    parser.add_argument("--escludi", default=ESCLUSI, help="slug da non usare mai, separati da virgola")
    parser.add_argument("--approva-fp4", default=APPROVATI_FP4,
                        help="slug a bassa precisione ammessi (solo in coda a order), separati da virgola")
    parser.add_argument("--tol", type=float, default=TOLLERANZA, help="[%%] sopra il costo minimo (default %(default)s)")
    parser.add_argument("--mix", default=",".join(str(v) for v in MIX), help="token non in cache,in cache,output")
    parser.add_argument("--apply", action="store_true", help="riscrive opencode.json")
    args = parser.parse_args()

    mix = tuple(int(v) for v in args.mix.split(","))
    elenco = lambda testo: [v.strip() for v in testo.split(",") if v.strip()]
    solo, esclusi, approvati = elenco(args.solo), elenco(args.escludi), elenco(args.approva_fp4)
    classifica, scelti = scegli(raggruppa(endpoint_modello(args.modello), mix), solo, esclusi, approvati, args.tol)
    stampa(classifica, scelti, mix, solo, esclusi, approvati)

    if not scelti:
        print("\nNessun fornitore utilizzabile fra i candidati: opencode.json NON toccato.")
        return 1

    provider = configurazione(scelti)
    primo = scelti[0]
    cost = {"input": round(primo["prompt"], 6), "output": round(primo["completion"], 6),
            "cache_read": round(primo["cache"], 6)}
    minimo = min(scelti, key=lambda r: r["costo"])
    print(f"\nTolleranza {args.tol:g}% sul minimo ({minimo['slug']}, {minimo['costo']:.3f} $ a sessione).")
    print(f"options.provider = {json.dumps(provider)}")
    print(f"cost (del primo in order) = {json.dumps(cost)}")

    if args.apply:
        applica(args.modello, provider, cost)
        print(f"\nScritto {OPENCODE_JSON}")
    else:
        print("\nDry-run: aggiungi --apply per scrivere opencode.json.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

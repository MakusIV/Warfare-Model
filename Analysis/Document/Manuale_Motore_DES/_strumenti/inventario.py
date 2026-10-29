"""Inventario dei moduli del core DES, estratto dal codice con `ast` (sola lettura).

Serve a due cose: dare ai diagrammi del manuale una base verificata (classi, campi, metodi, funzioni,
chiamate e dipendenze fra moduli) e controllare che gli identificatori scritti nei diagrammi esistano.

Uso, dalla root del repo (interprete della macchina, es. `.direnv/python-3.12/bin/python3`):
    python3 -I Analysis/Document/Manuale_Motore_DES/_strumenti/inventario.py modulo [Logic/Readiness ...]
    python3 -I ... inventario.py --dipendenze          # grafo degli import fra i moduli del core
    python3 -I ... inventario.py --chiamate Logic/Session_Simulator run_session
    python3 -I ... inventario.py --controlla file.md   # identificatori dei blocchi mermaid non trovati nel core

Non importa i moduli del progetto: legge solo i sorgenti. Non scrive nulla.
"""
import ast
import re
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[4]
SORGENTI = RADICE / 'Code' / 'Dynamic_War_Manager' / 'Source'
PREFISSO = 'Code.Dynamic_War_Manager.Source.'

# Core del motore DES (perimetro del pilota); i satelliti restano fuori.
CORE = (
    'Command/Session_Types', 'Command/Mission_Types', 'Command/Campaign_Types',
    'Logic/Session_Simulator', 'Logic/Contact_Scheduler', 'Logic/Engagement_Resolver',
    'Logic/Fire_Control', 'Logic/Fuel_Model', 'Logic/Damage_Model', 'Logic/Mission_Adapter',
    'Logic/Area_Fire', 'Logic/Session_Validator', 'Logic/Readiness', 'Logic/Session_Campaign',
    'Utility/Session_Rng',
)


def _albero(modulo):
    percorso = SORGENTI / (modulo + '.py')
    return ast.parse(percorso.read_text(encoding='utf-8'), filename=str(percorso))


def _nome(nodo):
    """Nome puntato di un'espressione (Name/Attribute), altrimenti None."""
    if isinstance(nodo, ast.Name):
        return nodo.id
    if isinstance(nodo, ast.Attribute):
        base = _nome(nodo.value)
        return f'{base}.{nodo.attr}' if base else nodo.attr
    return None


def _firma(f):
    args = [a.arg for a in f.args.posonlyargs + f.args.args + f.args.kwonlyargs]
    if f.args.vararg:
        args.append('*' + f.args.vararg.arg)
    if f.args.kwarg:
        args.append('**' + f.args.kwarg.arg)
    return f'{f.name}({", ".join(args)})'


def inventario(modulo):
    """Classi (basi, campi, metodi con riga) e funzioni di primo livello di un modulo."""
    albero = _albero(modulo)
    classi, funzioni = [], []
    for nodo in albero.body:
        if isinstance(nodo, ast.ClassDef):
            campi, metodi = [], []
            for c in nodo.body:
                if isinstance(c, ast.AnnAssign) and isinstance(c.target, ast.Name):
                    campi.append(c.target.id)
                elif isinstance(c, ast.Assign):
                    campi += [t.id for t in c.targets if isinstance(t, ast.Name)]
                elif isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    metodi.append((_firma(c), c.lineno))
            classi.append({'nome': nodo.name, 'riga': nodo.lineno,
                           'basi': [b for b in map(_nome, nodo.bases) if b],
                           'campi': campi, 'metodi': metodi})
        elif isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funzioni.append((_firma(nodo), nodo.lineno))
    return classi, funzioni


def dipendenze(moduli=CORE):
    """Per ogni modulo del core, i moduli del core che importa (`from X import ...` e `import X`)."""
    per_nome = {m: m.replace('/', '.') for m in moduli}
    risultato = {}
    for modulo in moduli:
        trovati = set()
        for nodo in ast.walk(_albero(modulo)):
            if isinstance(nodo, ast.ImportFrom) and nodo.module:
                nome = nodo.module[len(PREFISSO):] if nodo.module.startswith(PREFISSO) else None
                if nome:
                    trovati.update(m for m, p in per_nome.items() if p == nome and m != modulo)
                    # `from ...Logic import Mission_Adapter as MA`: il modulo e' un nome importato
                    for a in nodo.names:
                        trovati.update(m for m, p in per_nome.items()
                                       if p == f'{nome}.{a.name}' and m != modulo)
            elif isinstance(nodo, ast.Import):
                for a in nodo.names:
                    nome = a.name[len(PREFISSO):] if a.name.startswith(PREFISSO) else None
                    if nome:
                        trovati.update(m for m, p in per_nome.items() if p == nome and m != modulo)
        risultato[modulo] = sorted(trovati)
    return risultato


def chiamate(modulo, funzione):
    """Nomi chiamati dal corpo di una funzione o metodo (in ordine di comparsa, senza ripetizioni)."""
    for nodo in ast.walk(_albero(modulo)):
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)) and nodo.name == funzione:
            visti, ordine = set(), []
            for c in sorted((n for n in ast.walk(nodo) if isinstance(n, ast.Call)),
                            key=lambda n: (n.lineno, n.col_offset)):
                nome = _nome(c.func)
                if nome and nome not in visti:
                    visti.add(nome)
                    ordine.append((nome, c.lineno))
            return nodo.lineno, ordine
    return None, []


def tutti_i_nomi(moduli=CORE):
    """Insieme degli identificatori noti nel core: classi, campi, metodi, funzioni, argomenti, variabili."""
    nomi = set()
    for modulo in moduli:
        for nodo in ast.walk(_albero(modulo)):
            if isinstance(nodo, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                nomi.add(nodo.name)
            if isinstance(nodo, ast.arg):
                nomi.add(nodo.arg)
            if isinstance(nodo, ast.Name):
                nomi.add(nodo.id)
            if isinstance(nodo, ast.Attribute):
                nomi.add(nodo.attr)
        nomi.add(modulo.split('/')[-1])
    return nomi


def controlla(file_md):
    """Identificatori (con `_` o CamelCase) dei blocchi mermaid che il core non conosce.

    Euristica: segnala candidati da guardare a mano, non errori certi (il testo delle etichette
    contiene anche parole italiane e nomi di moduli fuori dal core)."""
    testo = Path(file_md).read_text(encoding='utf-8')
    noti = tutti_i_nomi()
    segnalati = []
    for blocco in re.finditer(r'```mermaid\n(.*?)```', testo, re.S):
        riga0 = testo[:blocco.start()].count('\n') + 2
        for i, riga in enumerate(blocco.group(1).splitlines()):
            for tok in re.findall(r'[A-Za-z_][A-Za-z0-9_]*', riga):
                if len(tok) > 3 and ('_' in tok or re.search(r'[a-z][A-Z]', tok) or tok[0].isupper() and tok.isalpha() and tok != tok.upper()):
                    if tok not in noti:
                        segnalati.append((riga0 + i, tok))
    return segnalati


def _stampa_modulo(modulo):
    classi, funzioni = inventario(modulo)
    print(f'# {modulo}.py')
    for c in classi:
        basi = f'({", ".join(c["basi"])})' if c['basi'] else ''
        print(f'class {c["nome"]}{basi}  :{c["riga"]}')
        if c['campi']:
            print('   campi:', ', '.join(c['campi']))
        for firma, riga in c['metodi']:
            print(f'   {firma}  :{riga}')
    for firma, riga in funzioni:
        print(f'def {firma}  :{riga}')


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    if argv[0] == '--dipendenze':
        for modulo, dip in dipendenze().items():
            print(f'{modulo} -> {", ".join(dip) if dip else "(nessuna dipendenza nel core)"}')
    elif argv[0] == '--chiamate' and len(argv) == 3:
        riga, ordine = chiamate(argv[1], argv[2])
        print(f'{argv[1]}.{argv[2]}  :{riga}')
        for nome, r in ordine:
            print(f'   :{r}  {nome}')
    elif argv[0] == '--controlla' and len(argv) == 2:
        for riga, tok in controlla(argv[1]):
            print(f'{argv[1]}:{riga}  {tok}')
    else:
        for modulo in argv:
            _stampa_modulo(modulo)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

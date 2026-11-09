import subprocess, re, csv, sys
from collections import defaultdict

REPO = sys.argv[1]
OUT = sys.argv[2]
FASES = [("F3", "517a399", "d0d758d"), ("F4", "d0d758d", "07dacc9"), ("F5", "07dacc9", "7c0326d")]

def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True, check=True).stdout

def categoria(p):
    if p.startswith("src/main/java/"): return "producao"
    if p.startswith("src/test/"): return "testes"
    return "configuracao"

rows = []
for fase, a, b in FASES:
    st = {}
    for l in git("diff", "--no-renames", "--name-status", f"{a}..{b}").splitlines():
        s, p = l.split("\t")
        st[p] = s
    agg = defaultdict(lambda: defaultdict(int))
    for l in git("diff", "--no-renames", "--numstat", f"{a}..{b}").splitlines():
        ad, rm, p = l.split("\t")
        for c in (categoria(p), "total"):
            d = agg[c]
            d[{"M": "alterados", "A": "criados", "D": "apagados"}[st[p]]] += 1
            d["linhas_adicionadas"] += int(ad)
            d["linhas_removidas"] += int(rm)
    for c in ("producao", "testes", "configuracao", "total"):
        d = agg[c]
        rows.append([fase, f"{a}..{b}", c, d["alterados"], d["criados"], d["apagados"],
                     d["linhas_adicionadas"], d["linhas_removidas"],
                     d["linhas_adicionadas"] + d["linhas_removidas"]])

with open(OUT, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["fase", "commits", "categoria", "arquivos_alterados", "arquivos_criados",
                "arquivos_apagados", "linhas_adicionadas", "linhas_removidas", "linhas_total"])
    w.writerows(rows)

# Linhas de estilo na F3
MAP_ADD = re.compile(r"@(Get|Post|Put|Delete|Patch)Mapping\(")
MAP_RM = re.compile(r"@RequestMapping\(.*method\s*=\s*RequestMethod\.")
MAP_IMP_ADD = re.compile(r"^import org\.springframework\.web\.bind\.annotation\.(Get|Post|Put|Delete|Patch)Mapping;")
MAP_IMP_RM = re.compile(r"^import org\.springframework\.web\.bind\.annotation\.RequestMethod;")
AUT_RM = re.compile(r"^\s*@Autowired\s*$")
AUT_IMP_RM = re.compile(r"^import org\.springframework\.beans\.factory\.annotation\.Autowired;")
SEQ_ADD = re.compile(r"\.(getFirst|removeFirst)\(\)")
SEQ_RM = re.compile(r"\.(get|remove)\(0\)")

cont = defaultdict(lambda: defaultdict(int))
arquivo = None
for l in git("diff", "--no-renames", "-U0", "517a399..d0d758d").splitlines():
    if l.startswith("+++ "):
        arquivo = l[6:]
        continue
    if l.startswith("--- ") or l.startswith("@@") or l.startswith("diff ") or l.startswith("index "):
        continue
    if not l or l[0] not in "+-":
        continue
    sinal, t = l[0], l[1:]
    cat = categoria(arquivo)
    chave = None
    if sinal == "+" and MAP_ADD.search(t): chave = ("mapeamentos", "anotacao")
    elif sinal == "-" and MAP_RM.search(t): chave = ("mapeamentos", "anotacao")
    elif sinal == "+" and MAP_IMP_ADD.search(t): chave = ("mapeamentos", "import")
    elif sinal == "-" and MAP_IMP_RM.search(t): chave = ("mapeamentos", "import")
    elif sinal == "-" and AUT_RM.search(t): chave = ("autowired", "anotacao")
    elif sinal == "-" and AUT_IMP_RM.search(t): chave = ("autowired", "import")
    elif sinal == "+" and SEQ_ADD.search(t): chave = ("getfirst_removefirst", "chamada")
    elif sinal == "-" and SEQ_RM.search(t): chave = ("getfirst_removefirst", "chamada")
    if chave:
        cont[(chave[0], cat)][("add" if sinal == "+" else "rm", chave[1])] += 1

print("ESTILO_F3")
for (tipo, cat), d in sorted(cont.items()):
    print(tipo, cat, dict(d))

# Recalcula as contagens de dependencias e plugins desatualizados das tres medicoes
# a partir das saidas brutas guardadas, com as funcoes corrigidas do medir.py.
# Nao roda nenhum build.
# Uso: python3 recalcular-contagens.py <pasta kit/scripts> <pasta medicoes>
import os
import sys

sys.path.insert(0, sys.argv[1])
import medir  # noqa: E402

MEDICOES = sys.argv[2]
PASTAS = [
    ("legado", "legado-20261103-174411"),
    ("openrewrite", "openrewrite-20261109-100726"),
    ("final", "final-20261109-113524"),
]


def ler(pasta, arquivo):
    with open(os.path.join(MEDICOES, pasta, arquivo), encoding="utf-8", errors="replace") as f:
        return f.read()


print("fase,pasta,deps_desatualizadas,deps_desatualizadas_mesma_major,plugins_desatualizados")
for fase, pasta in PASTAS:
    print(",".join(str(x) for x in (
        fase, pasta,
        medir.contar_deps_desatualizadas(ler(pasta, "versions-dependency-updates.log")),
        medir.contar_deps_desatualizadas(ler(pasta, "versions-dependency-updates-mesma-major.log")),
        medir.contar_plugins_desatualizados(ler(pasta, "versions-plugin-updates.log")),
    )))

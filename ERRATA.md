# Errata das medições

O `scripts/medir.py` tinha dois erros de contagem, encontrados depois das medições. Os dois foram
corrigidos no script, e as três medições (F1, T05 e T07) foram recalculadas a partir das saídas
brutas já guardadas, **sem rodar os builds de novo**. As saídas originais do script foram
preservadas e continuam mostrando os valores antigos.

## Erro 1: entradas quebradas em duas linhas (dependências)

Quando o `grupo:artefato` é longo, o `versions-maven-plugin` escreve o nome numa linha e as versões
(`atual -> nova`) na linha seguinte:

```
[INFO]   com.fasterxml.jackson.datatype:jackson-datatype-jsr310 ...
[INFO]                                                         2.21.4 -> 2.23.0
```

O script só contava linhas com o nome e a seta juntos e deixava essas entradas de fora. Correção:
a função `_juntar_linhas_quebradas` junta as duas linhas antes de contar.

## Erro 2: versões anteriores nos blocos "Require Maven" (plugins)

O relatório de plugins tem blocos "Require Maven X.Y.Z to use the following plugin updates", que
listam também versões **anteriores** à usada:

```
[INFO]   org.jacoco:jacoco-maven-plugin .................... 0.8.16 -> 0.8.2
```

O script contava essas linhas como atualização. Correção: a função `_versao_maior` faz o plugin só
contar quando a versão nova é maior que a atual.

## Valores antes e depois

| Medição | Coluna | Saída original | Corrigido |
|---|---|---:|---:|
| F1 (legado, 517a399) | deps_desatualizadas | 18 | 23 |
| | deps_desatualizadas_mesma_major | 18 | 23 |
| | plugins_desatualizados | 4 | 4 |
| T05 (openrewrite, d0d758d) | deps_desatualizadas | 17 | 22 |
| | deps_desatualizadas_mesma_major | 10 | 11 |
| | plugins_desatualizados | 3 | 2 |
| T07 (final, 7c0326d) | deps_desatualizadas | 17 | 22 |
| | deps_desatualizadas_mesma_major | 10 | 11 |
| | plugins_desatualizados | 2 | 1 |

## O que a contagem de dependências inclui

`deps_desatualizadas` conta as **entradas** que o `versions-maven-plugin` aponta como desatualizadas.
Ela não é uma fração de `deps_declaradas`, porque inclui, além das dependências diretas, o
`spring-boot-maven-plugin` do `pluginManagement`:

| Medição | Dependências declaradas | Desatualizadas: dependências diretas | Desatualizadas: `pluginManagement` | Total |
|---|---:|---:|---:|---:|
| F1 | 24 | 22 | 1 | 23 |
| T05 | 26 | 21 | 1 | 22 |
| T07 | 26 | 21 | 1 | 22 |

Na mesma major, o `pluginManagement` só entra no F1 (22 + 1 = 23); no T05 e no T07 são 11
dependências diretas.

Limite conhecido do indicador de plugins: um plugin sem `<version>` no `pom.xml`, com a versão vinda
do parent, pode não aparecer no relatório. É o caso do `build-helper-maven-plugin` 3.2.0 da versão
final (ver `evidencias/T07/dependencias.md`).

## Do relatório bruto até a tabela do TCC

1. Saídas brutas de cada execução (arquivos `versions-*.log`):
   `evidencias/F1/medicao-legado-20261103-174411/`, `evidencias/T05/medicao-openrewrite-20261109-100726/`
   e `evidencias/T07/medicao-final-20261109-113524/`.
2. Recontagem com o script corrigido: `evidencias/T07/recalcular-contagens.py`, com a saída em
   `evidencias/T07/recalculo-contagens.txt`.
3. Valores antigos e corrigidos, coluna por coluna: `medicoes/correcao-contagem-dependencias.csv`.
4. Tabela atual: `medicoes/medicoes.csv`. As versões anteriores ficaram em `medicoes/medicoes-v3.csv`
   (antes das duas correções) e `medicoes/medicoes-v4.csv` (só com a correção das dependências).
5. As Tabelas 1 e 2 do TCC usam os valores de `medicoes/medicoes.csv`.

Arquivos preservados com os valores antigos, por serem a saída original de cada execução:
`evidencias/T05/saida-medir.txt`, `evidencias/T05/linha-medicoes.csv`,
`evidencias/T07/saida-medir.txt` e `evidencias/T07/linha-medicoes.csv`.

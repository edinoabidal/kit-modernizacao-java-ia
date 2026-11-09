# medir.py — Script de medição do TCC

Mede o projeto **Spring PetClinic REST** sempre do mesmo jeito, nas três fases do
trabalho: `legado`, `openrewrite` e `final`. O script **não altera** nenhum arquivo
do projeto: ele usa o Maven Wrapper (`mvnw`) do próprio repositório e chama plugins
extras (como o `versions-maven-plugin`) pela linha de comando, com versão fixa.

Usa apenas **Python 3 + biblioteca padrão** (nenhum `pip install`).

## Como rodar

```bash
python3 kit/scripts/medir.py \
  --projeto   /caminho/para/spring-petclinic-rest \
  --fase      legado \
  --java-home /caminho/para/o/jdk \
  --saida     /caminho/para/medicoes        # opcional
```

### Parâmetros

| Parâmetro | Obrigatório | Descrição |
|---|---|---|
| `--projeto`   | sim | Caminho do repositório `spring-petclinic-rest`. |
| `--fase`      | sim | Rótulo da medição: `legado`, `openrewrite` ou `final`. |
| `--java-home` | sim | JDK usado **nesta** medição. Vira `JAVA_HOME` só nos comandos do script (não mexe no sistema). |
| `--saida`     | não | Pasta de saída. Padrão: `medicoes/` ao lado da pasta `kit`. |

### Exemplo (fase legado com JDK 8)

```bash
python3 kit/scripts/medir.py \
  --projeto   ../spring-petclinic-rest \
  --fase      legado \
  --java-home /mnt/c/Users/<usuario>/java/jdk8u-linux-x64
```

## O que o script faz (em ordem)

1. Lê commit, versão do Java (do `--java-home`) e versão do Maven (do wrapper).
2. Grava `git status --porcelain` **antes** da medição.
3. Roda `mvnw -B clean verify` e salva o **log completo**; mede a duração e classifica o resultado.
4. Soma os relatórios do **Surefire** (`target/surefire-reports/TEST-*.xml`).
5. Lê a cobertura do **JaCoCo** (`target/site/jacoco/jacoco.csv`). Se não existir, registra `N/D`.
6. Consulta **dependências/plugins/parent** desatualizados com o `versions-maven-plugin` (versão fixa `2.16.2`), ignorando pré-releases (SNAPSHOT, alpha, beta, milestone, RC).
7. Grava `git status --porcelain` **depois** da medição.
8. Acrescenta uma linha em `medicoes.csv` (cria o cabeçalho na primeira vez) e guarda as saídas brutas em `medicoes/<fase>-<data_hora>/`.

Uma **falha de build não interrompe** o script: ele registra o que conseguiu medir e
preenche o resto com `N/D`.

## Saídas brutas (por execução)

Em `medicoes/<fase>-<AAAAMMDD-HHMMSS>/`:

- `build.log` — saída completa do `clean verify`
- `jacoco.csv` — cópia do relatório de cobertura do projeto (se gerado nesta execução)
- `versions-dependency-updates.log` — dependências desatualizadas (qualquer major)
- `versions-dependency-updates-mesma-major.log` — dependências desatualizadas na mesma major
- `versions-plugin-updates.log`
- `versions-parent-updates.log` — parent mais recente (qualquer major)
- `versions-parent-updates-mesma-major.log` — parent mais recente na mesma major
- `git-status-antes.txt` e `git-status-depois.txt`

## Colunas do `medicoes.csv`

| Coluna | Significado |
|---|---|
| `data_hora` | Data e hora da medição (`AAAA-MM-DD HH:MM:SS`). |
| `fase` | `legado`, `openrewrite` ou `final`. |
| `commit` | `git rev-parse --short HEAD` do projeto. |
| `java_versao` | Versão do Java usado (ex.: `1.8.0_504`). |
| `maven_versao` | Versão do Maven do wrapper (ex.: `3.6.3`). |
| `build_resultado` | `sucesso`, `falha_compilacao`, `falha_testes`, `falha_cobertura` ou `outra_falha`. |
| `build_codigo_saida` | Código de saída do comando Maven (0 = ok). |
| `build_duracao_s` | Duração do `clean verify` em segundos. |
| `testes_total` | Total de testes somados do Surefire. |
| `testes_falhas` | Total de falhas (`failures`). |
| `testes_erros` | Total de erros (`errors`). |
| `testes_ignorados` | Total de ignorados (`skipped`). |
| `cobertura_linhas_pct` | Cobertura de linhas do projeto inteiro (%). |
| `cobertura_ramos_pct` | Cobertura de ramos/branches do projeto inteiro (%). |
| `deps_declaradas` | Nº de `<dependency>` na seção `<dependencies>` raiz do `pom.xml`. |
| `deps_desatualizadas` | Nº de dependências com versão estável mais nova disponível (qualquer major). |
| `deps_desatualizadas_mesma_major` | Nº de dependências com atualização **dentro da mesma versão major** (`allowMajorUpdates=false`). |
| `plugins_desatualizados` | Nº de plugins **únicos** (`groupId:artifactId`) com versão mais nova em **qualquer** bloco de atualização: o bloco "plugin updates are available" **e** os blocos "Require Maven X.Y.Z to use...". Cada plugin conta só uma vez, e só entram as linhas em que a versão nova é **maior** que a atual (os blocos "Require Maven" também listam versões anteriores). Plugins sem `<version>` no `pom.xml`, com a versão vinda do parent, podem não aparecer no relatório. |
| `parent_atual` | Versão atual do parent (`spring-boot-starter-parent`). |
| `parent_mais_recente` | Versão estável mais recente do parent disponível (qualquer major). |
| `parent_mais_recente_mesma_major` | Versão estável mais recente do parent **dentro da mesma major**. |
| `arvore_limpa` | `sim` se `git status` ficou vazio depois da medição; `nao` caso contrário. |

## Observações

- Histórico de versões do CSV (o cabeçalho/definições mudaram ao longo do trabalho):
  - **`medicoes-v1.csv`** — antes das colunas `*_mesma_major`.
  - **`medicoes-v2.csv`** — quando `plugins_desatualizados` contava só o bloco
    "The following plugin updates are available".
  - **`medicoes-v3.csv`** — antes da correção das entradas quebradas em duas linhas (abaixo).
  - **`medicoes-v4.csv`** — antes da correção dos plugins: os blocos "Require Maven" também
    listam versões **anteriores** à usada (ex.: `jacoco 0.8.16 -> 0.8.2`), e o script contava
    essas linhas como atualização.
  - **`medicoes.csv`** (atual) — `plugins_desatualizados` conta plugins únicos de
    **qualquer** bloco (inclusive os "Require Maven X.Y.Z to use..."), e as contagens de
    dependências e plugins juntam as entradas quebradas em duas linhas, e os plugins só contam
    quando a versão nova é maior que a atual. A errata das duas correções está em `ERRATA.md`,
    na raiz do kit.
- Quando o `grupo:artefato` é longo, o `versions-maven-plugin` escreve o nome numa linha e as
  versões (`atual -> nova`) na seguinte. Até a versão do `medicoes-v3.csv`, o script só contava
  as linhas com o nome e a seta juntos e deixava essas entradas de fora. Agora ele junta as duas
  linhas antes de contar. As três medições (legado, openrewrite e final) foram recalculadas a
  partir das saídas brutas guardadas, sem rodar os builds de novo; os valores antigos e os
  corrigidos estão em `correcao-contagem-dependencias.csv`.
- A coluna `plugins_desatualizados` considera todos os blocos porque a modernização pode
  mudar a versão do Maven exigida pelo projeto; contar só o primeiro bloco deixaria as
  fases (legado × openrewrite × final) difíceis de comparar.
- A versão do `versions-maven-plugin` está fixa em **2.16.2** no script: é a última linha
  que roda com **Java 8** e também funciona com **Java 21** e **Maven 3.6.3**.
- O filtro de pré-releases é aplicado via `-Dmaven.version.ignore` com expressões regulares.
- O script **nunca** edita o `pom.xml`: plugins ausentes são chamados pela coordenada completa
  (`grupo:artefato:versão:goal`).

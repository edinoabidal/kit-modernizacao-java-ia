# Kit de modernização Java com OpenRewrite e agente de IA

Kit do TCC "Uso de IA generativa na modernização de aplicações Java legadas". Reúne o que é preciso
para repetir o processo híbrido usado na migração do Spring PetClinic REST (commit `517a399`) de
Java 8 e Spring Boot 2.6 para Java 21 e Spring Boot 3.5: a receita do OpenRewrite, as regras do
agente de IA, os prompts, os testes de caracterização, o script de medição e as evidências de cada fase.

Licença: Apache 2.0 (`LICENSE`), a mesma do PetClinic.

## Estrutura

| Pasta ou arquivo | Conteúdo |
|---|---|
| `receita/` | `rewrite.yml` (receita composta `tcc.ModernizacaoPetClinic`) e `analise-dependencias.md` |
| `steering/modernizacao.md` | Regras seguidas pelo agente na F4 |
| `prompts/` | Prompts das fases F2, F3 e F4 |
| `testes-caracterizacao/` | Projeto Maven com os 8 testes REST Assured da API (ver `README-testes.md`) |
| `scripts/` | `medir.py` e `README-medir.md` |
| `medicoes/` | `medicoes.csv`, `mudancas-por-fase.csv` e a correção das contagens |
| `evidencias/` | Logs e relatórios de F1 a F5 e dos testes T01 a T08 |
| `ERRATA.md` | Correções das contagens de dependências e plugins |

Os dados do ambiente foram mascarados nos arquivos de evidência: usuário (`<usuario>`), máquina
(`<host>`), autor dos commits na sessão (`<autor>`, `<email>`) e senhas geradas pela aplicação
(`<removida>`).

## Pré-requisitos

- Git e Python 3 (só a biblioteca padrão).
- JDK 8 e JDK 21 (Eclipse Temurin). Os comandos usam o JDK só pela variável `JAVA_HOME` de cada
  comando, sem mudar o sistema.
- O Maven vem pelo Maven Wrapper (`mvnw`) de cada projeto.

Os exemplos abaixo usam Bash (Linux, macOS ou WSL) e supõem esta organização, com o kit e o projeto
lado a lado:

```
pasta-de-trabalho/
├── kit/                     (este repositório)
├── spring-petclinic-rest/   (o projeto a modernizar)
└── medicoes/                (criada pelo medir.py)
```

Defina antes os dois JDKs:

```bash
JDK8=/caminho/do/jdk8
JDK21=/caminho/do/jdk21
```

No Windows sem WSL, troque `./mvnw` por `mvnw.cmd`, defina o JDK com `set JAVA_HOME=...` antes de
cada comando e use `python` no lugar de `python3`.

## Como repetir o processo

Todos os comandos partem da `pasta-de-trabalho`.

### F1: linha de base

```bash
git clone https://github.com/spring-petclinic/spring-petclinic-rest.git
cd spring-petclinic-rest
git switch -c legado 517a399
git switch -c modernizacao
cd ..
python3 kit/scripts/medir.py --projeto spring-petclinic-rest --fase legado --java-home "$JDK8"
```

### F2: rede de proteção

Suba a versão legada e rode a suíte de caracterização contra ela (detalhes em
`testes-caracterizacao/README-testes.md`):

```bash
(cd spring-petclinic-rest && JAVA_HOME="$JDK8" ./mvnw -B clean package -DskipTests \
  && JAVA_HOME="$JDK8" "$JDK8/bin/java" -jar target/spring-petclinic-rest-2.6.2.jar) &
# espere a aplicação subir na porta 9966
(cd kit/testes-caracterizacao && JAVA_HOME="$JDK21" ./mvnw -B clean test)
```

Pare a aplicação no fim. A suíte precisa passar 100% antes da migração.

### F3: OpenRewrite

No `spring-petclinic-rest`, branch `modernizacao`, rode primeiro o `dryRun`, revise o
`target/rewrite/rewrite.patch` e depois troque `dryRun` por `run`:

```bash
cd spring-petclinic-rest
JAVA_HOME="$JDK21" ./mvnw -B -U org.openrewrite.maven:rewrite-maven-plugin:6.46.1:dryRun \
  -Drewrite.recipeArtifactCoordinates=org.openrewrite.recipe:rewrite-spring:6.37.0,org.openrewrite.recipe:rewrite-migrate-java:3.42.0 \
  -Drewrite.configLocation="$(cd ../kit/receita && pwd)/rewrite.yml" \
  -Drewrite.activeRecipes=tcc.ModernizacaoPetClinic \
  -Drewrite.exportDatatables=false
```

O `rewrite.configLocation` precisa de um caminho absoluto; o `$(cd ../kit/receita && pwd)` monta esse
caminho a partir da pasta de trabalho. Depois do `run`, faça o commit da fase e meça a referência
"só OpenRewrite":

```bash
cd ..
python3 kit/scripts/medir.py --projeto spring-petclinic-rest --fase openrewrite --java-home "$JDK21"
```

### F4: agente de IA

Copie `steering/modernizacao.md` para `spring-petclinic-rest/.kiro/steering/` (ou para a pasta de
regras do agente usado) e use o prompt `prompts/F4-agente.md`. O agente trabalha com o JDK 21 e faz um
único commit no fim. As pendências que ele registrar seguem para a F5.

### F5: ajuste dirigido pelo autor

Só para o que a receita e o agente não resolveram dentro das regras. Cada exceção às regras do
steering é decidida e registrada pelo autor (exemplo: `evidencias/F5/relatorio.md`).

### F6: validação e medição

Suba a versão modernizada com o JDK 21, rode a suíte de caracterização como na F2 e meça:

```bash
python3 kit/scripts/medir.py --projeto spring-petclinic-rest --fase final --java-home "$JDK21"
```

A contagem de arquivos e linhas por fase usa `evidencias/T08/contar-mudancas.py`. Os commits estão
fixados no script; troque-os pelos commits das suas fases:

```bash
python3 kit/evidencias/T08/contar-mudancas.py spring-petclinic-rest medicoes/mudancas-por-fase.csv
```

## Para usar em outro projeto

- `testes-caracterizacao/` é específico da API do PetClinic: crie testes equivalentes para a API do
  seu projeto, executados contra a versão legada antes de qualquer alteração.
- `receita/rewrite.yml` serve de modelo; escolha no catálogo do OpenRewrite as receitas da sua
  migração e justifique a ordem.
- `steering/modernizacao.md` traz regras gerais (não mudar regras de negócio, manter o contrato da
  API, parar e registrar quando só for possível resolver quebrando uma regra). Ajuste os detalhes do
  projeto, como porta, rotas e versões.
- `medir.py` funciona com qualquer projeto Maven com Maven Wrapper, JaCoCo e Surefire.

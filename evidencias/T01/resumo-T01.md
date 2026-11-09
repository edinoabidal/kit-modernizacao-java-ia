# Resumo T01 — Preparação e registro da versão LEGADA (Spring PetClinic REST)

## Metadados

- **Data e hora:** 2026-10-27 17:07 (America/Sao_Paulo, UTC-03)
- **Sistema operacional:** Ubuntu 22.04.5 LTS sobre WSL2 (kernel `6.18.54.1-microsoft-standard-WSL2`), host Windows
- **Terminal/shell:** `/bin/bash`
- **Git:** `git version 2.34.1`
- **Versão do Java (compilar e rodar):** Eclipse Temurin **JDK 1.8.0_504** (`OpenJDK 64-Bit Server VM, build 25.504-b01`)
  - `JAVA_HOME=C:/Users/<usuario>/java/jdk8u-linux-x64` (build Linux x64, ajustado **apenas na sessão** do terminal)
- **Maven usado pelo wrapper:** Apache **Maven 3.6.3** (via `./mvnw`, distribuição baixada automaticamente pelo wrapper)
- **Projeto:** https://github.com/spring-petclinic/spring-petclinic-rest.git
- **Branch:** `legado`
- **Commit:** `517a399 Bump to Spring Boot 2.6.2 #63`

## Onde o trabalho foi executado (importante)

- O build/execução foram feitos no **filesystem Linux do WSL**: `/home/<usuario>/tcc-modernizacao/`
  (o projeto está em `.../spring-petclinic-rest` e as evidências em `.../evidencias/T01`).
- **Motivo:** uma primeira tentativa em `C:\tcc-modernizacao` (`/mnt/c/...`) falhou pela lentidão de I/O do
  filesystem Windows via WSL — o fork do Maven Surefire "crashou" (`The forked VM terminated without properly
  saying goodbye`) mesmo com todos os testes passando. No Linux o mesmo build conclui com sucesso em ~42s.
- O conteúdo foi **copiado para `C:\tcc-modernizacao`** ao final, para uso na máquina Windows.
- **Nenhum arquivo versionado do projeto foi alterado** em nenhum momento (sem mudar pom.xml, código,
  configs ou o Maven Wrapper; sem atualizar dependências; sem OpenRewrite; sem commit/push).

## JDK 8

Não havia JDK 8 instalado (apenas JDK 11 e JDK 21 no Linux; no Windows havia só um JRE 8, sem `javac`).
Com autorização, foi baixado o **Eclipse Temurin 8u504-b01 (Linux x64)**, checksum SHA-256 verificado (OK),
e extraído em `C:\Users\<usuario>\java\jdk8u-linux-x64` (= `C:/Users/<usuario>/java/jdk8u-linux-x64`),
junto aos demais JDKs. Saída de `java -version` salva em `java-version.txt`.

## Comandos executados (essência)

```bash
# JAVA_HOME só na sessão
export JAVA_HOME=C:/Users/<usuario>/java/jdk8u-linux-x64
export PATH="$JAVA_HOME/bin:$PATH"

# Passo 2 — clone + branch legado
git clone https://github.com/spring-petclinic/spring-petclinic-rest.git
cd spring-petclinic-rest
git checkout -b legado 517a399
git log -1 --oneline            # 517a399 Bump to Spring Boot 2.6.2 #63

# Passo 3 — evidências
mkdir -p ../evidencias/T01
java -version > ../evidencias/T01/java-version.txt 2>&1

# Passo 4 — build + testes + cobertura (JDK 8)
./mvnw -B clean verify > ../evidencias/T01/build-legado.log 2>&1

# Passo 5 — subir a aplicação (JDK 8, em segundo plano)
java -jar target/spring-petclinic-rest-2.6.2.jar > ../evidencias/T01/app-run.log 2>&1 &

# Passo 6 — testar rotas
curl http://localhost:9966/petclinic/actuator/health
curl http://localhost:9966/petclinic/api/owners
curl http://localhost:9966/petclinic/api/vets
curl http://localhost:9966/petclinic/api/pettypes

# Passo 7 — parar app e liberar a porta 9966
# Passo 8 — git status --porcelain (limpo)
```

## Resultado do build e dos testes (Passo 4)

- **Resultado do build:** `BUILD SUCCESS` (tempo total: 42,3 s)
- **Testes:** `Tests run: 171, Failures: 0, Errors: 0, Skipped: 0`
  - Executados: **171** | Falhas: **0** | Erros: **0** | Ignorados: **0**
- **JaCoCo — verificação de cobertura do projeto (`jacoco:check`):** **PASSOU**
- Log completo: `build-legado.log`

## Cobertura (relatório JaCoCo em `target/site/jacoco`)

| Métrica | Cobertas | Total | Cobertura |
|---|---|---|---|
| **Linhas** | 1274 | 1441 | **88,41%** |
| **Ramos (branches)** | 270 | 380 | **71,05%** |

(valores agregados a partir de `target/site/jacoco/jacoco.csv`)

## Rotas testadas (Passo 6)

Base: `http://localhost:9966/petclinic`

| Rota | HTTP | Registros devolvidos | Arquivo |
|---|---|---|---|
| `/actuator/health` | **200** | `{"status":"UP"}` | `health.json` |
| `/api/owners` | **200** | 10 (owners de topo) | `owners.json` |
| `/api/vets` | **200** | 6 | `vets.json` |
| `/api/pettypes` | **200** | 6 | `pettypes.json` |

Aplicação subiu em ~10 s; `/actuator/health` respondeu `UP` (HTTP 200) dentro do limite de 3 min.

## Encerramento e porta (Passo 7)

- Aplicação encerrada; **porta 9966 confirmada LIVRE** após o shutdown
  (health passou a não responder — HTTP 000).

## git status (Passo 8)

- `git status --porcelain` → **vazio** (nenhum arquivo versionado modificado).
- Branch `legado` no commit `517a399`.
- O diretório `target/` (jar + relatório JaCoCo) é ignorado pelo `.gitignore` e não aparece no status.

## Arquivos de evidência em `evidencias/T01`

- `java-version.txt` — saída de `java -version` do JDK 8
- `build-legado.log` — log completo do `mvnw clean verify`
- `app-run.log` — log de inicialização da aplicação
- `health.json`, `owners.json`, `vets.json`, `pettypes.json` — respostas das rotas
- `resumo-T01.md` — este documento

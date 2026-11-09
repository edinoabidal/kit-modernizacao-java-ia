# T06: suíte de caracterização contra a versão modernizada

- Data: 2026-11-09, das 11:34 às 11:36
- Projeto: `spring-petclinic-rest`, branch `modernizacao`, commit `7c0326d` (commit 3), árvore limpa
- JDK: Temurin 21.0.13, só no `JAVA_HOME` dos comandos
- Nenhum código foi alterado.

## Como foi rodado

Como no T02:

1. Aplicação recém-iniciada com `java -jar target/spring-petclinic-rest-2.6.2.jar`, com a segurança
   desligada (padrão). O JAR é o do `clean verify` da F5, feito com o mesmo código do commit 3.
   Log em `app-modernizada.log`: `Tomcat started on port 9966 (http) with context path '/petclinic'`.
2. Em `kit/testes-caracterizacao`: `./mvnw -B clean test`. Log em `testes-caracterizacao.log` e
   relatórios em `surefire-reports/`.
3. Verificação da documentação com `curl`, registrada em `verificacao-swagger.txt`.
4. A aplicação foi parada com `SIGTERM` no fim (`Graceful shutdown complete` no log), e a porta
   9966 ficou livre.

## Resultado

| Verificação | Resultado |
|---|---|
| Suíte de caracterização (TC01 a TC08) | `Tests run: 8, Failures: 0, Errors: 0, Skipped: 0`, `BUILD SUCCESS` |
| `GET /petclinic/actuator/health` | 200, `{"status":"UP"}` |
| `GET /petclinic/v3/api-docs` | 200, `application/json`, OpenAPI 3.1.0, 16 caminhos, `info` com título, descrição, versão 1.0, contato e licença Apache 2.0 do `ApplicationSwaggerConfig` (cópia em `api-docs.json`) |
| `GET /petclinic/swagger-ui.html` | 302 para `/petclinic/swagger-ui/index.html`, que devolve 200, `text/html`, com o título "Swagger UI" (cópia em `swagger-ui.html`) |
| `GET /petclinic/v3/api-docs/swagger-config` | 200, aponta a interface para `/petclinic/v3/api-docs` |

Os testes do projeto (171) entram pelo T07, que roda o `mvnw verify`.

# F4: agente de IA (Kiro com steering), relatório

- Projeto: `spring-petclinic-rest`, branch `modernizacao`, a partir do commit 1 (`d0d758d`, F3).
- Regras seguidas: `.kiro/steering/modernizacao.md` (copiado para `kit/steering/modernizacao.md`).
- JDK: Temurin 21.0.13, só no `JAVA_HOME` dos comandos (o mesmo JDK do T05). Maven 3.6.3 (wrapper).
- Início: 2026-11-09 10:31:00 -03. Fim: 2026-11-09 10:51:23 -03 (antes do commit).
- Logs desta fase: `evidencias/F4/logs/`, `evidencias/F4/testes-caracterizacao.log`,
  `evidencias/F4/surefire-caracterizacao/`, `evidencias/F4/app-*.log`. A sessão do Kiro foi salva
  em `evidencias/F4/sessao-f4.json`. Os dados do ambiente estão mascarados como nos outros arquivos
  do kit: o usuário virou `<usuario>`, e o nome da máquina, `<host>`. Na sessão, o nome e o e-mail
  do autor dos commits viraram `<autor>` e `<email>`.

## Pré-condições conferidas

| Item | Resultado |
|---|---|
| `modernizacao` com o commit 1 (`d0d758d`) e árvore limpa | sim |
| T05 medido, com erros agrupados por causa (`evidencias/T05/erros-compilacao-por-causa.md`) | sim |
| Kit com os commits da F2 (`015ecaf`) e da F3 (`ba74bc0`), árvore limpa | sim |

## Resultado final

| Objetivo | Resultado |
|---|---|
| `./mvnw clean verify` passa, com todos os testes aprovados | **Não.** 171 testes, 169 aprovados, 2 com erro (pendência P1, encaminhada para a F5). O JaCoCo também ficaria abaixo do mínimo de ramos (69,25%, mínimo 70%) por causa desses 2 testes |
| A aplicação sobe na porta 9966, em `/petclinic` | **Sim.** `Tomcat started on port 9966 (http) with context path '/petclinic'`; `/actuator/health` devolve `{"status":"UP"}` |
| Suíte de caracterização passa 100% contra a versão modernizada | **Sim.** `Tests run: 8, Failures: 0, Errors: 0, Skipped: 0`, `BUILD SUCCESS` |

A suíte foi rodada como no T02: aplicação recém-iniciada com `java -jar target/spring-petclinic-rest-2.6.2.jar`
(segurança desligada, padrão) e `./mvnw -B clean test` em `kit/testes-caracterizacao`, com o JDK 21.

## Mudanças por causa

### Causas A, B e C do T05: DTOs gerados com Swagger 2 e `javax.*` (98 erros)

Origem comum: o `openapi-generator-maven-plugin` 5.2.1 gera os DTOs com `io.swagger.annotations`,
`javax.validation` e `javax.annotation.Generated`.

- `pom.xml`: plugin de 5.2.1 para **7.27.0** e opção `useSpringBoot3=true` (gera `jakarta.*` e as
  anotações `io.swagger.v3.oas.annotations` do springdoc).
- `src/main/openapi-templates/notNull.mustache` (novo) e `templateDirectory` no `pom.xml`: ver a decisão D2.

Depois da troca, a rodada 1 ficou só com os 2 erros da causa D. Os DTOs gerados continuam com os
mesmos campos, os mesmos nomes JSON e as mesmas regras de validação da 5.2.1 (comparação na decisão D2).

### Causa D do T05: Springfox no `ApplicationSwaggerConfig` (2 erros)

- `src/main/java/org/springframework/samples/petclinic/util/ApplicationSwaggerConfig.java`: tirei o
  `BeanPostProcessor` de contorno do Springfox para o Boot 2.6 e os imports do Springfox. Recriei
  título, descrição, versão, termos de uso, contato e licença do antigo `ApiInfo` num bean
  `OpenAPI` do springdoc. O `@Configuration` e o `@ComponentScan` ficaram como estavam.
- `pom.xml`: removida a propriedade `springfox-swagger.version`, que não era mais usada.

Conferido com a aplicação rodando: `/v3/api-docs` devolve o `info` com os mesmos textos do legado e 16 caminhos;
`/swagger-ui.html` redireciona (302) para `/swagger-ui/index.html`, que devolve 200.

### Causa E (nova, apareceu nos testes): barra no fim da URL

O Spring Framework 6 deixou de tratar `/api/owners/` como `/api/owners`. A requisição caía no
`ExceptionControllerAdvice` (`NoResourceFoundException`) e voltava 400. Na rodada 3 isso derrubou
22 testes dos controllers, que usam URLs com barra no fim (`get("/api/owners/")`, `post("/api/pets/")`).

- `src/main/java/org/springframework/samples/petclinic/util/TrailingSlashMatchConfig.java` (novo):
  `WebMvcConfigurer` com `setUseTrailingSlashMatch(true)`, o comportamento do Spring 5.
- Testes dos controllers: ver "Testes do projeto que mudaram".

Conferido com a aplicação rodando: `GET /petclinic/api/owners/` devolve 200.

### Causa F (nova, apareceu nos testes): HQL com nome de coluna

O Hibernate 6 não aceita mais nome de coluna dentro de HQL (`Could not interpret path expression 'pet_id'`
e `'type_id'`). Isso causou 4 erros: `shouldDeletePet` e `shouldDeletePetType` nos perfis `jpa` e `spring-data-jpa`.

- `repository/jpa/JpaPetRepositoryImpl.java` e `repository/springdatajpa/SpringDataPetRepositoryImpl.java`:
  `DELETE FROM Visit visit WHERE pet_id=` passou a `... WHERE visit.pet.id=`.
- `repository/jpa/JpaPetTypeRepositoryImpl.java` e `repository/springdatajpa/SpringDataPetTypeRepositoryImpl.java`:
  `SELECT pet FROM Pet pet WHERE type_id=` passou a `... WHERE pet.type.id=`.

`visit.pet` está mapeado com `@JoinColumn(name = "pet_id")` e `pet.type` com `@JoinColumn(name = "type_id")`,
então o filtro é o mesmo. O Hibernate 6 traduz `x.assoc.id` direto para a coluna da chave estrangeira,
sem join. Ver a decisão D4. Os dois testes `shouldDeletePet` passaram. Os dois `shouldDeletePetType`
passaram a falhar mais adiante, pela causa G.

### Causa G (nova, sem solução): exclusão de tipo de pet no Hibernate 6.6

Pendência P1, descrita na seção de pendências.

## Testes do projeto que mudaram

Só uma mudança, nos 7 testes de controller. Nenhuma asserção, valor esperado ou teste foi alterado,
apagado ou desativado.

| Arquivo (`src/test/java/org/springframework/samples/petclinic/rest/`) | Mudança | Motivo |
|---|---|---|
| `OwnerRestControllerTests.java`, `PetRestControllerTests.java`, `PetTypeRestControllerTests.java`, `SpecialtyRestControllerTests.java`, `UserRestControllerTests.java`, `VetRestControllerTests.java`, `VisitRestControllerTests.java` | `.setUseTrailingSlashPatternMatch(true)` no `MockMvcBuilders.standaloneSetup(...)` | Os testes montam o MockMvc em modo standalone, sem o contexto web da aplicação, então o `TrailingSlashMatchConfig` não vale ali. No Spring 5 a barra no fim era aceita por padrão. No Spring 6 é preciso ligar no builder. A mudança é mecânica e não muda o que os testes verificam |

As mudanças de estilo que a F3 fez nos testes (`getFirst()` e `removeFirst()`) ficaram como estavam,
como foi pedido. Não houve correção de nada que a F3 fez.

## Dependências e plugins trocados

| Item | Antes (F3) | Depois (F4) | Onde confirmei |
|---|---|---|---|
| `org.openapitools:openapi-generator-maven-plugin` | 5.2.1 | 7.27.0 | Maven Central: `repo1.maven.org/maven2/org/openapitools/openapi-generator-maven-plugin/maven-metadata.xml` (`<release>7.27.0</release>`) e o POM da 7.27.0 (HTTP 200). O Spring Boot não gerencia esse plugin |
| Propriedade `springfox-swagger.version` | 3.0.0 | removida | Não era usada no `pom.xml` |

Mantidos sem troca, com o motivo:

| Item | Versão | Motivo |
|---|---|---|
| `org.springdoc:springdoc-openapi-starter-webmvc-ui` | 2.8.17 (da F3) | Existe no Central (POM da 2.8.17, HTTP 200) e é a mais recente da linha 2.8, a do Boot 3.4/3.5. Traz `swagger-annotations-jakarta` e `swagger-models-jakarta` 2.2.47, usados pelos DTOs e pelo `ApplicationSwaggerConfig` |
| `org.springframework.data:spring-data-jdbc-core` | 1.2.1.RELEASE | É a última versão no Central (`<release>1.2.1.RELEASE</release>`, publicada em 2015). Funciona com o Spring 6: os 33 testes de `ClinicServiceJdbcTests` e o `UserServiceJdbcTests` passam. A análise da F3 previa um conflito de classes, que não aconteceu |
| `org.openapitools:jackson-databind-nullable` | 0.2.1 | Com `openApiNullable=false`, os DTOs gerados não usam a biblioteca, e nada quebrou. Existe a 0.2.13 no Central, mas trocar não é necessário |
| `jib-maven-plugin` | 1.3.0 | Não participa do build nem dos testes |

## Decisões

**D1. Versão do gerador: 7.27.0.** É a mais recente no Central e tem `useSpringBoot3`. Testei também
6.6.0, 7.0.0, 7.5.0, 7.10.0 e 7.20.0 só gerando os DTOs. Nenhuma devolvia o `@NotNull` dos campos
`readOnly` (ver D2), então não havia motivo para ficar numa versão mais antiga.

**D2. Template `notNull.mustache` para manter a validação da 5.2.1.** Comparei os DTOs da 5.2.1 com os
da 7.27.0. Desde a 6.x, o gerador não põe `@NotNull` em propriedade obrigatória marcada `readOnly`.
No `api-docs.yml`, isso atinge o `id` de Pet, PetType, Specialty, Vet e Visit e as listas `pets`
e `visits`. Na versão legada, um `POST /api/pettypes` sem `id`, por exemplo, devolve 400 pela
validação. Com a 7.27.0 sem ajuste, passaria a ser aceito, o que muda uma regra da API (regras 1 e 2).
A alternativa menor foi sobrescrever um único template do gerador
(`src/main/openapi-templates/notNull.mustache`, uma linha) com a regra da 5.2.1: `@NotNull` em toda
propriedade obrigatória. Depois disso, as anotações de validação de todos os DTOs ficaram iguais às
da 5.2.1. As únicas diferenças são de forma: `@Valid` passou de anotação no getter para anotação de
tipo (`List<@Valid PetDto>`), com o mesmo efeito de validação em cascata. Conferido com a aplicação
rodando: `POST /api/pettypes` com `{"name":"x"}` devolve 400.
Outras diferenças na saída da 7.27.0 que não afetam a API:
- `OwnerAllOfDto`, `PetAllOfDto` e `VisitAllOfDto` não são mais gerados. Nenhum código os usava.
- `ValidationMessageDto` deixou de estender `HashMap`. Nenhum código o usava.
- `UserDto.roles` começa como lista vazia, não mais `null`. O `UserServiceImpl` trata os dois casos
  igual: lança a exceção "User must have at least a role set!". Testei `containerDefaultToNull=true`
  para voltar ao `null`, mas a opção também tirava o `new ArrayList<>()` das listas obrigatórias
  (`pets`, `visits`, `specialties`), que a 5.2.1 inicializava. Por isso desfiz.
- Foi incluído `@DateTimeFormat` nas datas. Isso só vale para parâmetros de URL e não muda o JSON.

**D3. Barra no fim da URL com `setUseTrailingSlashMatch(true)`.** O método está marcado como obsoleto
no Spring 6, mas existe no 6.2 e devolve exatamente o comportamento do Spring 5 para todas as rotas.
A alternativa do Spring 6.2, o `UrlHandlerFilter`, é um filtro de servlet: não vale nos testes
standalone e mexe na ordem dos filtros de segurança. Mantive também
`spring.mvc.pathmatch.matching-strategy=ant_path_matcher`, que a F3 deixou. Trocar de estratégia de
rotas poderia mudar o casamento de rotas como `/owners/*/lastname/{lastName}`.

**D4. HQL com nome de coluna.** A regra 1 diz para não alterar consultas e também para mudar o
necessário para rodar nas versões novas. Tratei a troca de `pet_id` por `visit.pet.id` e de `type_id`
por `pet.type.id` como adaptação de sintaxe exigida pelo Hibernate 6: o filtro e o resultado são os
mesmos, e nada mais mudou nesses métodos. **Aprovada pelo autor do TCC depois da F4**: é uma
mudança de sintaxe exigida pelo Hibernate 6, com o mesmo filtro, e a regra 1 permite o que é
necessário para rodar nas versões novas.

**D5. Springdoc.** O endereço da especificação gerada mudou de `/v2/api-docs` (Springfox, Swagger 2)
para `/v3/api-docs` (springdoc, OpenAPI 3), como a regra 4 permite. A interface continua em
`/petclinic/swagger-ui.html`, que agora redireciona para `/petclinic/swagger-ui/index.html`. As
propriedades `springdoc.*` foram incluídas pela F3 e ficaram como estavam.

**D6. Segurança.** Não mudei os arquivos de segurança da F3. Conferi o comportamento com a aplicação
rodando com `--petclinic.security.enable=true`:
- sem login: 401;
- `admin:admin`: 200;
- senha errada: 401;
- um usuário criado só com `OWNER_ADMIN` lê `/api/owners` (200);
- o mesmo usuário recebe 400 em `/api/vets` e em `POST /api/users`.
O 400 vem do `@PreAuthorize` negado e tratado pelo `ExceptionControllerAdvice`, que transforma toda
exceção em 400. Com a segurança desligada, a API continua aberta (a suíte de caracterização passou sem login).
Observação, não verificada contra o legado em execução: no corpo do 400 por permissão negada, o
`className` passa a ser `org.springframework.security.authorization.AuthorizationDeniedException`.
Ela é subclasse da `AccessDeniedException` que o Spring Security 5 lançava. O status e o formato do
corpo são os mesmos.

**D7. O que ficou como estava.** Os avisos de obsolescência (`@MockBean` nos testes, `HSQLDialect`
explícito nas propriedades, `java8` no gerador) não impedem compilar nem rodar. A regra 6 e o escopo
da fase não permitem mudar isso aqui.

## Pendências

**P1. `shouldDeletePetType` falha nos perfis `jpa` e `spring-data-jpa` (2 testes), e `DELETE /api/pettypes/{id}` devolve 400.**

- Erro: `org.hibernate.TransientObjectException: persistent instance references an unsaved transient
  instance of 'org.springframework.samples.petclinic.model.PetType'`, no auto-flush antes dos
  `executeUpdate()` de `JpaPetTypeRepositoryImpl.delete` e `SpringDataPetTypeRepositoryImpl.delete`.
- Causa: esses métodos primeiro fazem `em.remove(petType)`. Depois carregam os pets desse tipo e os
  apagam com `DELETE` em lote. Os pets continuam gerenciados e apontando para o tipo removido. O
  Hibernate 6.6 (6.6.53, gerenciado pelo Boot 3.5.16) recusa esse flush. O Hibernate 5 do legado aceitava.
- Tentativas:
  1. Procurei uma configuração do Hibernate que desligasse a checagem e não encontrei.
  2. Movi o `em.remove(petType)` para o fim do método, como teste, e desfiz depois. O erro continua,
     porque os pets apagados em lote continuam gerenciados.
  3. Avaliei e descartei, sem aplicar, dois contornos. Mudar o flush mode global para `COMMIT` mudaria
     o comportamento de toda a aplicação e só adiaria o erro para o commit. Rebaixar o Hibernate para
     uma versão fora da gerenciada pelo Boot 3.5 iria contra a regra 7.
- O que resolveria: mudar a lógica dos dois repositórios, por exemplo removendo pets e visitas pelo
  `EntityManager` ou desanexando-os antes do flush. Isso quebra a regra 1 ("não altere ... a lógica de
  serviços e repositórios"), então parei e deixei registrado, como pede a regra 11.
- Efeito no build: com esses 2 testes falhando, o `verify` para no Surefire. A rodada de diagnóstico
  mostrou que o `jacoco:check` também falharia: ramos com 69,25% (259 de 374), mínimo de 70%. A
  diferença está toda nos ramos não exercitados de `JpaPetTypeRepositoryImpl` e
  `SpringDataPetTypeRepositoryImpl`. No legado eram 71,05%. Linhas: 87,73%, mínimo de 87%.
- Efeito na API: com a segurança desligada, `DELETE /petclinic/api/pettypes/6` devolveu 400 com
  `{"className":"org.springframework.dao.InvalidDataAccessApiUsageException", ...}`. A suíte de
  caracterização não cobre essa rota. `DELETE /api/pets/{id}` funciona (204).
- Decisão do autor do TCC, depois da F4: nada foi alterado nesta fase. A pendência foi
  **encaminhada para a F5**, o ajuste manual feito pelo autor.

**P2. Confirmar a decisão D4** (HQL com caminho de entidade no lugar do nome de coluna).
**Resolvida:** o autor do TCC aprovou a decisão D4 depois da F4. Nada mudou no código.

## Rodadas de build

Todas com o JDK 21, em `spring-petclinic-rest`. Logs em `evidencias/F4/logs/`.

| Rodada | Fim (log do Maven) | Comando | Depois de | Resultado |
|---|---|---|---|---|
| 0 (T05) | 10:07:26 | `clean verify` (medir.py) | F3 | 100 erros de compilação (truncado pelo javac) |
| 1 | 10:33:36 | `clean compile` | Gerador 7.27.0 (causas A, B, C) | 2 erros de compilação (causa D) |
| 2 | 10:39:43 | `clean test-compile` | Template `notNull` e `ApplicationSwaggerConfig` (causa D) | 0 erros; produção e testes compilam |
| 3 | 10:40:14 | `clean verify` | (nada; primeira execução dos testes) | 171 testes: 22 falhas e 4 erros (causas E e F) |
| 4 | 10:42:45 | `clean verify` | Barra no fim da URL (causa E) | 171 testes: 0 falhas e 4 erros (causa F) |
| 5 | 10:43:29 | `clean verify` | HQL (causa F) | 171 testes: 0 falhas e 2 erros (causa G) |
| 6 | 10:45:53 | `test -Dtest=ClinicServiceJpaTests` | Tentativa 2 da P1, desfeita depois | 33 testes: 1 erro (o mesmo) |
| 7 | 10:47:02 | `clean verify -Dmaven.test.failure.ignore=true` | (diagnóstico) | 2 erros; `jacoco:check` falha com ramos em 0,69 |
| 8 | 10:50:31 | `clean verify` | Remoção de `springfox-swagger.version` | 171 testes: 0 falhas e 2 erros (P1); `BUILD FAILURE` |

Ao todo foram 8 rodadas nesta fase: 7 com o projeto inteiro e 1 com uma só classe de teste. Também
houve execuções que só geraram os DTOs (`generate-sources`), para comparar versões do gerador. Elas
não compilam o projeto e ficaram fora da contagem. O `medir.py` não foi executado.

## Resultado do `mvnw verify` (rodada 8)

```
[ERROR]   ClinicServiceJpaTests>AbstractClinicServiceTests.shouldDeletePetType:402 » InvalidDataAccessApiUsage org.hibernate.TransientObjectException: ...
[ERROR]   ClinicServiceSpringDataJpaTests>AbstractClinicServiceTests.shouldDeletePetType:402 » InvalidDataAccessApiUsage org.hibernate.TransientObjectException: ...
[ERROR] Tests run: 171, Failures: 0, Errors: 2, Skipped: 0
[INFO] BUILD FAILURE
```

Os 2 erros são da pendência P1, encaminhada para a F5.

## Resultado da suíte de caracterização

```
[INFO] Tests run: 8, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 2.824 s -- in br.tcc.modernizacao.caracterizacao.ApiPetClinicCaracterizacaoTest
[INFO] Tests run: 8, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```

TC01 a TC08 passaram, inclusive o TC08: 400, corpo vazio e o erro no cabeçalho `errors`.

## Arquivos alterados no commit 2

- `pom.xml`
- `src/main/openapi-templates/notNull.mustache` (novo)
- `src/main/java/org/springframework/samples/petclinic/util/ApplicationSwaggerConfig.java`
- `src/main/java/org/springframework/samples/petclinic/util/TrailingSlashMatchConfig.java` (novo)
- `src/main/java/org/springframework/samples/petclinic/repository/jpa/JpaPetRepositoryImpl.java`
- `src/main/java/org/springframework/samples/petclinic/repository/jpa/JpaPetTypeRepositoryImpl.java`
- `src/main/java/org/springframework/samples/petclinic/repository/springdatajpa/SpringDataPetRepositoryImpl.java`
- `src/main/java/org/springframework/samples/petclinic/repository/springdatajpa/SpringDataPetTypeRepositoryImpl.java`
- Os 7 `*RestControllerTests.java` listados acima

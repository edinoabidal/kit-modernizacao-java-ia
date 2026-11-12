# Análise de dependências — F3

Versão analisada: Spring PetClinic REST, branch `legado`, commit `517a399`
(Spring Boot 2.6.2, Java 8). Alvo: Java 21 e Spring Boot 3.5.

Fontes usadas:
- o `pom.xml` do legado;
- a árvore de dependências gerada com o JDK 8
  (`mvnw dependency:tree`, salva em `evidencias/F3/dependency-tree-legado.txt`);
- a linha de base F1 (`medicoes/medicoes.csv`): 24 dependências declaradas, 23 entradas desatualizadas
  (22 dependências e o `spring-boot-maven-plugin` do `pluginManagement`; valor corrigido pela
  `ERRATA.md`, a contagem original do script era 18), 4 plugins desatualizados, parent 2.6.2 (mais recente 4.1.2; na mesma major, 2.7.18);
- a definição das receitas, lida nos arquivos `META-INF/rewrite/*.yml` dos JARs;
- o resultado do dryRun (`evidencias/F3/dryrun.patch`).

## Versões e licenças das receitas

As receitas do catálogo estão migrando para o Code Genome Project, e as versões mais novas do
`rewrite-spring` (6.38.0 em diante) e do `rewrite-migrate-java` (3.43.0 em diante) não estão no
Maven Central. O BOM `rewrite-recipe-bom` 3.38.0, que está no Central, já aponta para essas
versões ausentes. Por isso foi usado o último conjunto coerente que ficou inteiro no Central,
o do `rewrite-recipe-bom` 3.37.0, todo baseado no núcleo `rewrite` 8.89.0, a mesma versão do
plugin 6.46.1:

| Artefato | Versão | Mais recente no Central | Licença (lida do POM) |
|---|---|---|---|
| `org.openrewrite.maven:rewrite-maven-plugin` | 6.46.1 | 6.46.1 | The Apache Software License, Version 2.0 |
| `org.openrewrite.recipe:rewrite-spring` | 6.37.0 | 6.37.1 (núcleo 8.90.2) | Moderne Source Available License |
| `org.openrewrite.recipe:rewrite-migrate-java` | 3.42.0 | 3.42.1 (núcleo 8.90.2) | Moderne Source Available License |

As versões 6.37.1 e 3.42.1 usam o núcleo 8.90.2, diferente do 8.89.0 do plugin. Para evitar
mistura de versões do núcleo, foram escolhidas 6.37.0 e 3.42.0, publicadas juntas no BOM 3.37.0.

A licença Moderne Source Available permite aplicar as receitas ao próprio código e a
repositórios abertos, sem comercialização (OPENREWRITE, [2026e]). Os JARs são compilados para
Java 8 (bytecode 52), então o plugin roda com o JDK 8 do legado.

Receitas confirmadas nos JARs (todas no namespace `org.openrewrite`, nenhuma `io.moderne`):

| Receita | Arquivo no JAR |
|---|---|
| `org.openrewrite.java.springdoc.SpringFoxToSpringDoc` | `rewrite-spring`: `META-INF/rewrite/springdoc.yml` |
| `org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_5` | `rewrite-spring`: `META-INF/rewrite/spring-boot-35.yml` |
| `org.openrewrite.java.migrate.UpgradeToJava21` | `rewrite-migrate-java`: `META-INF/rewrite/java-version-21.yml` |

## Observações

1. **A ordem das receitas foi deduzida das definições delas**, lidas nos arquivos
   `META-INF/rewrite/*.yml` dos JARs, e não de uma recomendação da documentação do OpenRewrite.
   Não foi encontrada uma página que recomende a ordem dessas três receitas juntas.
2. **A receita do Spring Boot 3.5 também fez mudanças de estilo**, que não são necessárias para
   a migração: a cadeia `SpringBoot2BestPractices` trocou `@RequestMapping(method = ...)` por
   `@GetMapping`, `@PostMapping` etc. (`NoRequestMappingAnnotation`: 33 mapeamentos em 7 controllers) e tirou o
   `@Autowired` dos construtores (`NoAutowiredOnConstructor`). A cadeia do Java 21 também trocou
   `get(0)` por `getFirst()` e `remove(0)` por `removeFirst()` (`SequencedCollection`). Essas
   linhas entram na contagem de linhas alteradas pelo OpenRewrite no T08, junto com as mudanças
   de migração.
3. **Onde entraram o `getFirst()` e o `removeFirst()`.** Só em código de **teste**
   (`src/test`); nenhum arquivo de `src/main` recebeu esses métodos. Contagem de linhas no commit
   da F3:

   | Arquivo (`src/test/java/org/springframework/samples/petclinic/`) | `getFirst()` | `removeFirst()` | Lista e tamanho inicial |
   |---|---:|---:|---|
   | `rest/OwnerRestControllerTests.java` | 13 | 2 | `owners`, 4 itens |
   | `rest/PetRestControllerTests.java` | 9 | 0 | `pets`, 2 itens |
   | `rest/PetTypeRestControllerTests.java` | 8 | 2 | `petTypes`, 4 itens |
   | `rest/SpecialtyRestControllerTests.java` | 7 | 1 | `specialties`, 3 itens |
   | `rest/VetRestControllerTests.java` | 9 | 0 | `vets`, 3 itens |
   | `rest/VisitRestControllerTests.java` | 9 | 0 | `visits`, 2 itens |
   | `service/clinicService/AbstractClinicServiceTests.java` | 3 | 0 | `owner.getPets()` e `vet.getSpecialties()`, lidas do banco de exemplo |
   | **Total** | **58** | **5** | |

   **Nenhuma dessas listas fica vazia na execução normal.** Nos testes dos controllers, as listas
   são recriadas com `new ArrayList<>()` e preenchidas no `@BeforeEach` de cada teste, e cada teste
   chama `removeFirst()` no máximo uma vez, sobrando pelo menos 2 itens. No
   `AbstractClinicServiceTests`, as asserções anteriores já exigem os itens:
   `owner.getPets().size()` igual a 1 antes dos dois `getFirst()` do dono 1, e
   `vet.getNrOfSpecialties()` igual a 2 antes do `getFirst()` do veterinário 3. Se os dados de
   exemplo mudassem e a lista viesse vazia, o teste falharia antes, nessas asserções.

   A diferença só apareceria com a lista vazia: `get(0)` e `remove(0)` lançam
   `IndexOutOfBoundsException`, enquanto `getFirst()` e `removeFirst()` lançam
   `NoSuchElementException`. Como isso não acontece em nenhum desses pontos, a troca não muda o
   resultado dos testes. Também não há impacto em produção, porque o código de `src/main` não
   foi alterado por essa sub-receita.

   **Ponto para a F4:** essa troca não é exigida pelas versões novas (o `get(0)` continua válido no
   Java 21). A regra 6 só permite mudanças mecânicas exigidas pelas versões novas em `src/test`,
   então manter ou desfazer essas linhas é uma decisão a registrar no relatório da F4.

## Ordem das receitas

Ordem adotada no `rewrite.yml`: **SpringFoxToSpringDoc → UpgradeSpringBoot_3_5 → UpgradeToJava21**.

Não foi encontrada uma página da documentação que recomende explicitamente a ordem dessas três
receitas juntas (as páginas das receitas foram movidas para o Code Genome Project). A ordem foi
definida a partir da própria definição das receitas:

1. **SpringFoxToSpringDoc primeiro.** A sub-receita `ReplaceSpringFoxDependencies` troca o
   Springfox por `springdoc-openapi-ui` 1.5.x, com o comentário "aligns with spring boot 2.6",
   ou seja, ela foi feita para rodar ainda no Spring Boot 2. A cadeia do Spring Boot 3, por sua
   vez, contém `UpgradeSpringDoc_2` (no 3.0) até `UpgradeSpringDoc_2_8` (no 3.4), que levam o
   SpringDoc para a linha 2.x, compatível com Jakarta. Se a ordem fosse invertida, a cadeia do
   Boot 3 não encontraria o SpringDoc para atualizar.
2. **UpgradeSpringBoot_3_5 em seguida.** É a receita principal: passa por todas as versões do
   2.0 ao 3.5 e já inclui `UpgradeToJava17`, a migração `javax` → `jakarta`, o Spring Framework 6
   e o Spring Security 6.5.
3. **UpgradeToJava21 por último.** A cadeia do Boot leva o Java a 17; esta receita eleva a 21 e
   aplica as mudanças de linguagem e de API do Java 21. Ela só aumenta a versão, então rodar no
   fim garante que o resultado final seja o Java 21.

O dryRun confirmou a ordem: o `pom.xml` saiu com `springdoc-openapi-starter-webmvc-ui` 2.8.17
(o SpringDoc 2.x do Boot 3) e com `java.version` 21.

## Tabela de dependências

| Dependência | Versão atual | O que muda no Java 21 / Spring Boot 3.5 | Receita que trata | Resultado no dryRun / provável F4 |
|---|---|---|---|---|
| `spring-boot-starter-parent` | 2.6.2 | Boot 3 exige Java 17 e Jakarta EE 10 | `UpgradeSpringBoot_3_5` (`UpgradeParentVersion`) | Vai para 3.5.16 |
| Starters do Spring Boot (web, data-jpa, jdbc, security, validation, cache, aop, actuator, test) | 2.6.2 (do parent) | Versões vêm do parent | `UpgradeSpringBoot_3_5` | Seguem o parent; nada a fazer |
| `javax.persistence`, `javax.validation`, `javax.transaction`, `javax.servlet` no código (53, 14, 7 e 1 imports) | Java EE 8 | Pacotes passam a `jakarta.*` | `JavaxMigrationToJakarta` (dentro do Boot 3.0) | Trocados em 33 arquivos; `javax.sql` fica (é do JDK) |
| `io.springfox:springfox-boot-starter` | 3.0.0 | Sem versão para Boot 3 / Jakarta | `SpringFoxToSpringDoc` | Dependência trocada por `springdoc-openapi-starter-webmvc-ui` 2.8.17; o `Docket` e o `ApiInfo` foram removidos de `ApplicationSwaggerConfig`. **F4:** a classe ainda importa `WebMvcRequestHandlerProvider` e `WebFluxRequestHandlerProvider` do Springfox (o "workaround" do Boot 2.6), o que deve quebrar a compilação; o título, a descrição e o contato da API se perdem |
| Propriedade `springfox-swagger.version` | 3.0.0 | Fica sem uso | nenhuma | **F4:** sobra no `pom.xml` |
| Spring Security (`WebSecurityConfigurerAdapter`, `@EnableGlobalMethodSecurity`) | 5.6.1 | A classe base foi removida no Security 6 | `UpgradeSpringSecurity_6_5` (dentro do Boot 3.5) | Convertidos para `SecurityFilterChain`, `authorizeHttpRequests` e `@EnableMethodSecurity`. **F4:** conferir se `@EnableMethodSecurity` mantém o comportamento das regras `@PreAuthorize` com `@roles` |
| `javax.xml.bind:jaxb-api` | 2.3.0 | JAXB saiu do JDK no Java 11 (OPENJDK, 2017); no Jakarta vira `jakarta.xml.bind` | `UpgradeSpringBoot_3_0` / `JavaxMigrationToJakarta` | Trocada por `jakarta.xml.bind-api`; propriedade `jaxb-api.version` removida |
| `org.mapstruct:mapstruct` e `mapstruct-processor` | 1.4.1.Final | Versões antigas do processador não suportam bem Java 17+ | uma sub-receita `UpgradeDependencyVersion` da cadeia (o log do dryRun não separa qual) | Vão para 1.6.3 |
| `mysql:mysql-connector-java` | 8.0.27 | Coordenada nova `com.mysql:mysql-connector-j` | `UpgradeSpringBoot_3_0` (`ChangeDependency`) | Trocada; versão do parent |
| `org.postgresql:postgresql`, `org.hsqldb:hsqldb` | 42.3.1 / 2.5.2 | Versões vêm do parent | parent | Seguem o parent |
| `org.springframework.data:spring-data-jdbc-core` | 1.2.1.RELEASE | Versão fixa, de 2015; incompatível com Spring Framework 6 | nenhuma | **F4:** não foi tocada; deve gerar conflito de classes com o Spring 6 |
| `org.openapitools:jackson-databind-nullable` | 0.2.1 | Versão fixa e antiga | nenhuma | **F4:** não foi tocada; avaliar atualização |
| Jackson (`jackson-core`, `jackson-databind`, `jackson-datatype-jsr310`) | 2.13.1 (do parent) | Versão vem do parent | parent | Seguem o parent |
| `com.jayway.jsonpath:json-path`, `org.mockito:mockito-core` | 2.6.0 / 4.0.0 | Versões vêm do parent | parent | Seguem o parent |
| `spring-security-test`, `spring-boot-starter-test` | 5.6.1 / 2.6.2 | Versões vêm do parent | parent | Seguem o parent |
| Plugin `openapi-generator-maven-plugin` | 5.2.1 | Gera os DTOs (`org.springframework.samples.petclinic.dto`) a partir de `api-docs.yml` no build; a 5.2.1 gera código com `javax.*` | nenhuma | **F4:** provável quebra de compilação, porque os DTOs gerados usam `javax.validation`/`javax.annotation`; é preciso atualizar o plugin e ligar as opções de Jakarta / Spring Boot 3 |
| Plugin `jacoco-maven-plugin` | 0.8.7 | 0.8.7 não instrumenta bytecode do Java 21 | `UpgradeToJava21` (`UpgradePluginsForJava21`) | Vai para 0.8.16 |
| Plugin `build-helper-maven-plugin` | 3.2.0 | Versão passa a vir do parent | `UpgradeSpringBoot_3_x` | Versão explícita removida (fica a do parent) |
| Plugin `jib-maven-plugin` | 1.3.0 | Antigo; não afeta build nem testes | nenhuma | Fora do escopo; sobra desatualizado |
| `.github/workflows/maven-build.yml` | Java 11 | Pipeline do repositório | `UpgradeToJava21` (`SetupJavaUpgradeJavaVersion`) | Vai para Java 21 |
| Propriedade de teste `security.ignored` | — | Removida no Boot 3 | `SpringBootProperties_3_0` | Comentada com aviso |

## Resumo do que provavelmente sobra para a F4

1. `ApplicationSwaggerConfig`: imports e código restantes do Springfox.
2. `openapi-generator-maven-plugin` 5.2.1 gerando DTOs com `javax.*`.
3. `spring-data-jdbc-core` 1.2.1.RELEASE fixo.
4. `jackson-databind-nullable` 0.2.1 fixo.
5. Propriedade `springfox-swagger.version` sem uso.
6. Metadados da documentação da API (título, contato) que eram definidos no `Docket`.
7. Conferir o comportamento da segurança por método (`@EnableMethodSecurity`) e da validação.

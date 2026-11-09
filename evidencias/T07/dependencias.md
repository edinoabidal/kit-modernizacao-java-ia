# T07: conferência das dependências da versão final

- Data: 2026-11-09
- Projeto: `spring-petclinic-rest`, commit `7c0326d`, parent `spring-boot-starter-parent` 3.5.16
- Fontes: os relatórios do `versions-maven-plugin` gerados pelo `medir.py` no T07
  (`medicao-final-20261109-113524/`), o `pom.xml` final, o BOM `spring-boot-dependencies-3.5.16.pom`
  e o Maven Central (`repo1.maven.org`). A data de lançamento de cada versão é o `Last-Modified` do
  POM daquela versão no Central. A versão estável mais recente é a última do `maven-metadata.xml`,
  sem as pré-releases (alpha, beta, RC, milestone e SNAPSHOT).
- Nenhum arquivo do projeto foi alterado.

## 1. Dependências desatualizadas na mesma major

O `medir.py` registrou `deps_desatualizadas_mesma_major=10`, mas o relatório tem **11** dependências.
O nome `com.fasterxml.jackson.datatype:jackson-datatype-jsr310` é longo, e o `versions-maven-plugin`
quebra essa entrada em duas linhas: o nome fica numa e as versões na seguinte. O script só conta as
linhas que trazem o nome e a seta `->` juntos, então essa entrada fica de fora. Pela regra 5, o
script não foi alterado, e a diferença fica registrada aqui.

| Dependência | Versão atual | Mais recente na mesma major | Origem da versão |
|---|---|---|---|
| `com.fasterxml.jackson.core:jackson-core` | 2.21.4 | 2.23.0 | BOM do Boot 3.5.16 (`jackson-bom.version`) |
| `com.fasterxml.jackson.core:jackson-databind` | 2.21.4 | 2.23.0 | BOM do Boot 3.5.16 (`jackson-bom.version`) |
| `com.fasterxml.jackson.datatype:jackson-datatype-jsr310` (fora da contagem do script) | 2.21.4 | 2.23.0 | BOM do Boot 3.5.16 (`jackson-bom.version`) |
| `com.jayway.jsonpath:json-path` | 2.9.0 | 2.10.0 | BOM do Boot 3.5.16 (`json-path.version`) |
| `jakarta.servlet:jakarta.servlet-api` | 6.0.0 | 6.1.0 | BOM do Boot 3.5.16 (`jakarta-servlet.version`) |
| `jakarta.validation:jakarta.validation-api` | 3.0.2 | 3.1.1 | BOM do Boot 3.5.16 (`jakarta-validation.version`) |
| `org.hsqldb:hsqldb` | 2.7.3 | 2.7.4 | BOM do Boot 3.5.16 (`hsqldb.version`) |
| `org.mockito:mockito-core` | 5.17.0 | 5.24.0 | BOM do Boot 3.5.16 (`mockito.version`) |
| `org.openapitools:jackson-databind-nullable` | 0.2.1 | 0.2.13 | Fixada no `pom.xml` (propriedade `jackson-databind-nullable.version`, igual à do legado) |
| `org.postgresql:postgresql` | 42.7.11 | 42.7.14 | BOM do Boot 3.5.16 (`postgresql.version`) |
| `org.springdoc:springdoc-openapi-starter-webmvc-ui` | 2.8.17 | 2.10.0 | Fixada no `pom.xml` (versão literal, entrou na F3) |

Das 11, 9 vêm do BOM e mudam junto com o parent. As 2 fixadas no `pom.xml` são o
`jackson-databind-nullable` e o `springdoc`. A F4 manteve o springdoc na linha 2.8, que é a do Boot
3.4/3.5 (relatório da F4).

A mesma quebra de linha acontece na lista "qualquer major": o relatório tem 21 dependências e mais
o `spring-boot-maven-plugin` no `pluginManagement`, e o script contou 17. Os 5 nomes quebrados são o
`jackson-datatype-jsr310` e os starters `actuator`, `data-jpa`, `security` e `validation` do Boot. Os relatórios do legado também têm 5 entradas
quebradas, então a contagem fica abaixo do real nas duas fases. O CSV não foi corrigido.

## 2. Versões fixadas no `pom.xml` final

Versões que não vêm do BOM do Boot 3.5.16, com a data do último lançamento estável de cada artefato
no Central. A data de corte para "mais de três anos sem lançamento" é 2023-11-09.

### Dependências

| Artefato | Versão no `pom.xml` | Lançamento da versão usada | Última estável | Lançamento da última | Mais de 3 anos sem lançamento? |
|---|---|---|---|---|---|
| `org.springframework.data:spring-data-jdbc-core` | 1.2.1.RELEASE (propriedade `spring-data-jdbc.version`) | 2015-11-25 | 1.2.1.RELEASE | 2015-11-25 | **Sim, cerca de 11 anos** |
| `org.openapitools:jackson-databind-nullable` | 0.2.1 (propriedade) | 2019-12-19 | 0.2.13 | 2026-10-25 | Não |
| `org.springdoc:springdoc-openapi-starter-webmvc-ui` | 2.8.17 (literal) | 2026-04-11 | 3.2.0 (2.10.0 na mesma major) | 2026-10-24 | Não |
| `org.mapstruct:mapstruct` | 1.6.3 (propriedade `mapstruct.version`) | 2024-11-09 | 1.6.3 (1.7.0.Beta2, pré-release, de 2026-06-27) | 2024-11-09 | Não (2 anos) |
| `org.mapstruct:mapstruct-processor` (dependência e `annotationProcessorPaths`) | 1.6.3 (propriedade `mapstruct.version`) | 2024-11-09 | 1.6.3 (1.7.0.Beta2, pré-release, de 2026-06-27) | 2024-11-09 | Não (2 anos) |

### Plugins

| Plugin | Versão efetiva | Lançamento da versão usada | Última estável | Lançamento da última | Mais de 3 anos sem lançamento? |
|---|---|---|---|---|---|
| `org.jacoco:jacoco-maven-plugin` | 0.8.16 (propriedade) | 2026-10-26 | 0.8.16 | 2026-10-26 | Não |
| `org.openapitools:openapi-generator-maven-plugin` | 7.27.0 (propriedade) | 2026-11-02 | 7.27.0 | 2026-11-02 | Não |
| `com.google.cloud.tools:jib-maven-plugin` | 1.3.0 (propriedade, igual à do legado) | 2019-06-07 | 3.5.2 | 2026-07-14 | Não. A versão usada tem 7 anos |
| `org.codehaus.mojo:build-helper-maven-plugin` | 3.2.0 (ver a observação) | 2020-06-17 | 3.7.0 | 2026-11-06 | Não. A versão usada tem 6 anos |

Observação sobre o `build-helper-maven-plugin`: no `pom.xml` final o plugin não tem `<version>`, mas a
propriedade `build-helper-maven-plugin.version` (3.2.0, do legado) continua declarada. Ela tem o mesmo
nome da propriedade do BOM do Boot, que é 3.6.1, e a sobrescreve. Por isso a versão efetiva é 3.2.0,
como mostra o log do build (`build-helper-maven-plugin:3.2.0`).

**O único artefato há mais de três anos sem lançamento é o `spring-data-jdbc-core`.** Os outros têm
lançamentos de 2024 a 2026. O `jib-maven-plugin` 1.3.0, o `build-helper-maven-plugin` 3.2.0 e o
`jackson-databind-nullable` 0.2.1 são versões antigas de artefatos que continuam ativos.

## 3. `spring-data-jdbc-core` 1.2.1.RELEASE

- **Continua no projeto**, com a mesma versão e a mesma exclusão de `org.springframework:*` do legado.
  Nenhuma das fases mexeu nele. O JAR final leva `BOOT-INF/lib/spring-data-jdbc-core-1.2.1.RELEASE.jar`.
- O artefato é do antigo projeto Spring Data JDBC Extensions. O último e único lançamento da linha
  1.2 é de 2015-11-25. Ele não tem relação com o `spring-data-jdbc` atual, que está no BOM do Boot.
- A dependência transitiva `spring-retry` era 1.3.1 no legado e agora é 2.0.13, porque o BOM do Boot
  3.5.16 fixa essa versão (`dependency:tree`).
- **Quem usa:** uma só classe de produção importa o pacote `org.springframework.data.jdbc`:
  - `src/main/java/org/springframework/samples/petclinic/repository/jdbc/JdbcPetVisitExtractor.java`
    estende `org.springframework.data.jdbc.core.OneToManyResultSetExtractor<JdbcPet, Visit, Integer>`.
  - Essa classe só é usada em `JdbcOwnerRepositoryImpl.loadPetsAndVisits(Owner)`, que monta os pets e
    as visitas de um dono no perfil `jdbc`.
  - Nenhum teste importa o pacote. O `JdbcPetVisitExtractor` é exercitado pelos testes do perfil
    `jdbc` (`ClinicServiceJdbcTests`, 33 testes aprovados no T07), com 8 de 8 linhas cobertas no JaCoCo.
- Funciona no Spring 6 porque o `OneToManyResultSetExtractor` só usa APIs do Spring que continuam
  iguais (`ResultSetExtractor` e `RowMapper` do `spring-jdbc`, `IncorrectResultSizeDataAccessException`
  e `Assert`), conferidas no bytecode com `javap`.
- Trocar ou remover essa dependência mudaria código de repositório, o que a regra 1 não permite.
  O ponto fica registrado como risco de manutenção, sem mudança.

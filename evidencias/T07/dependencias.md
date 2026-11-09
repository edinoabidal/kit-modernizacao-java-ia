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

O relatório tem **11** dependências desatualizadas na mesma major. Na primeira execução, o `medir.py`
registrou 10, porque o `versions-maven-plugin` quebra a entrada do
`com.fasterxml.jackson.datatype:jackson-datatype-jsr310` em duas linhas: o nome fica numa e as versões
na seguinte. O script só contava as linhas com o nome e a seta `->` juntos. A contagem foi corrigida
depois, como descreve a seção 4.

| Dependência | Versão atual | Mais recente na mesma major | Origem da versão |
|---|---|---|---|
| `com.fasterxml.jackson.core:jackson-core` | 2.21.4 | 2.23.0 | BOM do Boot 3.5.16 (`jackson-bom.version`) |
| `com.fasterxml.jackson.core:jackson-databind` | 2.21.4 | 2.23.0 | BOM do Boot 3.5.16 (`jackson-bom.version`) |
| `com.fasterxml.jackson.datatype:jackson-datatype-jsr310` (entrada quebrada em duas linhas) | 2.21.4 | 2.23.0 | BOM do Boot 3.5.16 (`jackson-bom.version`) |
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

A mesma quebra acontece na lista de qualquer major. O relatório tem 21 dependências e mais o
`spring-boot-maven-plugin` no `pluginManagement`, 22 entradas no total, e a primeira execução contou 17.
Os 5 nomes quebrados são o `jackson-datatype-jsr310` e os starters `actuator`, `data-jpa`, `security`
e `validation` do Boot.

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

## 4. Correção da contagem no `medir.py`

Com autorização do autor, como exceção à regra 5 limitada a esse ponto, o `medir.py` passou a juntar
as entradas que o `versions-maven-plugin` quebra em duas linhas antes de contar. A correção é a função
`_juntar_linhas_quebradas`, usada na contagem de dependências e na de plugins. O `README-medir.md`
registra a mudança.

As três medições foram recalculadas com as funções corrigidas, a partir das saídas brutas guardadas de
cada execução, sem rodar os builds de novo (`recalcular-contagens.py`, saída em `recalculo-contagens.txt`).

| Medição | Coluna | Antes | Depois | Linhas `->` nos relatórios | Entradas quebradas |
|---|---|---:|---:|---:|---:|
| F1 (legado, 517a399) | deps_desatualizadas | 18 | 23 | 23 | 5 |
| | deps_desatualizadas_mesma_major | 18 | 23 | 23 | 5 |
| | plugins_desatualizados | 4 | 4 | 4 plugins com versão maior | 0 |
| T05 (openrewrite, d0d758d) | deps_desatualizadas | 17 | 22 | 22 | 5 |
| | deps_desatualizadas_mesma_major | 10 | 11 | 11 | 1 |
| | plugins_desatualizados | 3 | **2** | 2 plugins com versão maior (jacoco só com versões anteriores) | 0 |
| T07 (final, 7c0326d) | deps_desatualizadas | 17 | 22 | 22 | 5 |
| | deps_desatualizadas_mesma_major | 10 | 11 | 11 | 1 |
| | plugins_desatualizados | 2 | **1** | 1 plugin com versão maior (jacoco só com versões anteriores) | 0 |

As contagens novas batem com as linhas dos relatórios: no T07, 22 em qualquer major e 11 na mesma
major. Nenhum relatório de plugins tem entradas quebradas.

Numa segunda correção, também autorizada pelo autor, os plugins passaram a contar só quando a
versão nova é maior que a atual. Os blocos "Require Maven X para usar..." do relatório listam também
versões anteriores: no T05 e no T07, o `jacoco-maven-plugin` 0.8.16, que é a versão mais recente,
aparecia com `0.8.16 -> 0.8.2` e `0.8.16 -> 0.6.3...` e era contado. Com a correção, o T05 passa de 3
para 2 (jib e openapi-generator) e o T07, de 2 para 1 (só o jib). O legado continua com 4, porque
os quatro plugins têm versão maior disponível. O `build-helper-maven-plugin` 3.2.0 da versão final
não aparece no relatório, porque não tem `<version>` no `pom.xml` (ver a seção 2); esse limite do
indicador fica registrado.

A errata das duas correções, com o caminho do relatório bruto até a tabela do TCC, está em
`ERRATA.md`, na raiz do kit.

Onde ficou registrado:

- `medicoes/medicoes.csv`: as três linhas com os valores corrigidos, sem mudar as outras colunas.
- `medicoes/medicoes-v3.csv`: cópia do `medicoes.csv` antes da correção das dependências.
- `medicoes/medicoes-v4.csv`: cópia do `medicoes.csv` depois da correção das dependências e antes da correção dos plugins.
- `medicoes/correcao-contagem-dependencias.csv`: o valor antigo e o corrigido de cada coluna em cada linha.
- `linha-medicoes.csv` e `saida-medir.txt` do T05 e do T07 ficaram como estavam, porque são a saída
  original de cada execução.

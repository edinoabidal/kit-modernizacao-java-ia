# T05 — Erros de compilação após o OpenRewrite (fase openrewrite)

- Commit medido: `d0d758d` (branch modernizacao, "F3: OpenRewrite (receita composta tcc.ModernizacaoPetClinic)")
- JDK: Temurin 21.0.13 (só no JAVA_HOME dos comandos do script); Maven 3.6.3 (wrapper)
- Comando: `kit/scripts/medir.py --fase openrewrite` (build `mvnw -B clean verify`)
- Resultado: `falha_compilacao`, código de saída 1, 76,5 s. Falhou no `maven-compiler-plugin:3.14.1:compile` (código de produção); o `testCompile` não chegou a rodar.
- Como o build falhou, a API não subiu e a suíte de caracterização não foi executada. Nada foi corrigido.
- Fonte: `medicao-openrewrite-20261109-100726/build.log`, bloco "COMPILATION ERROR".

## Atenção: a contagem está truncada

O javac parou em **100 erros**, que é o limite padrão (`-Xmaxerrs 100`). O log mostra
`[INFO] 100 errors`, então o total real é **pelo menos 100**. Erros que viriam depois
(outros usos de `@ApiModelProperty`, `@Valid`, `@NotNull` etc. nos DTOs, o restante do
`ApplicationSwaggerConfig` e qualquer erro em `src/test`) não aparecem no log.

## Resumo

| # | Causa | Erros | Arquivos |
|---|---|---:|---:|
| A | Anotações do Swagger 2 (`io.swagger.annotations`) nos DTOs gerados | 46 | 16 |
| B | Bean Validation em `javax.validation` nos DTOs gerados | 36 | 16 |
| C | `javax.annotation.Generated` nos DTOs gerados | 16 | 16 |
| D | Imports do Springfox no `ApplicationSwaggerConfig` | 2 | 1 |
| | **Total (truncado pelo javac)** | **100** | **17** |

As causas A, B e C vêm do mesmo ponto: o `openapi-generator-maven-plugin` continua na
versão 5.2.1 e gera os DTOs com as anotações do Swagger 2 e os pacotes `javax.*`. Com o
Spring Boot 3.5, o Springfox saiu do classpath (levando o `io.swagger:swagger-annotations` 1.x)
e as APIs passaram a ser `jakarta.*`. Os 98 erros dessas causas estão em código **gerado**
(`target/generated-sources/openapi`), que a receita do OpenRewrite não alcança, porque
ele não existe no código-fonte versionado.

A causa D está em código de produção versionado: a receita trocou a dependência do
Springfox pelo springdoc no `pom.xml`, mas o `ApplicationSwaggerConfig` ainda importa
classes do Springfox.

## A — `io.swagger.annotations` (46 erros, 16 arquivos)

| Mensagem | Erros |
|---|---:|
| `package io.swagger.annotations does not exist` | 32 |
| `cannot find symbol: class ApiModel` | 13 |
| `cannot find symbol: class ApiModelProperty` | 1 |

## B — `javax.validation` (36 erros, 16 arquivos)

| Mensagem | Erros |
|---|---:|
| `package javax.validation does not exist` | 16 |
| `package javax.validation.constraints does not exist` | 16 |
| `cannot find symbol: class Valid` | 1 |
| `cannot find symbol: class NotNull` | 1 |
| `cannot find symbol: class Pattern` | 1 |
| `cannot find symbol: class Size` | 1 |

## C — `javax.annotation` (16 erros, 16 arquivos)

| Mensagem | Erros |
|---|---:|
| `package javax.annotation does not exist` (`@javax.annotation.Generated`) | 16 |

### Arquivos das causas A, B e C (os mesmos 16)

Todos em `target/generated-sources/openapi/src/main/java/org/springframework/samples/petclinic/dto/`:

- OwnerAllOfDto.java
- OwnerDto.java
- OwnerFieldsDto.java
- PetAllOfDto.java
- PetDto.java
- PetFieldsDto.java
- PetTypeDto.java
- RestErrorDto.java
- RoleDto.java
- SpecialtyDto.java
- UserDto.java
- ValidationMessageDto.java
- VetDto.java
- VisitAllOfDto.java
- VisitDto.java
- VisitFieldsDto.java

## D — Springfox (2 erros, 1 arquivo)

| Mensagem | Erros |
|---|---:|
| `package springfox.documentation.spring.web.plugins does not exist` | 2 |

Arquivo: `src/main/java/org/springframework/samples/petclinic/util/ApplicationSwaggerConfig.java`
(linhas 28 e 29: imports de `WebFluxRequestHandlerProvider` e `WebMvcRequestHandlerProvider`).

## Outras medidas do T05

| Medida | Valor |
|---|---|
| Testes | N/D (build parou na compilação) |
| Cobertura (linhas / ramos) | N/D (JaCoCo não gerou relatório) |
| Dependências declaradas | 26 |
| Entradas desatualizadas (qualquer major / mesma major) | 22 / 11 |
| Plugins com versão maior disponível | 2 |
| Parent atual / mais recente / mais recente na mesma major | 3.5.16 / 4.1.2 / 3.5.16 |
| Árvore limpa após a medição | sim |

Valores corrigidos conforme a `ERRATA.md`. A saída original do script, em `saida-medir.txt` e
`linha-medicoes.csv`, mostra os valores antigos (17 / 10 e 3 plugins).

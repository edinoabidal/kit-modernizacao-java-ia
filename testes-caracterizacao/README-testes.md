# Testes de caracterização da API do Spring PetClinic REST

Projeto Maven independente que registra o comportamento **atual** da API da versão legada
(commit `517a399`). A mesma suíte roda depois contra a versão modernizada: se algum teste
falhar, o comportamento mudou.

O projeto **não depende do código do PetClinic**: ele só faz chamadas HTTP à API em execução.

## Versões usadas

| Item | Versão |
|---|---|
| Java (compilação) | 8 (`maven.compiler.source/target = 1.8`); roda com JDK 8 e JDK 21 |
| Maven (via Maven Wrapper) | 3.6.3 |
| REST Assured | 5.5.7 (última linha compatível com Java 8; a 6.x exige Java mais novo) |
| JUnit | 5.14.4 (a linha 6.x exige Java 17) |
| Jackson Databind | 2.22.4 (usado pelo REST Assured para montar o JSON das requisições) |
| Hamcrest | 3.0 |
| maven-surefire-plugin | 3.5.6 |
| maven-compiler-plugin | 3.14.1 |

## Como rodar

1. Suba a aplicação (por padrão em `http://localhost:9966/petclinic`).
2. Na pasta `testes-caracterizacao`, rode:

```bash
# Linux / WSL
JAVA_HOME=/caminho/do/jdk ./mvnw -B clean test

# Windows
set JAVA_HOME=C:\caminho\do\jdk
mvnw.cmd -B clean test
```

Para apontar para outra URL base, sem mudar o código:

```bash
./mvnw -B clean test -Dapi.baseUrl=http://outro-host:8080/petclinic/api
```

Os relatórios ficam em `target/surefire-reports`. Os testes rodam em **ordem aleatória**
(no JUnit e no Surefire), para comprovar que não dependem uns dos outros.

## Testes

| ID | Teste | Objetivo |
|---|---|---|
| TC01 | `listaDeDonosContemDadosIniciais` | `GET /owners`: 200, JSON, os 10 donos iniciais presentes e um dono completo (Jean Coleman, Monona, pets Max e Samantha). Não confere o tamanho exato, porque os testes de cadastro podem incluir donos. |
| TC02 | `donoPorIdComDadosIniciais` | `GET /owners/1`: 200, JSON, George Franklin com endereço, cidade, telefone e o pet Leo (cat). |
| TC03 | `buscaDeDonosPeloSobrenome` | `GET /owners/*/lastname/Davis`: 200, JSON, exatamente Betty e Harold, em qualquer ordem. |
| TC04 | `listasDeVeterinariosETiposDePet` | `GET /vets`: 6 veterinários e as especialidades de cada um. `GET /pettypes`: os 6 tipos de pet. |
| TC05 | `cadastroDeDonoEConsulta` | `POST /owners`: 201, JSON, cabeçalho `Location` e o dono no corpo; em seguida `GET /owners/{id}` devolve os mesmos dados. |
| TC06 | `atualizacaoDeDono` | Cadastra um dono próprio, `PUT /owners/{id}` devolve 204 sem corpo e a consulta mostra os dados novos. |
| TC07 | `donoInexistente` | `GET /owners/999999` e busca por sobrenome inexistente: 404 com corpo vazio. |
| TC08 | `cadastroInvalido` | `POST /owners` com telefone inválido: 400, corpo vazio e o erro descrito no cabeçalho `errors`. |

## Regras dos testes

- Conferem o código HTTP, o tipo de conteúdo e os campos que importam, com os valores que a
  versão legada devolve hoje.
- Não conferem ids gerados, datas nem uma ordem que a API não garante.
- Os testes de escrita usam dados próprios (sobrenomes `Cadastro`, `Atualizacao` e
  `Invalido`, que não existem nos dados iniciais) e não alteram os dados usados pelos testes
  de leitura.
- A aplicação usa banco em memória (HSQLDB): reiniciá-la volta aos dados iniciais.

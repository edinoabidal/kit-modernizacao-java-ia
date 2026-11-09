package br.tcc.modernizacao.caracterizacao;

import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import io.restassured.response.Response;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;

import java.util.HashMap;
import java.util.Map;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.containsInAnyOrder;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.emptyString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.hasItems;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.matchesPattern;
import static org.hamcrest.Matchers.notNullValue;

/**
 * Testes de caracterização da API do Spring PetClinic REST.
 *
 * Eles registram o comportamento ATUAL da versão legada (commit 517a399), sem julgar se
 * está certo. Depois da modernização, a mesma suíte roda contra a versão nova: se algum
 * teste falhar, o comportamento mudou.
 *
 * Regras seguidas:
 * - não conferimos ids gerados, datas nem ordem que a API não garante;
 * - os testes de escrita usam dados próprios (sobrenomes que não existem nos dados iniciais),
 *   então não afetam os testes de leitura, em qualquer ordem de execução;
 * - a URL base vem da propriedade "api.baseUrl" (padrão: http://localhost:9966/petclinic/api).
 */
@TestMethodOrder(MethodOrderer.Random.class) // ordem aleatória, para provar a independência
class ApiPetClinicCaracterizacaoTest {

    @BeforeAll
    static void configurarUrlBase() {
        // A URL base pode ser trocada sem mexer no código: -Dapi.baseUrl=http://outro-host/...
        RestAssured.baseURI = System.getProperty("api.baseUrl", "http://localhost:9966/petclinic/api");
        // Em caso de falha, mostra a requisição e a resposta completas no log.
        RestAssured.enableLoggingOfRequestAndResponseIfValidationFails();
    }

    /** Monta o corpo JSON de um dono. Os dados são próprios dos testes de escrita. */
    private static Map<String, Object> dono(String nome, String sobrenome, String endereco,
                                            String cidade, String telefone) {
        Map<String, Object> corpo = new HashMap<>();
        corpo.put("firstName", nome);
        corpo.put("lastName", sobrenome);
        corpo.put("address", endereco);
        corpo.put("city", cidade);
        corpo.put("telephone", telefone);
        return corpo;
    }

    /** Cadastra um dono e devolve o id gerado (o valor do id não é conferido). */
    private static int cadastrarDono(Map<String, Object> corpo) {
        return given().contentType(ContentType.JSON).body(corpo)
                .when().post("/owners")
                .then().statusCode(201)
                .extract().path("id");
    }

    // ------------------------------------------------------------------ leitura

    @Test
    @DisplayName("TC01 - lista de donos contém os 10 donos dos dados iniciais")
    void listaDeDonosContemDadosIniciais() {
        // Confere que os 10 donos iniciais estão na lista. Não conferimos o tamanho exato,
        // porque os testes de cadastro podem ter incluído donos novos antes deste.
        given()
        .when().get("/owners")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("size()", greaterThanOrEqualTo(10))
            .body("lastName", hasItems("Franklin", "Davis", "Rodriquez", "McTavish", "Coleman",
                    "Black", "Escobito", "Schroeder", "Estaban"))
            .body("firstName", hasItems("George", "Betty", "Eduardo", "Harold", "Peter", "Jean",
                    "Jeff", "Maria", "David", "Carlos"))
            // um dono completo, localizado pelo nome (sem depender da posição na lista)
            .body("find { it.firstName == 'Jean' && it.lastName == 'Coleman' }.city", equalTo("Monona"))
            .body("find { it.firstName == 'Jean' && it.lastName == 'Coleman' }.pets.name",
                    containsInAnyOrder("Max", "Samantha"));
    }

    @Test
    @DisplayName("TC02 - dono pelo id 1 devolve George Franklin com o pet Leo")
    void donoPorIdComDadosIniciais() {
        // O id 1 vem dos dados iniciais (não é gerado pelo teste), por isso pode ser usado.
        given()
        .when().get("/owners/1")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("id", equalTo(1))
            .body("firstName", equalTo("George"))
            .body("lastName", equalTo("Franklin"))
            .body("address", equalTo("110 W. Liberty St."))
            .body("city", equalTo("Madison"))
            .body("telephone", equalTo("6085551023"))
            .body("pets", hasSize(1))
            .body("pets[0].name", equalTo("Leo"))
            .body("pets[0].type.name", equalTo("cat"));
    }

    @Test
    @DisplayName("TC03 - busca pelo sobrenome Davis devolve Betty e Harold")
    void buscaDeDonosPeloSobrenome() {
        // A rota da versão legada é /owners/*/lastname/{sobrenome}.
        // A ordem dos resultados não é garantida, por isso usamos containsInAnyOrder.
        given()
        .when().get("/owners/*/lastname/Davis")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("", hasSize(2))
            .body("lastName", everyItem(equalTo("Davis")))
            .body("firstName", containsInAnyOrder("Betty", "Harold"))
            .body("city", containsInAnyOrder("Sun Prairie", "Windsor"));
    }

    @Test
    @DisplayName("TC04 - lista de veterinários e lista de tipos de pet")
    void listasDeVeterinariosETiposDePet() {
        // Veterinários: os 6 dos dados iniciais, com as especialidades de cada um.
        // Nenhum teste cadastra veterinários, então o tamanho exato pode ser conferido.
        given()
        .when().get("/vets")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("", hasSize(6))
            .body("lastName", containsInAnyOrder("Carter", "Leary", "Douglas", "Ortega", "Stevens", "Jenkins"))
            .body("find { it.lastName == 'Douglas' }.specialties.name", containsInAnyOrder("dentistry", "surgery"))
            .body("find { it.lastName == 'Leary' }.specialties.name", containsInAnyOrder("radiology"))
            .body("find { it.lastName == 'Carter' }.specialties", empty());

        // Tipos de pet: os 6 tipos dos dados iniciais.
        given()
        .when().get("/pettypes")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("", hasSize(6))
            .body("name", containsInAnyOrder("cat", "dog", "lizard", "snake", "bird", "hamster"));
    }

    // ------------------------------------------------------------------ escrita

    @Test
    @DisplayName("TC05 - cadastro de um dono novo e consulta dele em seguida")
    void cadastroDeDonoEConsulta() {
        // Dados próprios: o sobrenome não existe nos dados iniciais.
        Map<String, Object> novo = dono("Ana", "Cadastro", "Rua das Flores, 10", "Campinas", "1932221100");

        // O cadastro devolve 201, o dono criado no corpo e o endereço dele no cabeçalho Location.
        Response resposta = given().contentType(ContentType.JSON).body(novo)
            .when().post("/owners")
            .then()
                .statusCode(201)
                .contentType(ContentType.JSON)
                .header("Location", matchesPattern(".*/owners/\\d+$"))
                .body("id", notNullValue())
                .body("firstName", equalTo("Ana"))
                .body("lastName", equalTo("Cadastro"))
                .body("city", equalTo("Campinas"))
                .body("pets", empty())
                .extract().response();

        // Consulta pelo id devolvido (o valor do id em si não é conferido).
        int id = resposta.path("id");
        given()
        .when().get("/owners/" + id)
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("firstName", equalTo("Ana"))
            .body("lastName", equalTo("Cadastro"))
            .body("address", equalTo("Rua das Flores, 10"))
            .body("city", equalTo("Campinas"))
            .body("telephone", equalTo("1932221100"))
            .body("pets", empty());
    }

    @Test
    @DisplayName("TC06 - atualização de um dono cadastrado pelo próprio teste")
    void atualizacaoDeDono() {
        // Cadastra um dono próprio, para não alterar os dados iniciais usados nos testes de leitura.
        int id = cadastrarDono(dono("Bruno", "Atualizacao", "Av. Brasil, 100", "Santos", "1333334444"));

        // A atualização devolve 204 (sem corpo).
        given().contentType(ContentType.JSON)
            .body(dono("Bruno", "Atualizacao", "Av. Paulista, 2000", "São Paulo", "1155556666"))
        .when().put("/owners/" + id)
        .then()
            .statusCode(204)
            .body(emptyString());

        // A consulta seguinte mostra os dados novos.
        given()
        .when().get("/owners/" + id)
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("firstName", equalTo("Bruno"))
            .body("lastName", equalTo("Atualizacao"))
            .body("address", equalTo("Av. Paulista, 2000"))
            .body("city", equalTo("São Paulo"))
            .body("telephone", equalTo("1155556666"));
    }

    // ------------------------------------------------------------------ erros

    @Test
    @DisplayName("TC07 - dono inexistente e busca sem resultado devolvem 404 sem corpo")
    void donoInexistente() {
        // Na versão legada, um id que não existe devolve 404 com corpo vazio.
        given()
        .when().get("/owners/999999")
        .then()
            .statusCode(404)
            .body(emptyString());

        // A busca por um sobrenome sem nenhum dono também devolve 404 com corpo vazio.
        given()
        .when().get("/owners/*/lastname/SobrenomeQueNaoExiste")
        .then()
            .statusCode(404)
            .body(emptyString());
    }

    @Test
    @DisplayName("TC08 - cadastro inválido devolve 400 e o erro no cabeçalho 'errors'")
    void cadastroInvalido() {
        // Telefone com letras viola a validação (só dígitos). A versão legada responde 400,
        // sem corpo, e descreve o erro no cabeçalho "errors", em JSON.
        given().contentType(ContentType.JSON)
            .body(dono("Carla", "Invalido", "Rua X, 1", "Sorocaba", "abc"))
        .when().post("/owners")
        .then()
            .statusCode(400)
            .body(emptyString())
            .header("errors", containsString("\"fieldName\":\"telephone\""))
            .header("errors", containsString("\"fieldValue\":\"abc\""));
    }
}

# Relatório da F5: ajuste decidido pelo autor na exclusão de tipo de pet

- Início: 2026-11-09 às 11:17 (a primeira rodada do `verify` começou às 11:17:52; a edição foi feita logo antes, sem registro exato do minuto)
- Fim: 2026-11-09 às 11:29
- Branch: `modernizacao` do `spring-petclinic-rest`, commit `7c0326d` ("F5: ajuste decidido pelo autor na exclusão de tipo de pet (Hibernate 6.6)"), só local, sem push
- JDK: Temurin 21.0.13, só no `JAVA_HOME` do comando, o mesmo do T05

## Pendência P1 da F4 e causa

O teste `shouldDeletePetType` falhava nos perfis `jpa` e `spring-data-jpa` (2 testes), e
`DELETE /api/pettypes/{id}` devolvia 400. O erro era
`org.hibernate.TransientObjectException: persistent instance references an unsaved transient instance of 'org.springframework.samples.petclinic.model.PetType'`,
no auto-flush antes dos `executeUpdate()` de `JpaPetTypeRepositoryImpl.delete` e
`SpringDataPetTypeRepositoryImpl.delete`.

Causa: os dois métodos faziam primeiro `em.remove(petType)`, depois carregavam os pets desse tipo na
sessão do Hibernate e os apagavam com `DELETE` por id. Os pets carregados continuavam gerenciados e
apontando para o tipo já removido. O Hibernate 6.6 (6.6.53, gerenciado pelo Spring Boot 3.5.16) recusa
esse flush; o Hibernate 5 do legado aceitava. Na F4 não havia correção possível sem mudar a lógica do
repositório, o que a regra 1 do steering proíbe, e por isso o problema ficou como pendência.

## Decisão

A correção foi decidida e revisada por mim, o autor, como exceção à regra 1 do steering, limitada ao
método `delete(PetType)` dos dois arquivos. A análise do erro foi feita com apoio de IA (Claude), e a
correção foi aplicada pelo agente (Kiro).

O que mudou nos dois métodos:

1. Os pets deixam de ser carregados na sessão. As visitas e depois os pets do tipo são apagados com dois
   `DELETE` em lote, com o id do tipo passado como parâmetro nomeado (`:petTypeId`), em vez de
   concatenado na consulta.
2. O `em.remove(...)` do tipo foi para o fim do método, na mesma forma, com o `contains` e o `merge`.
3. Saiu o `DELETE` em lote do `PetType` da última linha, que ficou redundante com o `em.remove`.
4. Depois da minha aprovação, saíram os imports sem uso (`Pet`, `Visit` e `List`) e o
   `@SuppressWarnings("unchecked")` do `delete`, que deixaram de ser necessários.

O efeito é o mesmo de antes: somem o tipo, os pets dele e as visitas desses pets. O
`import java.util.ArrayList` do `JpaPetTypeRepositoryImpl` já não era usado no legado e ficou como estava.

## Diff

```diff
--- a/src/main/java/org/springframework/samples/petclinic/repository/jpa/JpaPetTypeRepositoryImpl.java
+++ b/src/main/java/org/springframework/samples/petclinic/repository/jpa/JpaPetTypeRepositoryImpl.java
@@ -18,16 +18,13 @@ package org.springframework.samples.petclinic.repository.jpa;
 
 import java.util.ArrayList;
 import java.util.Collection;
-import java.util.List;
 
 import jakarta.persistence.EntityManager;
 import jakarta.persistence.PersistenceContext;
 
 import org.springframework.context.annotation.Profile;
 import org.springframework.dao.DataAccessException;
-import org.springframework.samples.petclinic.model.Pet;
 import org.springframework.samples.petclinic.model.PetType;
-import org.springframework.samples.petclinic.model.Visit;
 import org.springframework.samples.petclinic.repository.PetTypeRepository;
 import org.springframework.stereotype.Repository;
 
@@ -64,21 +61,17 @@ public class JpaPetTypeRepositoryImpl implements PetTypeRepository {
 
 	}
 
-	@SuppressWarnings("unchecked")
 	@Override
 	public void delete(PetType petType) throws DataAccessException {
-		this.em.remove(this.em.contains(petType) ? petType : this.em.merge(petType));
 		Integer petTypeId = petType.getId();
 		
-		List<Pet> pets = this.em.createQuery("SELECT pet FROM Pet pet WHERE pet.type.id=" + petTypeId).getResultList();
-		for (Pet pet : pets){
-			List<Visit> visits = pet.getVisits();
-			for (Visit visit : visits){
-				this.em.createQuery("DELETE FROM Visit visit WHERE id=" + visit.getId()).executeUpdate();
-			}
-			this.em.createQuery("DELETE FROM Pet pet WHERE id=" + pet.getId()).executeUpdate();
-		}
-		this.em.createQuery("DELETE FROM PetType pettype WHERE id=" + petTypeId).executeUpdate();
+		this.em.createQuery("DELETE FROM Visit visit WHERE visit.pet.id IN (SELECT pet.id FROM Pet pet WHERE pet.type.id = :petTypeId)")
+			.setParameter("petTypeId", petTypeId)
+			.executeUpdate();
+		this.em.createQuery("DELETE FROM Pet pet WHERE pet.type.id = :petTypeId")
+			.setParameter("petTypeId", petTypeId)
+			.executeUpdate();
+		this.em.remove(this.em.contains(petType) ? petType : this.em.merge(petType));
 	}
 
 }
--- a/src/main/java/org/springframework/samples/petclinic/repository/springdatajpa/SpringDataPetTypeRepositoryImpl.java
+++ b/src/main/java/org/springframework/samples/petclinic/repository/springdatajpa/SpringDataPetTypeRepositoryImpl.java
@@ -17,13 +17,10 @@
 package org.springframework.samples.petclinic.repository.springdatajpa;
 
 import org.springframework.context.annotation.Profile;
-import org.springframework.samples.petclinic.model.Pet;
 import org.springframework.samples.petclinic.model.PetType;
-import org.springframework.samples.petclinic.model.Visit;
 
 import jakarta.persistence.EntityManager;
 import jakarta.persistence.PersistenceContext;
-import java.util.List;
 
 /**
  * @author Vitaliy Fedoriv
@@ -36,21 +33,17 @@ public class SpringDataPetTypeRepositoryImpl implements PetTypeRepositoryOverrid
 	@PersistenceContext
     private EntityManager em;
 
-	@SuppressWarnings("unchecked")
 	@Override
 	public void delete(PetType petType) {
-        this.em.remove(this.em.contains(petType) ? petType : this.em.merge(petType));
 		Integer petTypeId = petType.getId();
 		
-		List<Pet> pets = this.em.createQuery("SELECT pet FROM Pet pet WHERE pet.type.id=" + petTypeId).getResultList();
-		for (Pet pet : pets){
-			List<Visit> visits = pet.getVisits();
-			for (Visit visit : visits){
-				this.em.createQuery("DELETE FROM Visit visit WHERE id=" + visit.getId()).executeUpdate();
-			}
-			this.em.createQuery("DELETE FROM Pet pet WHERE id=" + pet.getId()).executeUpdate();
-		}
-		this.em.createQuery("DELETE FROM PetType pettype WHERE id=" + petTypeId).executeUpdate();
+		this.em.createQuery("DELETE FROM Visit visit WHERE visit.pet.id IN (SELECT pet.id FROM Pet pet WHERE pet.type.id = :petTypeId)")
+			.setParameter("petTypeId", petTypeId)
+			.executeUpdate();
+		this.em.createQuery("DELETE FROM Pet pet WHERE pet.type.id = :petTypeId")
+			.setParameter("petTypeId", petTypeId)
+			.executeUpdate();
+        this.em.remove(this.em.contains(petType) ? petType : this.em.merge(petType));
 	}
 
 }
```

## Resultado do `./mvnw clean verify`

| Rodada | Fim | Código | Testes | Linhas | Ramos | Resultado |
|---|---|---|---|---|---|---|
| 1 | 11:18:18 | Correção, ainda com os imports sem uso e o `@SuppressWarnings` | 171, 0 falhas, 0 erros, 0 pulados | 88,52% (1264/1428) | 70,22% (257/366) | `BUILD SUCCESS` |
| 2 | 11:24:08 | Versão do commit, após a limpeza | 171, 0 falhas, 0 erros, 0 pulados | 88,52% (1264/1428) | 70,22% (257/366) | `BUILD SUCCESS` |

Na rodada 2, o `jacoco:check` registrou "All coverage checks have been met" (mínimo do projeto: 70% de
ramos). Na F4 os ramos ficavam em 69,25% por causa dos 2 testes com erro. O log completo da rodada 2
está em `verify.log`. O log da rodada 1 não foi guardado.

Nas classes alteradas, `JpaPetTypeRepositoryImpl` ficou com 16/16 linhas e 3/4 ramos cobertos, e
`SpringDataPetTypeRepositoryImpl` com 10/10 linhas e 1/2 ramos. Em cada uma, o ramo não coberto é um dos
dois lados do `contains ? petType : merge`.

A suíte de caracterização (`kit/testes-caracterizacao`) não foi rodada nesta fase.

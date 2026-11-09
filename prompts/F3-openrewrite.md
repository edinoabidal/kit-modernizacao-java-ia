# F3 — OpenRewrite (receita composta)

Contexto: continuo o TCC. Os testes de caracterização já estão prontos (F2). Agora é a F3: a IA analisa as dependências, eu monto uma receita composta só com receitas prontas do catálogo do OpenRewrite, reviso o dryRun e aplico. O resultado é o commit 1, e o estado depois dele é a referência "só OpenRewrite".

Regras:
- Trabalhe no branch modernizacao do fork; o branch legado não muda.
- Na F3, só o OpenRewrite altera o código. Não corrija nada, mesmo que o build quebre: isso fica para a F4.
- Não instale nada nem crie contas ou tokens sem me perguntar.
- Salve este prompt em kit/prompts/F3-openrewrite.md.
- Se algo falhar, pare, mostre o erro e explique a causa provável.

1. JDK 21: veja se há um Eclipse Temurin 21 disponível. Se não houver, me pergunte antes de baixar. A sugestão é colocá-lo ao lado do JDK 8 e usá-lo só pelo JAVA_HOME dos comandos, sem mudar o sistema.

2. Análise de dependências: a partir do pom.xml, da árvore de dependências do legado (mvnw dependency:tree com o JDK 8) e da medição da linha de base, escreva kit/receita/analise-dependencias.md com uma tabela: dependência, versão atual, o que muda no Java 21 e no Spring Boot 3.5 (javax para jakarta, Springfox para SpringDoc, Spring Security 6, JAXB, MapStruct etc.), qual receita do catálogo deve tratar cada item e o que provavelmente vai sobrar para a F4.

3. Onde obter as receitas: a documentação do OpenRewrite diz que as receitas estão migrando do Maven Central para o Code Genome Project, que exige login. Os binários novos do rewrite-spring ficaram restritos a clientes da Moderne; para uso não comercial, a documentação permite compilar o módulo localmente. Por isso:
   a) descubra no Maven Central (repo1.maven.org, pelos maven-metadata.xml) as versões mais recentes que ficaram lá do rewrite-maven-plugin, do rewrite-spring e do rewrite-migrate-java;
   b) confirme que essas versões têm as receitas org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_5 (do namespace org.openrewrite, não a io.moderne, que é proprietária), org.openrewrite.java.migrate.UpgradeToJava21 e org.openrewrite.java.springdoc.SpringFoxToSpringDoc;
   c) registre as versões escolhidas e a licença de cada artefato, lida do POM dele.
   Se não encontrar no Maven Central versões que funcionem, pare e me explique as alternativas. Não crie conta no Code Genome Project.

4. Crie kit/receita/rewrite.yml com uma receita composta chamada tcc.ModernizacaoPetClinic, que só reúne as três receitas do item 3, na ordem que a documentação recomendar. Justifique a ordem na análise. Nenhuma receita própria em código.

5. dryRun: rode o rewrite-maven-plugin pela linha de comando, sem alterar o pom.xml, com as versões do item 3, apontando para o rewrite.yml do kit (rewrite.configLocation) e com rewrite.activeRecipes=tcc.ModernizacaoPetClinic. Salve o rewrite.patch em evidencias/F3/dryrun.patch e me mostre um resumo: arquivos alterados por tipo de mudança e o que a receita não tocou. Pare e espere eu revisar o patch e aprovar.

6. Depois da minha aprovação, rode o run com o mesmo comando, confira com git diff que só há mudanças da receita e faça o commit 1, com a mensagem "F3: OpenRewrite (receita composta tcc.ModernizacaoPetClinic)". Envie para o fork.

7. T04 (determinismo): crie um worktree temporário a partir do legado, rode o mesmo run e compare o resultado com o commit 1, ignorando a pasta target. O esperado é nenhuma diferença. Salve a comparação em evidencias/T04 e apague o worktree.

8. T05: rode o medir.py com --fase openrewrite e o JDK 21 no commit 1, mesmo que o build falhe. Se o build passar e a API subir, rode também a suíte de caracterização e registre o resultado, sem corrigir nada.

9. Faça o commit da análise, da receita, das evidências e deste prompt no repositório do kit e envie.

No final, mostre as versões e licenças usadas, o comando exato do dryRun e do run, o resumo do que mudou, o resultado do T04 e do T05 e a lista do que ficou quebrado ou pendente para a F4, sem omitir nada.

# F2 — Repositórios públicos e testes de caracterização

Contexto: continuo o TCC de modernização do Spring PetClinic REST. A pasta de trabalho é /home/<usuario>/tcc-modernizacao, com o clone spring-petclinic-rest (branch legado, commit 517a399), a pasta kit (scripts/medir.py), medicoes e evidencias. Nesta etapa (F2) quero os repositórios públicos e a rede de proteção: testes de caracterização da API, que registram o comportamento atual da versão legada para comprovar depois que a versão modernizada se comporta igual.

Regras:
- Não altere o branch legado nem o commit 517a399. Mudanças temporárias só no branch do item 6, que deve ser apagado no final.
- Não instale nada, não crie contas e não publique nada sem me mostrar antes e esperar a minha confirmação.
- Salve este prompt em kit/prompts/F2-testes-caracterizacao.md.
- Se algo falhar, pare, mostre o erro e explique a causa provável.

1. Repositórios no GitHub, os dois públicos:
   a) Código: um fork de spring-petclinic/spring-petclinic-rest na minha conta, com o branch legado (517a399) enviado e definido como branch padrão. Crie também o branch modernizacao a partir do legado; é nele que vão os commits de cada fase.
   b) Kit: um repositório novo, tcc-modernizacao-kit, a partir da pasta kit, com .gitignore para target, __pycache__ e arquivos locais, e licença Apache-2.0, a mesma do PetClinic.
   Se o gh estiver instalado e autenticado, use-o; se não, me passe os passos para eu fazer pelo site. Antes do primeiro push, me mostre a lista de arquivos que vão subir e confirme que não há senhas, tokens ou dados pessoais.

2. Leia na versão legada os controllers e o openapi.yml e liste os endpoints da API com método, rota e o que retornam com os dados iniciais.

3. Crie em kit/testes-caracterizacao um projeto Maven separado com REST Assured e JUnit 5, compatível com Java 8, para rodar igual com o JDK 8 e o JDK 21. Use versões estáveis e registre quais foram. A URL base deve ser configurável (padrão http://localhost:9966/petclinic/api), sem nenhuma dependência do código do PetClinic.

4. Escreva de 5 a 8 testes de caracterização cobrindo consultas e cadastros dos recursos principais, incluindo:
   - a lista de donos e um dono pelo id, com os dados iniciais;
   - a busca de donos pelo sobrenome;
   - o cadastro de um dono novo e a consulta dele em seguida;
   - a atualização de um dono;
   - as listas de veterinários e de tipos de pet;
   - um caso de erro, como um dono inexistente.
   Cada teste confere o código HTTP, o tipo de conteúdo e os campos que importam, com os valores que a versão legada devolve hoje. Não confira ids gerados, datas nem uma ordem que não seja garantida. Os testes de escrita usam dados próprios e não podem afetar os de leitura, em qualquer ordem de execução. Comente cada teste em português e crie kit/testes-caracterizacao/README-testes.md com o comando para rodar e uma tabela com o objetivo de cada teste.

5. T02: suba a versão legada com o JDK 8, como no T01, rode a suíte e salve em evidencias/T02 o log e os relatórios do Surefire. O esperado é 100% de aprovação. Se algum teste falhar, o erro está no teste, não na aplicação: ajuste o teste para registrar o comportamento atual e me diga o que mudou.

6. T03 (teste negativo): crie o branch temporário t03-negativo a partir do legado e altere de propósito uma resposta da API, por exemplo a cidade de um dono nos dados iniciais. Recompile, suba a aplicação, rode a suíte e confirme que ela falha apontando a diferença. Salve a saída em evidencias/T03. Depois volte ao legado, apague o branch e confirme com git status e git rev-parse que o legado continua intacto no 517a399.

7. Faça o commit do projeto de testes, das evidências e deste prompt no repositório do kit e envie, depois da minha confirmação.

No final, mostre os endereços dos dois repositórios, a tabela dos testes, o resultado do T02 e do T03 e qualquer erro, sem omitir nada.

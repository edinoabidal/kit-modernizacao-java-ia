Fase F4 do TCC: completar com você a migração que o OpenRewrite deixou incompleta, seguindo o steering desta pasta (.kiro/steering/modernizacao.md).

Antes de começar, confira e, se algo faltar, pare e me diga:
- no spring-petclinic-rest, o branch modernizacao tem o commit 1 (F3, d0d758d) e a árvore está limpa;
- o T05 foi medido, com os erros agrupados por causa em evidencias/T05;
- o kit tem os commits da F2 e da F3.

Objetivo, com o Temurin 21 no JAVA_HOME (o mesmo usado no T05):
- ./mvnw clean verify passa, com todos os testes do projeto aprovados;
- a aplicação sobe na porta 9966, em /petclinic;
- a suíte de caracterização (kit/testes-caracterizacao, rodada como no T02) passa 100% contra a versão modernizada.

Como trabalhar:
1. Parta dos erros do T05 (evidencias/T05/erros-compilacao-por-causa.md) e da análise da F3 (kit/receita/analise-dependencias.md). O javac parou no limite de 100 erros, então devem aparecer outros depois que esses forem resolvidos.
2. As mudanças da F3 ficam como estão, inclusive as de estilo nos testes, como o getFirst() e o removeFirst(): a regra 6 vale para o que você mudar nesta fase. Se precisar corrigir algo que a F3 fez, registre no relatório como correção da F3.
3. Resolva uma causa de cada vez e compile depois de cada uma.
4. Se uma causa continuar sem solução depois de três tentativas, registre como pendência e siga para a próxima.
5. Não rode o medir.py: a medição é na F6.
6. Faça um único commit, no fim.

Ao terminar:
1. Commit 2 no modernizacao local, sem push, com a mensagem "F4: agente de IA (Kiro com steering)" e o mesmo autor e e-mail do commit 1.
2. Relatório em evidencias/F4/relatorio.md com:
   - as mudanças agrupadas por causa, com os arquivos de cada uma;
   - cada teste do projeto que mudou e o motivo;
   - as dependências trocadas, com as versões e onde você confirmou que existem;
   - as decisões, com o motivo de cada uma, e as pendências;
   - o horário de início e de fim, quantas vezes o build rodou e quantos erros restavam em cada rodada;
   - o resultado final do mvnw verify e da suíte de caracterização.
3. Copie este prompt para kit/prompts/F4-agente.md e o steering para kit/steering/modernizacao.md.
4. Pare antes do commit do kit: vou salvar esta conversa para as evidências.

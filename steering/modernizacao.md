---
inclusion: always
---

# Regras da modernização

Projeto: Spring PetClinic REST, de Java 8 e Spring Boot 2.6 para Java 21 e Spring Boot 3.5. O trabalho é no branch modernizacao. O branch legado (commit 517a399) é a referência e não pode ser alterado.

## Comportamento
1. Não altere regras de negócio, consultas, dados de exemplo nem a lógica de serviços e repositórios. Mude só o necessário para compilar e rodar nas versões novas.
2. O contrato da API é o comportamento que os testes de caracterização registraram na versão legada: rotas, porta 9966, caminho /petclinic/api, códigos de status, corpos de resposta e formato dos erros, inclusive o cabeçalho errors no 400. Não alinhe a API ao api-docs.yml: o generateApis continua false.
3. Com a segurança desligada, que é o padrão do projeto, a API continua aberta, sem login. Com ela ligada, valem a mesma autenticação e as mesmas permissões por papel de antes.
4. A documentação da API passa do Springfox para o springdoc. Recrie no springdoc as informações do ApplicationSwaggerConfig (título, descrição, versão, contato e licença) e mantenha a interface do Swagger acessível. A mudança de endereço da especificação gerada é aceita, mas deve ser registrada.

## Testes
5. Não altere os testes de caracterização (kit/testes-caracterizacao) nem o script de medição (kit/scripts).
6. Nos testes do projeto (src/test), só mudanças mecânicas exigidas pelas versões novas, como imports e APIs renomeadas. Não mude asserções nem valores esperados, e não apague nem desative testes.

## Dependências
7. Prefira as versões gerenciadas pelo Spring Boot 3.5. Para as demais, confirme no Maven Central que o artefato e a versão existem antes de usar. Não adicione dependências desnecessárias.

## Fontes
8. Não consulte o histórico do projeto original depois do 517a399: nada de git log, show, diff ou checkout em origin/* ou em branches além de legado e modernizacao, nem o repositório original ou forks dele na web. A documentação oficial das ferramentas pode ser consultada.

## Ambiente
9. Não faça push nem crie repositórios, contas ou tokens sem o meu pedido explícito, e não instale nada no sistema. O JDK 21 é usado só pelo JAVA_HOME dos comandos.
10. Não grave nos arquivos do projeto ou do kit nomes de usuário, nome da máquina, caminhos pessoais ou dados da empresa.

## Registro
11. Registre cada decisão relevante no relatório da fase, com o motivo. Se algo só puder ser resolvido quebrando uma destas regras, não contorne: pare e registre como pendência.

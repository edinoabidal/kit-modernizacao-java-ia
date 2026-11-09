# T07: medição final

- Data: 2026-11-09 às 11:35:24
- Comando: `python3 kit/scripts/medir.py --projeto spring-petclinic-rest --fase final --java-home <JDK 21>`
- JDK: Temurin 21.0.13, o mesmo do T05 e do T06
- Projeto: commit `7c0326d` (commit 3). O `git status` ficou vazio antes e depois (`arvore_limpa=sim`).

Arquivos:

- `saida-medir.txt`: saída do script.
- `linha-medicoes.csv`: cabeçalho e a linha acrescentada ao `medicoes/medicoes.csv`.
- `medicao-final-20261109-113524/`: saídas brutas do script (log do build, `jacoco.csv`, relatórios
  do `versions-maven-plugin` e `git status`).

## Comparação

Valores corrigidos (errata em `ERRATA.md`, na raiz do kit). A saída original do script, em
`saida-medir.txt` e `linha-medicoes.csv`, foi preservada e mostra os valores antes da correção:
17 dependências desatualizadas, 10 na mesma major e 2 plugins no T07.

| Coluna | Legado (F1) | T05 (só OpenRewrite) | T07 (final) |
|---|---|---|---|
| data_hora | 2026-11-03 17:44:11 | 2026-11-09 10:07:26 | 2026-11-09 11:35:24 |
| commit | 517a399 | d0d758d | 7c0326d |
| java_versao | 1.8.0_504 | 21.0.13 | 21.0.13 |
| maven_versao | 3.6.3 | 3.6.3 | 3.6.3 |
| build_resultado | sucesso | falha_compilacao | sucesso |
| build_codigo_saida | 0 | 1 | 0 |
| build_duracao_s | 30.8 | 76.5 | 28.8 |
| testes_total | 171 | N/D | 171 |
| testes_falhas | 0 | N/D | 0 |
| testes_erros | 0 | N/D | 0 |
| testes_ignorados | 0 | N/D | 0 |
| cobertura_linhas_pct | 88.41 | N/D | 88.52 |
| cobertura_ramos_pct | 71.05 | N/D | 70.22 |
| deps_declaradas | 24 | 26 | 26 |
| deps_desatualizadas | 23 | 22 | 22 |
| deps_desatualizadas_mesma_major | 23 | 11 | 11 |
| plugins_desatualizados | 4 | 2 | 1 |
| parent_atual | 2.6.2 | 3.5.16 | 3.5.16 |
| parent_mais_recente | 4.1.2 | 4.1.2 | 4.1.2 |
| parent_mais_recente_mesma_major | 2.7.18 | 3.5.16 | 3.5.16 |
| arvore_limpa | sim | sim | sim |

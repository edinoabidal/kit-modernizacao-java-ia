# T08: mudanças por fase

- Data: 2026-11-09
- Fonte: `git diff --no-renames --numstat` e `--name-status` entre os commits de cada fase, no
  repositório `spring-petclinic-rest`. Nenhum renomeamento nem arquivo binário aparece nas três fases.
- Categorias: **produção** = `src/main/java`; **testes** = `src/test`; **configuração** = o resto
  (`pom.xml`, `src/main/resources`, `src/main/openapi-templates`, `.github/workflows`).
- Script: `contar-mudancas.py` (uso: `python3 contar-mudancas.py <projeto> <saida.csv>`). A mesma
  tabela está em `mudancas-por-fase.csv` e em `medicoes/mudancas-por-fase.csv`.

## Tabela

| Fase | Commits | Categoria | Alterados | Criados | Apagados | Linhas + | Linhas − | Total de linhas |
|---|---|---|---:|---:|---:|---:|---:|---:|
| F3 (OpenRewrite) | 517a399 → d0d758d | Produção | 41 | 0 | 0 | 163 | 180 | 343 |
| | | Testes | 9 | 0 | 0 | 70 | 66 | 136 |
| | | Configuração | 3 | 0 | 0 | 27 | 16 | 43 |
| | | **Total** | **53** | **0** | **0** | **260** | **262** | **522** |
| F4 (agente de IA) | d0d758d → 07dacc9 | Produção | 5 | 1 | 0 | 47 | 48 | 95 |
| | | Testes | 7 | 0 | 0 | 8 | 1 | 9 |
| | | Configuração | 1 | 1 | 0 | 6 | 2 | 8 |
| | | **Total** | **13** | **2** | **0** | **61** | **51** | **112** |
| F5 (ajuste do autor) | 07dacc9 → 7c0326d | Produção | 2 | 0 | 0 | 14 | 28 | 42 |
| | | Testes | 0 | 0 | 0 | 0 | 0 | 0 |
| | | Configuração | 0 | 0 | 0 | 0 | 0 | 0 |
| | | **Total** | **2** | **0** | **0** | **14** | **28** | **42** |

Arquivos de configuração por fase:

- F3: `pom.xml` (+23 −15), `src/main/resources/application.properties` (+3), `.github/workflows/maven-build.yml` (+1 −1).
- F4: `pom.xml` (+5 −2) e o arquivo criado `src/main/openapi-templates/notNull.mustache` (+1).
- F4, produção: o arquivo criado é `src/main/java/org/springframework/samples/petclinic/util/TrailingSlashMatchConfig.java` (+19).

## Mudanças de estilo dentro da F3

São as mudanças registradas em `kit/receita/analise-dependencias.md` (observação 2), que não são
exigidas pela migração. Linhas contadas no diff da F3 (`git diff -U0`), pelo padrão de cada mudança
(saída em `estilo-f3.txt`):

| Mudança | Receita | Categoria | Linhas + | Linhas − | Total |
|---|---|---|---:|---:|---:|
| `@RequestMapping(method = ...)` → `@GetMapping`, `@PostMapping` etc. | `NoRequestMappingAnnotation` | Produção | 33 | 33 | 66 |
| `@Autowired` tirado dos construtores, com o import | `NoAutowiredOnConstructor` | Produção | 0 | 16 | 16 |
| `get(0)` → `getFirst()` e `remove(0)` → `removeFirst()` | `SequencedCollection` | Testes | 63 | 63 | 126 |
| **Total de estilo** | | | **96** | **112** | **208** |

- Mapeamentos: 33 anotações trocadas em 7 controllers, como na análise. Os controllers importam
  `org.springframework.web.bind.annotation.*`, então não houve linha de import nessa troca.
- `@Autowired`: 8 anotações e 8 imports removidos.
- `getFirst()`/`removeFirst()`: 63 linhas, que batem com a tabela da análise (58 com `getFirst()` e
  5 com `removeFirst()`), cada uma trocando uma linha com `get(0)`/`remove(0)`.

Das 522 linhas da F3, 208 (39,8%) são de estilo e 314 são de migração. Por categoria: em produção,
82 de 343 linhas são de estilo; em testes, 126 de 136; na configuração, nenhuma.

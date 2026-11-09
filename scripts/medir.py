#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================================
# medir.py — Script de medição do TCC (Spring PetClinic REST)
#
# Objetivo: medir SEMPRE do mesmo jeito o projeto em tres momentos:
#   - fase "legado"      (antes de modernizar)
#   - fase "openrewrite" (depois de rodar o OpenRewrite)
#   - fase "final"       (versao final modernizada)
#
# O script NAO altera nenhum arquivo do projeto. Ele:
#   1. roda o build/testes com o Maven Wrapper do proprio projeto (mvnw);
#   2. soma os relatorios de teste do Surefire;
#   3. le a cobertura do JaCoCo do proprio projeto (jacoco.csv);
#   4. consulta dependencias/plugins desatualizados com o versions-maven-plugin
#      chamado pela LINHA DE COMANDO (sem mexer no pom.xml);
#   5. grava uma linha num CSV acumulado e guarda as saidas brutas.
#
# Usa SOMENTE a biblioteca padrao do Python 3 (nada de pip install).
# ============================================================================

import argparse          # para ler os parametros da linha de comando
import csv               # para escrever o medicoes.csv
import os                # para caminhos e variaveis de ambiente
import platform          # para saber se estamos no Windows ou Linux
import re                # para interpretar (regex) a saida do Maven
import shutil            # para copiar arquivos (ex.: jacoco.csv)
import subprocess        # para executar comandos externos (mvnw, git)
import sys               # para encerrar com mensagens de erro
import time              # para medir a duracao do build
import xml.etree.ElementTree as ET  # para ler os XML do Surefire
from datetime import datetime       # para o carimbo de data/hora

# ----------------------------------------------------------------------------
# VERSAO FIXA do versions-maven-plugin.
# Escolhida porque a linha 2.16.x e a ultima que ainda roda com Java 8,
# e tambem funciona com Java 21 e com o Maven 3.6.3 do wrapper do projeto.
# Como o plugin NAO esta declarado no pom, ele e chamado pelo "coordenada completa".
# ----------------------------------------------------------------------------
VERSIONS_PLUGIN = "org.codehaus.mojo:versions-maven-plugin:2.16.2"

# Regex que dizem ao versions-maven-plugin quais versoes IGNORAR.
# Cada item casa a string inteira da versao. Ignoramos pre-releases:
# SNAPSHOT, milestone (-M1), release candidate (-RC1 / -rc), alpha, beta e -CR.
IGNORAR_VERSOES = (
    r".*-SNAPSHOT,"
    r".*-M\d+,"
    r".*-RC\d*,"
    r".*-rc\d*,"
    r".*[-\.](?:alpha|beta|ALPHA|BETA|Alpha|Beta)[-\.\d]*.*,"
    r".*-CR\d+"
)

# Valor usado quando nao conseguimos medir alguma coisa.
ND = "N/D"

# Ordem EXATA das colunas do CSV (nao mude sem querer, para nao quebrar o historico).
COLUNAS_CSV = [
    "data_hora", "fase", "commit", "java_versao", "maven_versao",
    "build_resultado", "build_codigo_saida", "build_duracao_s",
    "testes_total", "testes_falhas", "testes_erros", "testes_ignorados",
    "cobertura_linhas_pct", "cobertura_ramos_pct",
    "deps_declaradas", "deps_desatualizadas", "deps_desatualizadas_mesma_major",
    "plugins_desatualizados",
    "parent_atual", "parent_mais_recente", "parent_mais_recente_mesma_major",
    "arvore_limpa",
]


# ============================================================================
# FUNCOES AUXILIARES
# ============================================================================

def agora_carimbo():
    """Devolve a data/hora atual em dois formatos: um legivel e um para nome de pasta."""
    agora = datetime.now()
    legivel = agora.strftime("%Y-%m-%d %H:%M:%S")      # ex.: 2026-10-27 17:45:00
    para_pasta = agora.strftime("%Y%m%d-%H%M%S")       # ex.: 20261027-174500
    return legivel, para_pasta


def nome_do_mvnw():
    """Escolhe o wrapper certo conforme o sistema: mvnw.cmd no Windows, mvnw no resto."""
    if platform.system() == "Windows":
        return "mvnw.cmd"
    return "./mvnw"


def rodar_comando(comando, cwd, java_home, log_path=None, timeout=None):
    """
    Executa um comando externo dentro da pasta 'cwd'.
    - Ajusta JAVA_HOME e PATH SOMENTE para este comando (nao mexe no sistema).
    - Se log_path for dado, grava toda a saida (stdout+stderr) nesse arquivo.
    - Devolve (codigo_de_saida, texto_da_saida).
    """
    # Copiamos o ambiente atual e sobrescrevemos o JAVA_HOME so aqui.
    ambiente = os.environ.copy()
    ambiente["JAVA_HOME"] = java_home
    # Colocamos o bin do JDK na frente do PATH para garantir que seja usado.
    sep = ";" if platform.system() == "Windows" else ":"
    ambiente["PATH"] = os.path.join(java_home, "bin") + sep + ambiente.get("PATH", "")

    try:
        processo = subprocess.run(
            comando,
            cwd=cwd,                 # pasta onde o comando roda (o projeto)
            env=ambiente,            # ambiente com o JAVA_HOME desta medicao
            stdout=subprocess.PIPE,  # captura a saida padrao
            stderr=subprocess.STDOUT,  # junta o erro na mesma saida
            universal_newlines=True,   # trata a saida como texto
            timeout=timeout,
        )
        saida = processo.stdout or ""
        codigo = processo.returncode
    except subprocess.TimeoutExpired as e:
        # Se estourar o tempo, registramos o que veio ate agora.
        saida = (e.stdout or "") if isinstance(e.stdout, str) else ""
        codigo = -1
    except FileNotFoundError as e:
        # Ex.: o mvnw nao existe/nao e executavel.
        saida = "ERRO ao executar comando: %s" % e
        codigo = -1

    # Se pediram, salvamos a saida bruta em arquivo (evidencia).
    if log_path:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(saida)

    return codigo, saida


def ler_git(projeto, args):
    """Roda 'git' no projeto e devolve a saida como texto (ou string vazia em caso de erro)."""
    try:
        processo = subprocess.run(
            ["git"] + args,
            cwd=projeto,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        return processo.stdout.strip()
    except Exception:
        return ""


def detectar_versao_java(java_home):
    """Roda 'java -version' do JDK informado e devolve a string de versao (ex.: 1.8.0_504)."""
    java_bin = os.path.join(java_home, "bin", "java")
    try:
        processo = subprocess.run(
            [java_bin, "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        texto = processo.stdout
        # A versao aparece entre aspas na primeira linha, ex.: version "1.8.0_504"
        m = re.search(r'version "([^"]+)"', texto)
        if m:
            return m.group(1)
        return texto.strip().splitlines()[0] if texto.strip() else ND
    except Exception:
        return ND


def detectar_versao_maven(projeto, java_home):
    """Roda 'mvnw -version' e devolve a versao do Maven que o wrapper usa (ex.: 3.6.3)."""
    codigo, saida = rodar_comando([nome_do_mvnw(), "-version"], projeto, java_home)
    m = re.search(r"Apache Maven ([\d.]+)", saida)
    if m:
        return m.group(1)
    return ND


# ============================================================================
# CLASSIFICACAO DO RESULTADO DO BUILD
# ============================================================================

def classificar_build(codigo_saida, log_texto):
    """
    Olha o codigo de saida e o log para dizer que tipo de resultado tivemos:
      - "sucesso"                 -> BUILD SUCCESS
      - "falha_compilacao"        -> erro de compilacao
      - "falha_testes"            -> testes falharam/deram erro
      - "falha_cobertura"         -> so a verificacao de cobertura (jacoco:check) falhou
      - "outra_falha"             -> qualquer outra coisa
    A ordem das verificacoes importa: checamos as causas mais especificas primeiro.
    """
    if "BUILD SUCCESS" in log_texto and codigo_saida == 0:
        return "sucesso"

    # Falha de compilacao: o maven-compiler-plugin reclama.
    if re.search(r"Failed to execute goal.*maven-compiler-plugin.*:(compile|testCompile)", log_texto) \
       or "COMPILATION ERROR" in log_texto:
        return "falha_compilacao"

    # Falha SO na verificacao de cobertura do projeto (jacoco:check).
    # Sinal tipico: a regra do JaCoCo foi violada (coverage ratio ... is below ...).
    if re.search(r"jacoco-maven-plugin.*:check", log_texto) and \
       re.search(r"(Coverage checks have not been met|coverage ratio|is below [0-9.]+)", log_texto):
        return "falha_cobertura"

    # Falha de testes: o surefire reclama de falhas/erros nos testes.
    if re.search(r"Failed to execute goal.*maven-surefire-plugin", log_texto) \
       or "There are test failures" in log_texto \
       or re.search(r"BUILD FAILURE", log_texto) and re.search(r"Tests run:.*Failures: [1-9]", log_texto):
        return "falha_testes"

    # Se chegou aqui mas houve BUILD FAILURE, e "outra falha".
    if "BUILD FAILURE" in log_texto or codigo_saida != 0:
        return "outra_falha"

    return "outra_falha"


# ============================================================================
# SOMA DOS RELATORIOS DO SUREFIRE (target/surefire-reports/TEST-*.xml)
# ============================================================================

def somar_surefire(projeto, apos_timestamp=None):
    """
    Le todos os arquivos TEST-*.xml do Surefire e soma:
      total de testes, falhas, erros e ignorados (skipped).
    Devolve um dicionario. Se a pasta nao existir, devolve N/D em tudo.

    'apos_timestamp' (opcional): se informado, SO conta relatorios cujo arquivo foi
    modificado DEPOIS desse instante. Isso evita contar relatorios ANTIGOS de uma
    medicao anterior quando o build atual falhou antes de gerar relatorios novos.
    """
    pasta = os.path.join(projeto, "target", "surefire-reports")
    if not os.path.isdir(pasta):
        return {"total": ND, "falhas": ND, "erros": ND, "ignorados": ND}

    total = falhas = erros = ignorados = 0
    achou_algum = False
    for nome in os.listdir(pasta):
        # Os relatorios por classe tem o padrao TEST-<classe>.xml
        if nome.startswith("TEST-") and nome.endswith(".xml"):
            caminho = os.path.join(pasta, nome)
            # Se pediram, ignoramos relatorios velhos (de medicoes anteriores).
            if apos_timestamp is not None and os.path.getmtime(caminho) < apos_timestamp:
                continue
            try:
                raiz = ET.parse(caminho).getroot()  # tag <testsuite ...>
                total += int(raiz.get("tests", 0))
                falhas += int(raiz.get("failures", 0))
                erros += int(raiz.get("errors", 0))
                ignorados += int(raiz.get("skipped", 0))
                achou_algum = True
            except Exception:
                # Se um XML estiver corrompido, ignoramos so ele.
                continue

    if not achou_algum:
        return {"total": ND, "falhas": ND, "erros": ND, "ignorados": ND}
    return {"total": total, "falhas": falhas, "erros": erros, "ignorados": ignorados}


# ============================================================================
# COBERTURA DO JACOCO (target/site/jacoco/jacoco.csv)
# ============================================================================

def ler_cobertura(projeto, apos_timestamp=None):
    """
    Le o jacoco.csv gerado pelo proprio projeto e calcula a cobertura do projeto inteiro:
      - linhas  = LINE_COVERED  / (LINE_MISSED  + LINE_COVERED)
      - ramos   = BRANCH_COVERED/ (BRANCH_MISSED+ BRANCH_COVERED)
    Devolve (linhas_pct, ramos_pct, motivo). Se nao existir, devolve (N/D, N/D, motivo).
    IMPORTANTE: nao geramos cobertura por nenhum outro caminho — so lemos este arquivo.

    'apos_timestamp' (opcional): se informado e o arquivo for ANTERIOR a esse instante,
    tratamos como inexistente (relatorio velho de outra medicao) e devolvemos N/D.
    """
    caminho = os.path.join(projeto, "target", "site", "jacoco", "jacoco.csv")
    if not os.path.isfile(caminho):
        return ND, ND, "jacoco.csv nao encontrado (relatorio do JaCoCo nao foi gerado)"
    if apos_timestamp is not None and os.path.getmtime(caminho) < apos_timestamp:
        return ND, ND, "jacoco.csv e de uma medicao anterior (build atual nao o gerou)"

    linha_miss = linha_cov = ramo_miss = ramo_cov = 0
    try:
        with open(caminho, newline="", encoding="utf-8") as f:
            leitor = csv.DictReader(f)  # usa o cabecalho do CSV
            for linha in leitor:
                linha_miss += int(linha["LINE_MISSED"])
                linha_cov += int(linha["LINE_COVERED"])
                ramo_miss += int(linha["BRANCH_MISSED"])
                ramo_cov += int(linha["BRANCH_COVERED"])
    except Exception as e:
        return ND, ND, "erro ao ler jacoco.csv: %s" % e

    total_linhas = linha_miss + linha_cov
    total_ramos = ramo_miss + ramo_cov
    # Calculamos a porcentagem com 2 casas; evitamos divisao por zero.
    linhas_pct = round(linha_cov / total_linhas * 100, 2) if total_linhas > 0 else ND
    ramos_pct = round(ramo_cov / total_ramos * 100, 2) if total_ramos > 0 else ND
    return linhas_pct, ramos_pct, "ok"


# ============================================================================
# CONTAGEM DE DEPENDENCIAS DECLARADAS NO POM
# ============================================================================

def contar_deps_declaradas(projeto):
    """
    Conta quantas <dependency> existem na secao <dependencies> de nivel raiz do pom.xml.
    Apenas LEITURA do pom (nao editamos nada).
    Usa o parser de XML da biblioteca padrao, ignorando o namespace do Maven.
    """
    caminho = os.path.join(projeto, "pom.xml")
    if not os.path.isfile(caminho):
        return ND
    try:
        arvore = ET.parse(caminho)
        raiz = arvore.getroot()

        # O pom do Maven usa namespace; criamos uma funcao para remover o prefixo {..}.
        def tag_local(elem):
            return elem.tag.split("}")[-1]

        # Procuramos a <dependencies> que e filha direta do <project> (nao a de dependencyManagement).
        for filho in raiz:
            if tag_local(filho) == "dependencies":
                deps = [d for d in filho if tag_local(d) == "dependency"]
                return len(deps)
        return 0
    except Exception:
        return ND


# ============================================================================
# PARSING DAS SAIDAS DO versions-maven-plugin
# ============================================================================

def _versions_rodou_ok(saida):
    """Diz se a execucao de um goal do versions-maven-plugin terminou bem (BUILD SUCCESS)."""
    return bool(saida) and "BUILD SUCCESS" in saida


def _juntar_linhas_quebradas(saida):
    """
    Junta as entradas que o versions-maven-plugin quebra em duas linhas.
    Quando o 'grupo:artefato' e longo, o plugin escreve o nome numa linha e as
    versoes na seguinte:
      "[INFO]   com.fasterxml.jackson.datatype:jackson-datatype-jsr310 ..."
      "[INFO]                                                  2.21.4 -> 2.23.0"
    Esta funcao junta as duas numa linha so:
      "[INFO]   com.fasterxml.jackson.datatype:jackson-datatype-jsr310 ... 2.21.4 -> 2.23.0"
    As outras linhas ficam como estao.
    """
    nome_sem_versao = re.compile(r"^\[INFO\]\s+\S+:\S+\s+\.+\s*$")
    continuacao = re.compile(r"^\[INFO\]\s+(\S+\s+->\s+\S+.*)$")
    linhas = saida.splitlines()
    resultado = []
    i = 0
    while i < len(linhas):
        linha = linhas[i]
        if nome_sem_versao.match(linha) and i + 1 < len(linhas):
            m = continuacao.match(linhas[i + 1])
            if m:
                resultado.append(linha.rstrip() + " " + m.group(1))
                i += 2
                continue
        resultado.append(linha)
        i += 1
    return "\n".join(resultado)


def contar_deps_desatualizadas(saida):
    """
    Conta dependencias desatualizadas na saida do display-dependency-updates.
    Contamos as linhas que tem 'grupo:artefato ... versao_atual -> versao_nova',
    depois de juntar as entradas que o plugin quebra em duas linhas
    (ver _juntar_linhas_quebradas).
    Se o comando nem rodou direito (ex.: Java invalido), devolve N/D.
    """
    if not _versions_rodou_ok(saida):
        return ND
    saida = _juntar_linhas_quebradas(saida)
    # Ex.: "[INFO]   com.fasterxml.jackson.core:jackson-core ... 2.13.1 -> 2.22.4"
    # Exigimos ao menos um ':' (grupo:artefato) antes dos pontinhos e a seta '->'.
    padrao = re.compile(r"^\[INFO\]\s+\S+:\S+\s+\.+\s+\S+\s+->\s+\S+")
    artefatos = set()
    for linha in saida.splitlines():
        if padrao.search(linha):
            # pega o 'grupo:artefato' (primeiro token depois de [INFO])
            m = re.search(r"^\[INFO\]\s+(\S+:\S+)\s", linha)
            if m:
                artefatos.add(m.group(1))
    return len(artefatos)


def contar_plugins_desatualizados(saida):
    """
    Conta plugins desatualizados na saida do display-plugin-updates.

    Contamos os plugins UNICOS (groupId:artifactId) que aparecem em QUALQUER bloco
    de atualizacao, sem repetir o mesmo plugin:
      - "The following plugin updates are available:"            (atualizacoes diretas)
      - "Require Maven X.Y.Z to use the following plugin updates:" (exigem um Maven mais novo)
    Isso e importante porque a modernizacao pode mudar a versao do Maven exigida; contar
    todos os blocos deixa as fases comparaveis.
    Os blocos "Require Maven ..." tambem listam versoes ANTERIORES a usada
    (ex.: "0.8.16 -> 0.8.2"). So contamos a linha quando a versao nova e MAIOR que a atual.

    Devolve o numero de plugins unicos. Se o comando nem rodou direito, devolve N/D.
    """
    if not _versions_rodou_ok(saida):
        return ND
    plugins = _coletar_plugins_desatualizados(saida)
    return len(plugins)


def _versao_maior(nova, atual):
    """
    Diz se a versao 'nova' e maior que a 'atual', comparando os numeros na ordem
    (ex.: "0.8.16" > "0.8.2"; "0.6.3.201306030806" < "0.8.16").
    Partes que nao sao numeros (ex.: "RELEASE") sao ignoradas na comparacao.
    """
    def numeros(versao):
        return [int(n) for n in re.findall(r"\d+", versao)]
    a, b = numeros(nova), numeros(atual)
    tamanho = max(len(a), len(b))
    a += [0] * (tamanho - len(a))
    b += [0] * (tamanho - len(b))
    return a > b


def _coletar_plugins_desatualizados(saida):
    """
    Funcao auxiliar: devolve o CONJUNTO (set) de 'groupId:artifactId' de plugins
    desatualizados encontrados em qualquer bloco da saida do display-plugin-updates.
    Separada para podermos tambem LISTAR os plugins (nao so conta-los).
    """
    plugins = set()
    if not saida:
        return plugins
    saida = _juntar_linhas_quebradas(saida)

    # Cabecalhos que iniciam um bloco de atualizacao de plugins.
    inicio_bloco = re.compile(
        r"(The following plugin updates are available"
        r"|Require Maven [\d.]+ to use the following plugin updates)"
    )
    dentro = False
    for linha in saida.splitlines():
        if inicio_bloco.search(linha):
            dentro = True       # entramos (ou reentramos) num bloco de plugins
            continue
        if not dentro:
            continue
        # Dentro de um bloco: tentamos casar uma linha "grupo:artefato ... atual -> nova".
        m = re.search(r"^\[INFO\]\s+(\S+:\S+)\s+\.+\s+(\S+)\s+->\s+(\S+)", linha)
        if m:
            if _versao_maior(m.group(3), m.group(2)):
                plugins.add(m.group(1))
            continue
        # Se a linha nao e de plugin e tambem nao e um novo cabecalho de bloco,
        # consideramos que o bloco atual terminou (ex.: WARNING/ERROR/BUILD/linha vazia).
        # Nao damos 'break': pode haver outros blocos "Require Maven ..." mais adiante.
        if re.search(r"^\[(WARNING|ERROR)\]", linha) or "BUILD SUCCESS" in linha \
           or "BUILD FAILURE" in linha or linha.strip() == "[INFO]" or linha.strip() == "":
            dentro = False
    return plugins


def ler_parent_updates(saida):
    """
    Le a saida do display-parent-updates e devolve (versao_atual, versao_mais_recente).
    Se nao houver versao mais nova (ou nao der para ler), devolve o que for possivel.
    """
    atual = ND
    recente = ND
    if not saida:
        return atual, recente
    # Ex.: "spring-boot-starter-parent  2.6.2 -> 4.1.2"
    m = re.search(r"([\w\.\-]+:[\w\.\-]+)\s+([\w\.\-]+)\s+->\s+([\w\.\-]+)", saida)
    if m:
        atual = m.group(2)
        recente = m.group(3)
        return atual, recente
    # Se o plugin disser que ja esta atualizado, tentamos achar a versao atual.
    if re.search(r"is the latest version|No newer version", saida, re.IGNORECASE):
        return atual, recente
    return atual, recente


# ============================================================================
# FUNCAO PRINCIPAL
# ============================================================================

def main():
    # ---- 1) Ler os parametros da linha de comando -------------------------
    parser = argparse.ArgumentParser(
        description="Mede o projeto Spring PetClinic REST (build, testes, cobertura, dependencias)."
    )
    parser.add_argument("--projeto", required=True,
                        help="Caminho do repositorio spring-petclinic-rest.")
    parser.add_argument("--fase", required=True, choices=["legado", "openrewrite", "final"],
                        help="Rotulo da medicao: legado, openrewrite ou final.")
    parser.add_argument("--java-home", required=True, dest="java_home",
                        help="Caminho do JDK a usar NESTA medicao (vira JAVA_HOME so nos comandos).")
    parser.add_argument("--saida", default=None,
                        help="Pasta de saida das medicoes (padrao: 'medicoes' ao lado do kit).")
    args = parser.parse_args()

    # Normalizamos caminhos para absoluto (fica mais seguro).
    projeto = os.path.abspath(args.projeto)
    java_home = os.path.abspath(args.java_home)

    # Pasta de saida padrao: <pai-do-kit>/medicoes
    if args.saida:
        saida_base = os.path.abspath(args.saida)
    else:
        # Este arquivo esta em kit/scripts/medir.py; subimos 3 niveis ate a pasta tcc,
        # e colocamos 'medicoes' ali (ao lado do kit).
        pasta_kit = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../kit
        pasta_tcc = os.path.dirname(pasta_kit)                                   # .../tcc-modernizacao
        saida_base = os.path.join(pasta_tcc, "medicoes")

    # ---- Validacoes basicas ----------------------------------------------
    if not os.path.isdir(projeto):
        print("ERRO: pasta do projeto nao existe: %s" % projeto)
        sys.exit(1)
    mvnw_arquivo = "mvnw.cmd" if platform.system() == "Windows" else "mvnw"
    if not os.path.isfile(os.path.join(projeto, mvnw_arquivo)):
        print("ERRO: nao achei o Maven Wrapper (%s) em %s" % (mvnw_arquivo, projeto))
        sys.exit(1)
    if not os.path.isdir(java_home):
        # NAO abortamos: um JAVA_HOME invalido e justamente um dos casos de "falha"
        # que o script precisa tolerar. Avisamos e seguimos; os comandos Maven vao
        # falhar e o resultado sera registrado como falha/N/D, sem travar o script.
        print("AVISO: JAVA_HOME informado nao existe: %s" % java_home)
        print("       Prosseguindo mesmo assim; a medicao deve registrar falha/N/D.")

    # ---- Preparar pastas de saida ----------------------------------------
    data_legivel, data_pasta = agora_carimbo()
    os.makedirs(saida_base, exist_ok=True)
    pasta_bruta = os.path.join(saida_base, "%s-%s" % (args.fase, data_pasta))
    os.makedirs(pasta_bruta, exist_ok=True)

    print("=" * 70)
    print("Medicao: fase=%s" % args.fase)
    print("Projeto: %s" % projeto)
    print("JAVA_HOME: %s" % java_home)
    print("Saida bruta: %s" % pasta_bruta)
    print("=" * 70)

    # ---- 2) Dados do ambiente --------------------------------------------
    commit = ler_git(projeto, ["rev-parse", "--short", "HEAD"]) or ND
    java_versao = detectar_versao_java(java_home)
    maven_versao = detectar_versao_maven(projeto, java_home)

    # ---- 3) git status ANTES da medicao (evidencia de que nada mudou) -----
    git_antes = ler_git(projeto, ["status", "--porcelain"])
    with open(os.path.join(pasta_bruta, "git-status-antes.txt"), "w", encoding="utf-8") as f:
        f.write(git_antes + "\n")

    # ---- 4) BUILD: clean verify em modo batch ----------------------------
    print(">> Rodando build (clean verify)...")
    log_build = os.path.join(pasta_bruta, "build.log")
    inicio = time.time()
    codigo_build, saida_build = rodar_comando(
        [nome_do_mvnw(), "-B", "clean", "verify"],
        projeto, java_home, log_path=log_build,
    )
    duracao = round(time.time() - inicio, 1)
    build_resultado = classificar_build(codigo_build, saida_build)
    # Referencia de tempo para aceitar so relatorios gerados por ESTE build.
    # Tiramos 1 segundo por seguranca (o mtime tem resolucao de segundos).
    ref_relatorios = inicio - 1
    print("   resultado=%s  codigo=%s  duracao=%ss" % (build_resultado, codigo_build, duracao))

    # ---- 5) Testes: somar relatorios do Surefire -------------------------
    # Passamos 'inicio' para NAO contar relatorios antigos de outra medicao:
    # so valem relatorios gerados depois que este build comecou.
    testes = somar_surefire(projeto, apos_timestamp=ref_relatorios)
    print("   testes: total=%s falhas=%s erros=%s ignorados=%s"
          % (testes["total"], testes["falhas"], testes["erros"], testes["ignorados"]))

    # ---- 6) Cobertura: ler jacoco.csv ------------------------------------
    cob_linhas, cob_ramos, cob_motivo = ler_cobertura(projeto, apos_timestamp=ref_relatorios)
    print("   cobertura: linhas=%s%% ramos=%s%% (%s)" % (cob_linhas, cob_ramos, cob_motivo))
    # Guardamos uma copia do jacoco.csv como evidencia (se for desta execucao).
    jacoco_origem = os.path.join(projeto, "target", "site", "jacoco", "jacoco.csv")
    if os.path.isfile(jacoco_origem) and os.path.getmtime(jacoco_origem) >= ref_relatorios:
        shutil.copy(jacoco_origem, os.path.join(pasta_bruta, "jacoco.csv"))

    # ---- 7) Dependencias/plugins/parent via versions-maven-plugin --------
    # Mesmo que o build tenha falhado, tentamos medir isto (nao depende do build).
    print(">> Consultando dependencias/plugins desatualizados...")
    deps_declaradas = contar_deps_declaradas(projeto)

    # display-dependency-updates (com processDependencyManagement=false)
    _, saida_dep = rodar_comando(
        [nome_do_mvnw(), "-B", "%s:display-dependency-updates" % VERSIONS_PLUGIN,
         "-DprocessDependencyManagement=false",
         "-Dmaven.version.ignore=%s" % IGNORAR_VERSOES],
        projeto, java_home,
        log_path=os.path.join(pasta_bruta, "versions-dependency-updates.log"),
    )
    deps_desatualizadas = contar_deps_desatualizadas(saida_dep)

    # display-dependency-updates com allowMajorUpdates=false:
    # conta SO as dependencias que tem atualizacao DENTRO da mesma versao major
    # (ex.: 2.6.2 -> 2.7.18 conta; 2.6.2 -> 4.x nao conta).
    _, saida_dep_major = rodar_comando(
        [nome_do_mvnw(), "-B", "%s:display-dependency-updates" % VERSIONS_PLUGIN,
         "-DprocessDependencyManagement=false", "-DallowMajorUpdates=false",
         "-Dmaven.version.ignore=%s" % IGNORAR_VERSOES],
        projeto, java_home,
        log_path=os.path.join(pasta_bruta, "versions-dependency-updates-mesma-major.log"),
    )
    deps_desatualizadas_mesma_major = contar_deps_desatualizadas(saida_dep_major)

    # display-plugin-updates
    _, saida_plug = rodar_comando(
        [nome_do_mvnw(), "-B", "%s:display-plugin-updates" % VERSIONS_PLUGIN,
         "-Dmaven.version.ignore=%s" % IGNORAR_VERSOES],
        projeto, java_home,
        log_path=os.path.join(pasta_bruta, "versions-plugin-updates.log"),
    )
    plugins_desatualizados = contar_plugins_desatualizados(saida_plug)

    # display-parent-updates
    _, saida_parent = rodar_comando(
        [nome_do_mvnw(), "-B", "%s:display-parent-updates" % VERSIONS_PLUGIN,
         "-Dmaven.version.ignore=%s" % IGNORAR_VERSOES],
        projeto, java_home,
        log_path=os.path.join(pasta_bruta, "versions-parent-updates.log"),
    )
    parent_atual, parent_recente = ler_parent_updates(saida_parent)

    # display-parent-updates com allowMajorUpdates=false:
    # pega a versao mais recente do parent DENTRO da mesma major (ex.: 2.6.2 -> 2.7.18).
    _, saida_parent_major = rodar_comando(
        [nome_do_mvnw(), "-B", "%s:display-parent-updates" % VERSIONS_PLUGIN,
         "-DallowMajorUpdates=false",
         "-Dmaven.version.ignore=%s" % IGNORAR_VERSOES],
        projeto, java_home,
        log_path=os.path.join(pasta_bruta, "versions-parent-updates-mesma-major.log"),
    )
    _, parent_recente_mesma_major = ler_parent_updates(saida_parent_major)
    # Se nao houver atualizacao na mesma major, a "mais recente mesma major" e a propria atual.
    if parent_recente_mesma_major == ND and parent_atual != ND:
        parent_recente_mesma_major = parent_atual
    print("   deps_declaradas=%s desatualizadas=%s (mesma_major=%s) plugins_desatualizados=%s"
          % (deps_declaradas, deps_desatualizadas, deps_desatualizadas_mesma_major,
             plugins_desatualizados))
    print("   parent: atual=%s mais_recente=%s mais_recente_mesma_major=%s"
          % (parent_atual, parent_recente, parent_recente_mesma_major))

    # ---- 8) git status DEPOIS da medicao ---------------------------------
    git_depois = ler_git(projeto, ["status", "--porcelain"])
    with open(os.path.join(pasta_bruta, "git-status-depois.txt"), "w", encoding="utf-8") as f:
        f.write(git_depois + "\n")
    # "arvore_limpa" = sim se nada versionado mudou depois da medicao.
    arvore_limpa = "sim" if git_depois.strip() == "" else "nao"

    # ---- 9) Montar a linha e gravar no CSV acumulado ---------------------
    linha = {
        "data_hora": data_legivel,
        "fase": args.fase,
        "commit": commit,
        "java_versao": java_versao,
        "maven_versao": maven_versao,
        "build_resultado": build_resultado,
        "build_codigo_saida": codigo_build,
        "build_duracao_s": duracao,
        "testes_total": testes["total"],
        "testes_falhas": testes["falhas"],
        "testes_erros": testes["erros"],
        "testes_ignorados": testes["ignorados"],
        "cobertura_linhas_pct": cob_linhas,
        "cobertura_ramos_pct": cob_ramos,
        "deps_declaradas": deps_declaradas,
        "deps_desatualizadas": deps_desatualizadas,
        "deps_desatualizadas_mesma_major": deps_desatualizadas_mesma_major,
        "plugins_desatualizados": plugins_desatualizados,
        "parent_atual": parent_atual,
        "parent_mais_recente": parent_recente,
        "parent_mais_recente_mesma_major": parent_recente_mesma_major,
        "arvore_limpa": arvore_limpa,
    }

    csv_path = os.path.join(saida_base, "medicoes.csv")
    # Se o CSV ainda nao existe, escrevemos o cabecalho na primeira vez.
    precisa_cabecalho = not os.path.isfile(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=COLUNAS_CSV)
        if precisa_cabecalho:
            escritor.writeheader()
        escritor.writerow(linha)

    # ---- 10) Resumo final na tela ----------------------------------------
    print("=" * 70)
    print("RESUMO DA MEDICAO (fase=%s)" % args.fase)
    for coluna in COLUNAS_CSV:
        print("  %-24s = %s" % (coluna, linha[coluna]))
    print("-" * 70)
    print("Linha adicionada em: %s" % csv_path)
    print("Saidas brutas em:    %s" % pasta_bruta)
    if build_resultado != "sucesso":
        print("AVISO: o build NAO foi 'sucesso' (%s). As medicoes possiveis foram registradas;"
              " o que nao deu para medir ficou como N/D." % build_resultado)
    print("=" * 70)

    # O script sempre sai com codigo 0 (uma falha de build nao interrompe a medicao).
    sys.exit(0)


if __name__ == "__main__":
    main()

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import BadRequest, RequestEntityTooLarge

import ml_clas_sk
import ml_reg_sk
import configparser
import json
import os


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024


def carregar_configuracoes():
    caminho = os.path.join(app.root_path, "CONFIG.TXT")
    if not os.path.exists(caminho):
        raise BadRequest("Arquivo CONFIG.TXT não encontrado.")

    try:
        conteudo = open(caminho, "r", encoding="utf-8-sig").read()
        if conteudo.strip().startswith("{"):
            dados = json.loads(conteudo)
            return {
                chave.lower(): normalizar_parametros({
                    parametro.lower(): converter_valor_config(valor)
                    for parametro, valor in parametros.items()
                })
                for chave, parametros in dados.items()
            }

        config = configparser.ConfigParser()
        config.read_string(conteudo)
        return {
            secao.lower(): normalizar_parametros({
                chave.lower(): converter_valor_config(valor)
                for chave, valor in config.items(secao)
            })
            for secao in config.sections()
        }
    except (json.JSONDecodeError, configparser.Error, OSError) as erro:
        raise BadRequest(f"Não foi possível ler CONFIG.TXT: {erro}") from erro


def converter_valor_config(valor):
    if isinstance(valor, (dict, list, bool, int, float)):
        return valor
    texto = str(valor).strip()
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        return texto


def normalizar_parametros(parametros):
    aliases = {
        "c": "C",
        "kernel": "kernel",
        "gamma": "gamma",
        "n_estimators": "n_estimators",
        "criterion": "criterion",
        "random_state": "random_state",
        "hidden_layer_sizes": "hidden_layer_sizes",
        "activation": "activation",
        "solver": "solver",
        "alpha": "alpha",
        "max_iter": "max_iter",
    }
    return {
        aliases.get(chave, chave): valor
        for chave, valor in parametros.items()
    }


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/style.css")
def style():
    return send_from_directory(".", "style.css", mimetype="text/css")


@app.route("/script.js")
def script():
    return send_from_directory(".", "script.js", mimetype="text/javascript")


@app.route("/api/analisar", methods=["POST"])
def analisar():
    arquivo = request.files.get("arquivo")
    metodo = request.form.get("metodo")
    modelo = request.form.get("modelo") or None
    usar_padrao = request.form.get("padrao", "true").lower() == "true"
    test_size = int(request.form.get("test_size", 20)) / 100

    if arquivo is None or not arquivo.filename:
        raise BadRequest("Selecione um arquivo CSV ou XLSX.")
    if metodo not in ("classificacao", "regressao"):
        raise BadRequest("Selecione um método de análise.")
    if modelo is not None and modelo not in ("mlp", "svc", "random_forest"):
        raise BadRequest("Selecione um modelo válido.")
    if metodo == "classificacao" and modelo == "mlp":
        raise BadRequest("Selecione um modelo válido para classificação.")
    if metodo == "regressao" and modelo == "svc":
        raise BadRequest("Selecione um modelo válido para regressão.")
    if not arquivo.filename.lower().endswith((".csv", ".xlsx")):
        raise BadRequest("Formato não suportado. Use CSV ou XLSX.")
    if test_size < 0.1 or test_size > 0.9:
        raise BadRequest("Porcentagem de teste inválida.")

    try:
        configuracoes = None if usar_padrao else carregar_configuracoes()
        if metodo == "classificacao":
            resultado = ml_clas_sk.executar(arquivo, test_size, modelo, configuracoes)
        else:
            resultado = ml_reg_sk.executar(arquivo, test_size, modelo, configuracoes)
    except Exception as erro:
        raise BadRequest(f"Não foi possível analisar o arquivo: {erro}") from erro

    return jsonify({"metodo": metodo, "test_size": test_size, **resultado})


@app.errorhandler(BadRequest)
def bad_request(error):
    return jsonify({"erro": error.description}), 400


@app.errorhandler(RequestEntityTooLarge)
def arquivo_muito_grande(error):
    return jsonify({"erro": "O arquivo excede o limite máximo de 20 MB."}), 413


if __name__ == "__main__":
    app.run(port=5000)

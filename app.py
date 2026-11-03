from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import BadRequest, RequestEntityTooLarge

import ml_clas_sk
import ml_reg_sk


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024


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
    test_size = int(request.form.get("test_size", 20)) / 100

    if arquivo is None or not arquivo.filename:
        raise BadRequest("Selecione um arquivo CSV ou XLSX.")
    if metodo not in ("classificacao", "regressao"):
        raise BadRequest("Selecione um método de análise.")
    if not arquivo.filename.lower().endswith((".csv", ".xlsx")):
        raise BadRequest("Formato não suportado. Use CSV ou XLSX.")
    if test_size < 0.1 or test_size > 0.9:
        raise BadRequest("Porcentagem de teste inválida.")

    try:
        if metodo == "classificacao":
            resultado = ml_clas_sk.executar(arquivo, test_size)
        else:
            resultado = ml_reg_sk.executar(arquivo, test_size)
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

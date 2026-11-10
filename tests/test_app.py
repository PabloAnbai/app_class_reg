import io

import app as app_module
from app import app
from google.genai import errors as genai_errors


def client():
    app.config.update(TESTING=True)
    return app.test_client()


def teste_servidor_retorna_frontend():
    response = client().get("/")

    assert response.status_code == 200
    assert b"Painel de Avaliacao" in response.data or b"Painel de Avalia" in response.data
    assert b"Assistente de IA" in response.data
    assert b"assistant-question" in response.data


def teste_arquivos_internos_sao_bloqueados():
    assert client().get("/app.py").status_code == 404
    assert client().get("/ml_clas_sk.py").status_code == 404
    assert client().get("/requirements.txt").status_code == 404


def teste_upload_obrigatorio():
    response = client().post("/api/analisar", data={
        "metodo": "classificacao",
        "test_size": "20",
    })

    assert response.status_code == 400
    assert "Selecione um arquivo" in response.get_json()["erro"]


def teste_metodo_obrigatorio():
    response = client().post("/api/analisar", data={
        "arquivo": (io.BytesIO(b"1,2,A\n3,4,B\n"), "dados.csv"),
        "test_size": "20",
    }, content_type="multipart/form-data")

    assert response.status_code == 400
    assert "Selecione um método" in response.get_json()["erro"]


def teste_extensao_invalida():
    response = client().post("/api/analisar", data={
        "arquivo": (io.BytesIO(b"dados"), "dados.txt"),
        "metodo": "classificacao",
        "test_size": "20",
    }, content_type="multipart/form-data")

    assert response.status_code == 400
    assert "Formato não suportado" in response.get_json()["erro"]


def teste_config_padrao_desmarcado_exige_config():
    response = client().post("/api/analisar", data={
        "arquivo": (io.BytesIO(b"1,2,A\n3,4,A\n5,6,B\n7,8,B\n"), "dados.csv"),
        "metodo": "classificacao",
        "modelo": "svc",
        "padrao": "false",
        "test_size": "20",
    }, content_type="multipart/form-data")

    assert response.status_code == 200


def teste_api_encaminha_coluna_target_selecionada(monkeypatch):
    chamadas = {}

    def executar(arquivo, test_size, modelo, configuracoes, target_column):
        chamadas["target_column"] = target_column
        return {"modelos": {}}

    monkeypatch.setattr("ml_clas_sk.executar", executar)
    response = client().post("/api/analisar", data={
        "arquivo": (io.BytesIO(b"1,A,2\n3,B,4\n"), "dados.csv"),
        "metodo": "classificacao",
        "modelo": "svc",
        "target_column": "1",
        "test_size": "20",
    }, content_type="multipart/form-data")

    assert response.status_code == 200
    assert chamadas["target_column"] == 1


def teste_api_rejeita_coluna_target_invalida():
    response = client().post("/api/analisar", data={
        "arquivo": (io.BytesIO(b"1,A,2\n3,B,4\n"), "dados.csv"),
        "metodo": "classificacao",
        "target_column": "nao-e-um-indice",
        "test_size": "20",
    }, content_type="multipart/form-data")

    assert response.status_code == 400
    assert "coluna Target" in response.get_json()["erro"]


def teste_assistente_valida_pergunta_obrigatoria():
    response = client().post("/api/perguntar", data={"pergunta": "   "})

    assert response.status_code == 400
    assert "Informe uma pergunta" in response.get_json()["erro"]


def teste_assistente_limita_tamanho_da_pergunta():
    response = client().post("/api/perguntar", data={"pergunta": "a" * 2001})

    assert response.status_code == 400
    assert "2000 caracteres" in response.get_json()["erro"]


def teste_assistente_informa_chave_ausente(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    response = client().post("/api/perguntar", data={"pergunta": "Qual modelo devo usar?"})

    assert response.status_code == 400
    assert "GEMINI_API_KEY" in response.get_json()["erro"]


def teste_assistente_moca_gemini_e_envia_apenas_resumo(monkeypatch):
    chamadas = {}

    class ModelosFalsos:
        def generate_content(self, **kwargs):
            chamadas.update(kwargs)
            return type("Resposta", (), {"text": "1. Classificação\n2. SVC\n3. F1"})()

    def cliente_falso(**kwargs):
        chamadas["cliente"] = kwargs
        return type("Cliente", (), {"models": ModelosFalsos()})()

    monkeypatch.setenv("GEMINI_API_KEY", "chave-de-teste")
    monkeypatch.setenv("GEMINI_MODEL", "modelo-de-teste")
    monkeypatch.setattr(app_module.genai, "Client", cliente_falso)
    response = client().post("/api/perguntar", data={
        "pergunta": "Como prever a classe?",
        "arquivo": (io.BytesIO(b"731,classe-a\n842,classe-b\n"), "dados.csv"),
    }, content_type="multipart/form-data")

    assert response.status_code == 200
    assert response.get_json()["resposta"] == "1. Classificação\n2. SVC\n3. F1"
    assert chamadas["cliente"]["api_key"] == "chave-de-teste"
    assert chamadas["model"] == "modelo-de-teste"
    assert "Número de linhas: 2" in chamadas["contents"]
    assert "Número de colunas de atributos: 1" in chamadas["contents"]
    assert "valores distintos na última coluna: 2" in chamadas["contents"]
    assert "texto/categórico" in chamadas["contents"]
    assert "731" not in chamadas["contents"]
    assert "842" not in chamadas["contents"]
    assert "Responda sempre em português" in chamadas["config"].system_instruction


def teste_assistente_usa_modelo_padrao_atual(monkeypatch):
    chamadas = {}

    class ModelosFalsos:
        def generate_content(self, **kwargs):
            chamadas.update(kwargs)
            return type("Resposta", (), {"text": "Resposta de teste"})()

    monkeypatch.setenv("GEMINI_API_KEY", "chave-de-teste")
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.setattr(
        app_module.genai,
        "Client",
        lambda **kwargs: type("Cliente", (), {"models": ModelosFalsos()})(),
    )
    response = client().post("/api/perguntar", data={"pergunta": "Sugira um modelo."})

    assert response.status_code == 200
    assert chamadas["model"] == "gemini-3.5-flash-lite"


def teste_assistente_trata_limite_de_uso_do_gemini(monkeypatch):
    class ErroLimite(genai_errors.APIError):
        def __init__(self):
            Exception.__init__(self, "limite de uso")
            self.code = 429

    class ModelosFalsos:
        def generate_content(self, **kwargs):
            raise ErroLimite()

    monkeypatch.setenv("GEMINI_API_KEY", "chave-de-teste")
    monkeypatch.setattr(
        app_module.genai,
        "Client",
        lambda **kwargs: type("Cliente", (), {"models": ModelosFalsos()})(),
    )
    response = client().post("/api/perguntar", data={"pergunta": "Sugira um modelo."})

    assert response.status_code == 400
    assert "limite de uso" in response.get_json()["erro"]


def teste_assistente_explica_erro_de_chave_ou_modelo(monkeypatch):
    class ErroSolicitacao(genai_errors.APIError):
        def __init__(self):
            Exception.__init__(self, "erro de configuração")
            self.code = 400

    class ModelosFalsos:
        def generate_content(self, **kwargs):
            raise ErroSolicitacao()

    monkeypatch.setenv("GEMINI_API_KEY", "chave-de-teste")
    monkeypatch.setattr(
        app_module.genai,
        "Client",
        lambda **kwargs: type("Cliente", (), {"models": ModelosFalsos()})(),
    )
    response = client().post("/api/perguntar", data={"pergunta": "Sugira um modelo."})

    assert response.status_code == 400
    assert "GEMINI_MODEL" in response.get_json()["erro"]
    assert "API Gemini" in response.get_json()["erro"]


def teste_assistente_trata_timeout_do_gemini(monkeypatch):
    class ModelosFalsos:
        def generate_content(self, **kwargs):
            raise app_module.httpx.TimeoutException("timeout")

    monkeypatch.setenv("GEMINI_API_KEY", "chave-de-teste")
    monkeypatch.setattr(
        app_module.genai,
        "Client",
        lambda **kwargs: type("Cliente", (), {"models": ModelosFalsos()})(),
    )
    response = client().post("/api/perguntar", data={"pergunta": "Sugira um modelo."})

    assert response.status_code == 400
    assert "tempo limite" in response.get_json()["erro"]


def teste_assistente_trata_falha_de_rede_do_gemini(monkeypatch):
    class ModelosFalsos:
        def generate_content(self, **kwargs):
            raise app_module.httpx.NetworkError("sem conexão")

    monkeypatch.setenv("GEMINI_API_KEY", "chave-de-teste")
    monkeypatch.setattr(
        app_module.genai,
        "Client",
        lambda **kwargs: type("Cliente", (), {"models": ModelosFalsos()})(),
    )
    response = client().post("/api/perguntar", data={"pergunta": "Sugira um modelo."})

    assert response.status_code == 400
    assert "conectar ao Gemini" in response.get_json()["erro"]

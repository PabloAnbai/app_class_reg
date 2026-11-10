import io

from app import app


def client():
    app.config.update(TESTING=True)
    return app.test_client()


def teste_servidor_retorna_frontend():
    response = client().get("/")

    assert response.status_code == 200
    assert b"Painel de Avaliacao" in response.data or b"Painel de Avalia" in response.data


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

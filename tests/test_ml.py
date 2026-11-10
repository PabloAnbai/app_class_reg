import io

import ml_clas_sk
import ml_reg_sk
from app import app
from werkzeug.datastructures import FileStorage


def csv_file(text, name="dados.csv"):
    return FileStorage(
        stream=io.BytesIO(text.encode("latin1")),
        filename=name,
    )


def teste_csv_latin1_com_cabecalho_e_classificacao():
    linhas = ["area,perimetro,classe"]
    for indice in range(20):
        classe = "acao" if indice % 2 == 0 else "opcao"
        linhas.append(f"{indice},{indice * 2},{classe}")

    resultado = ml_clas_sk.executar(csv_file("\n".join(linhas)), 0.2)

    assert "svc" in resultado["modelos"]
    assert "random_forest" in resultado["modelos"]
    assert 0 <= resultado["modelos"]["svc"]["acuracia"] <= 1


def teste_classificacao_usa_target_selecionado():
    linhas = ["area,classe,perimetro"]
    for indice in range(20):
        classe = "acao" if indice % 2 == 0 else "opcao"
        linhas.append(f"{indice},{classe},{indice * 2}")

    atributos, classes = ml_clas_sk.ler_arquivo(
        csv_file("\n".join(linhas)), target_column=1
    )

    assert atributos.shape == (20, 2)
    assert atributos[0].tolist() == [0, 0]
    assert classes[0] == "acao"
    assert classes[1] == "opcao"


def teste_classificacao_rejeita_classe_com_poucas_amostras():
    linhas = ["area,classe"]
    for indice in range(12):
        classe = "A" if indice < 6 else "B"
        linhas.append(f"{indice},{classe}")
    linhas[-1] = "11,C"

    try:
        ml_clas_sk.executar(csv_file("\n".join(linhas)), 0.2)
        assert False, "Esperava ValueError para classe insuficiente"
    except ValueError as erro:
        assert "C" in str(erro)


def teste_regressao_retorna_metricas():
    linhas = ["area,valor"]
    for indice in range(20):
        linhas.append(f"{indice},{indice * 3 + 1}")

    resultado = ml_reg_sk.executar(csv_file("\n".join(linhas)), 0.2)

    assert "mlp" in resultado["modelos"]
    assert "random_forest" in resultado["modelos"]
    assert set(resultado["modelos"]["mlp"]) == {"mae", "mse", "rmse", "r2"}


def teste_regressao_usa_target_selecionado():
    linhas = ["valor,area,perimetro"]
    for indice in range(20):
        linhas.append(f"{indice * 3 + 1},{indice},{indice * 2}")

    atributos, target = ml_reg_sk.ler_arquivo(
        csv_file("\n".join(linhas)), target_column=0
    )

    assert atributos.shape == (20, 2)
    assert atributos[0].tolist() == [0, 0]
    assert target[0] == 1

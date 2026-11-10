import numpy as np
import pandas as pd
import io
from sklearn import metrics as me
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler


def ler_csv(dados):
    for encoding in ("utf-8-sig", "cp1252", "iso-8859-1", "latin1"):
        try:
            return pd.read_csv(
                io.BytesIO(dados),
                header=None,
                sep=None,
                engine="python",
                encoding=encoding,
            )
        except UnicodeDecodeError:
            continue
    raise ValueError("Não foi possível identificar a codificação do arquivo CSV.")


def ler_arquivo(arquivo, target_column=None):
    if hasattr(arquivo, "read"):
        name = getattr(arquivo, "filename", "")
        arquivo.seek(0)
        if name.lower().endswith(".xlsx"):
            df = pd.read_excel(arquivo, header=None)
        else:
            dados = arquivo.read()
            df = ler_csv(dados)
    else:
        if str(arquivo).lower().endswith(".xlsx"):
            df = pd.read_excel(arquivo, header=None)
        else:
            with open(arquivo, "rb") as entrada:
                df = ler_csv(entrada.read())

    df = df.dropna()
    if df.empty:
        raise ValueError("O arquivo não contém colunas de dados.")
    if target_column is None:
        target_column = len(df.columns) - 1
    if not isinstance(target_column, int) or not 0 <= target_column < len(df.columns):
        raise ValueError("A coluna Target selecionada não existe no arquivo.")

    coluna_target = df.columns[target_column]
    atributo_colunas = [coluna for coluna in df.columns if coluna != coluna_target]
    if not atributo_colunas:
        raise ValueError("O arquivo precisa ter ao menos uma coluna de atributos.")

    for coluna in [*atributo_colunas, coluna_target]:
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
    df = df.dropna(subset=[*atributo_colunas, coluna_target])

    if df.empty:
        raise ValueError("Nenhum dado numérico foi encontrado no arquivo.")

    atributos = df.loc[:, atributo_colunas].astype(float)
    target = df[coluna_target].astype(float)
    return atributos.values, target.values


def executar(arquivo, test_size=0.2, modelo=None, configuracoes=None, target_column=None):
    feat, target = ler_arquivo(arquivo, target_column)
    x_treino, x_teste, y_treino, y_teste = train_test_split(
        feat,
        target,
        test_size=test_size,
        random_state=42,
    )

    scaler = StandardScaler()
    x_treino_sc = scaler.fit_transform(x_treino)
    x_teste_sc = scaler.transform(x_teste)

    modelos = {}
    configuracoes = configuracoes or {}

    if modelo in (None, "mlp"):
        parametros_mlp = configuracoes.get("mlp", {})
        mlp = MLPRegressor(**parametros_mlp)
        mlp.fit(x_treino_sc, y_treino)
        mlp_pred = mlp.predict(x_teste_sc)
        modelos["mlp"] = metricas(y_teste, mlp_pred)

    if modelo in (None, "random_forest"):
        parametros_rf = configuracoes.get(
            "random_forest_regressao",
            configuracoes.get("random_forest", {}),
        )
        rf = RandomForestRegressor(**parametros_rf)
        rf.fit(x_treino, y_treino)
        rf_pred = rf.predict(x_teste)
        modelos["random_forest"] = metricas(y_teste, rf_pred)

    return {"modelos": modelos}


def metricas(y_teste, y_pred):
    mae = me.mean_absolute_error(y_teste, y_pred)
    mse = me.mean_squared_error(y_teste, y_pred)
    return {
        "mae": round(mae, 4),
        "mse": round(mse, 4),
        "rmse": round(float(np.sqrt(mse)), 4),
        "r2": round(me.r2_score(y_teste, y_pred), 4),
    }

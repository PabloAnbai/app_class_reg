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


def ler_arquivo(arquivo):
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
    numericas = df.columns
    for coluna in numericas:
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
    df = df.dropna()

    if df.empty:
        raise ValueError("Nenhum dado numérico foi encontrado no arquivo.")

    atributos = df.iloc[:, :-1].astype(float)
    target = df.iloc[:, -1].astype(float)
    return atributos.values, target.values


def executar(arquivo, test_size=0.2):
    feat, target = ler_arquivo(arquivo)
    x_treino, x_teste, y_treino, y_teste = train_test_split(
        feat,
        target,
        test_size=test_size,
        random_state=42,
    )

    scaler = StandardScaler()
    x_treino_sc = scaler.fit_transform(x_treino)
    x_teste_sc = scaler.transform(x_teste)

    mlp = MLPRegressor(
        hidden_layer_sizes=(150,),
        activation="relu",
        solver="lbfgs",
        alpha=0.01,
        max_iter=1000,
        random_state=42,
    )
    mlp.fit(x_treino_sc, y_treino)
    mlp_pred = mlp.predict(x_teste_sc)

    rf = RandomForestRegressor(
        n_estimators=80,
        criterion="squared_error",
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(x_treino, y_treino)
    rf_pred = rf.predict(x_teste)

    return {
        "modelos": {
            "mlp": metricas(y_teste, mlp_pred),
            "random_forest": metricas(y_teste, rf_pred),
        }
    }


def metricas(y_teste, y_pred):
    mae = me.mean_absolute_error(y_teste, y_pred)
    mse = me.mean_squared_error(y_teste, y_pred)
    return {
        "mae": round(mae, 4),
        "mse": round(mse, 4),
        "rmse": round(float(np.sqrt(mse)), 4),
        "r2": round(me.r2_score(y_teste, y_pred), 4),
    }

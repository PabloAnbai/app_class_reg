import numpy as np
import pandas as pd
import io
from collections import Counter
from sklearn import metrics as me
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
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
    atributo_colunas = df.columns[:-1]
    for coluna in atributo_colunas:
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
    df = df.dropna(subset=list(atributo_colunas))

    if df.empty:
        raise ValueError("Nenhum dado numérico foi encontrado nas colunas de atributos.")

    atributos = df.iloc[:, :-1].astype(float)
    classes_originais = df.iloc[:, -1].tolist()
    return atributos.values, classes_originais


def executar(arquivo, test_size=0.2):
    feat, classes_originais = ler_arquivo(arquivo)
    classes = sorted(set(classes_originais), key=str)
    contagem_classes = Counter(classes_originais)
    classes_invalidas = [classe for classe in classes if contagem_classes[classe] < 2]
    if classes_invalidas:
        raise ValueError(
            "Cada classe precisa de pelo menos duas amostras. Classes insuficientes: "
            + ", ".join(map(str, classes_invalidas))
        )
    if len(feat) < 4:
        raise ValueError("A classificação exige pelo menos quatro amostras válidas.")

    classe_para_numero = {classe: indice for indice, classe in enumerate(classes)}
    y = np.array([classe_para_numero[classe] for classe in classes_originais])

    x_treino, x_teste, y_treino, y_teste = train_test_split(
        feat,
        y,
        test_size=test_size,
        random_state=42,
        stratify=y,
    )

    scaler = StandardScaler()
    x_treino_sc = scaler.fit_transform(x_treino)
    x_teste_sc = scaler.transform(x_teste)

    mlp = MLPClassifier(
        hidden_layer_sizes=(125,),
        activation="logistic",
        solver="adam",
        alpha=0.01,
        learning_rate="adaptive",
        max_iter=10000,
        random_state=42,
    )
    mlp.fit(x_treino_sc, y_treino)
    mlp_pred = mlp.predict(x_teste_sc)

    rf = RandomForestClassifier(
        n_estimators=100,
        criterion="gini",
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
    cm = me.confusion_matrix(y_teste, y_pred).tolist()
    return {
        "matriz_confusao": cm,
        "acuracia": round(me.accuracy_score(y_teste, y_pred), 4),
        "precisao": round(me.precision_score(y_teste, y_pred, average="macro", zero_division=0), 4),
        "recall": round(me.recall_score(y_teste, y_pred, average="macro", zero_division=0), 4),
        "f1": round(me.f1_score(y_teste, y_pred, average="macro", zero_division=0), 4),
    }

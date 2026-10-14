
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import umap
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

ROOT = Path(__file__).resolve().parents[4]
CSV = ROOT / "data" / "btcusd_1-min_data.csv"
FIGURES = Path(__file__).resolve().parents[1] / "figures"
SEED = 42  # mesma semente do resto do relatório

CUT = "2024-01-01"  # mesmo corte da seção 9
PRICE_FEATURES = ["ret_1", "amplitude", "direcao"]
VOLUME_FEATURES = ["Volume"]
FEATURES = PRICE_FEATURES + VOLUME_FEATURES
TARGET = "ret_futuro"


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Troca os preços em USD por valores relativos (seções 7 e 9).

    Tudo usa só informação até o minuto t, menos o alvo, que é o retorno até t+1.
    """
    out = pd.DataFrame(index=df.index)
    out["ret_1"] = np.log(df["Close"] / df["Close"].shift(1))  # retorno do minuto
    out["amplitude"] = np.log(df["High"] / df["Low"])  # volatilidade do minuto
    out["direcao"] = np.log(df["Close"] / df["Open"])  # sobe ou desce no minuto
    out["Volume"] = df["Volume"]  # log1p fica no pipeline
    out[TARGET] = np.log(df["Close"].shift(-1) / df["Close"])
    # o shift deixa NaN só na primeira linha (ret_1) e na última (alvo)
    return out.dropna()


def split(feats: pd.DataFrame):
    train, test = feats[feats.index < CUT], feats[feats.index >= CUT]
    # o alvo da última linha do treino é o Close do primeiro minuto do teste
    train = train.iloc[:-1]
    return train[FEATURES], train[TARGET], test[FEATURES], test[TARGET]


def make_preprocess() -> ColumnTransformer:
    return ColumnTransformer([
        ("preco", StandardScaler(), PRICE_FEATURES),
        ("volume", Pipeline([
            ("log1p", FunctionTransformer(np.log1p, feature_names_out="one-to-one")),
            ("scale", StandardScaler()),
        ]), VOLUME_FEATURES),
    ])


def report(nome: str, X: np.ndarray):
    print(f"{nome}: shape {X.shape}, NaN {np.isnan(X).sum()}")


def scatter_target(ax, Z: np.ndarray, y: np.ndarray):
    # o retorno tem cauda pesada: a escala de cor vai até o percentil 99 do |alvo|
    lim = np.percentile(np.abs(y), 99)
    return ax.scatter(Z[:, 0], Z[:, 1], c=y, cmap="coolwarm", vmin=-lim, vmax=lim, s=2, alpha=0.6)


def plot_pca(X: np.ndarray, y: np.ndarray, names, sample: np.ndarray):
    pca = PCA(random_state=SEED).fit(X)
    acumulada = np.cumsum(pca.explained_variance_ratio_)
    print("\nPCA — variância explicada acumulada:", acumulada.round(4))
    print("Loadings (linhas = componentes):")
    print(pd.DataFrame(pca.components_, columns=names, index=[f"PC{i + 1}" for i in range(len(names))]).round(3))

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), layout="constrained")
    ax = axes[0]
    ax.plot(range(1, len(acumulada) + 1), acumulada, marker="o")
    ax.set_xticks(range(1, len(acumulada) + 1))
    ax.set_ylim(0, 1.05)
    ax.set_title("Variância explicada acumulada")
    ax.set_xlabel("número de componentes")
    ax.set_ylabel("fração da variância")

    ax = axes[1]
    Z = pca.transform(X[sample])[:, :2]
    pontos = scatter_target(ax, Z, y[sample])
    ax.set_title("PCA (2 primeiros componentes)")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    fig.colorbar(pontos, ax=ax, label="retorno do minuto seguinte (log)")
    plt.savefig(FIGURES / "pca.png", dpi=120, bbox_inches="tight")
    plt.close()


def plot_nonlinear(X: np.ndarray, y: np.ndarray):
    projecoes = [
        ("t-SNE, perplexity = 30", TSNE(perplexity=30, random_state=SEED)),
        ("t-SNE, perplexity = 100", TSNE(perplexity=100, random_state=SEED)),
        ("UMAP, n_neighbors = 15", umap.UMAP(n_neighbors=15, random_state=SEED)),
        ("UMAP, n_neighbors = 100", umap.UMAP(n_neighbors=100, random_state=SEED)),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(11, 9), layout="constrained")
    for ax, (titulo, modelo) in zip(axes.flat, projecoes):
        print("calculando", titulo)
        pontos = scatter_target(ax, modelo.fit_transform(X), y)
        ax.set_title(titulo)
        ax.set_xticks([])
        ax.set_yticks([])
    fig.colorbar(pontos, ax=axes, label="retorno do minuto seguinte (log)")
    fig.suptitle(f"Projeções não lineares (amostra de {len(X)} minutos do treino)")
    plt.savefig(FIGURES / "tsne_umap.png", dpi=120, bbox_inches="tight")
    plt.close()


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(CSV)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="s")
    df = df.set_index("Timestamp")

    X_train, y_train, X_test, y_test = split(build_features(df))

    preprocess = make_preprocess()
    X_train_t = preprocess.fit_transform(X_train)  # fit só no treino
    X_test_t = preprocess.transform(X_test)  # teste só é transformado

    names = list(preprocess.get_feature_names_out())
    print("Features:", names)
    report("treino", X_train_t)
    report("teste", X_test_t)

    # t-SNE e UMAP não escalam para 6 milhões de linhas: amostra fixa do treino
    rng = np.random.default_rng(SEED)
    sample = rng.choice(len(X_train_t), 10_000, replace=False)
    y = y_train.to_numpy()
    plot_pca(X_train_t, y, names, sample)
    plot_nonlinear(X_train_t[sample], y[sample])


if __name__ == "__main__":
    main()

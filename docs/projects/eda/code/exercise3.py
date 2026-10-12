
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[4]
CSV = ROOT / "data" / "btcusd_1-min_data.csv"
FIGURES = Path(__file__).resolve().parents[1] / "figures"
SEED = 42  # mesma semente do resto do relatório

COLUMNS = ["Open", "High", "Low", "Volume"]
TARGET = "Close"


def correlacoes(df: pd.DataFrame):
    dados = df[COLUMNS + [TARGET]].copy()
    dados["Volume"] = np.log1p(dados["Volume"])
    corr = dados.corr(method="spearman")
    print(corr.round(4))

    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr)), corr.columns)
    ax.set_yticks(range(len(corr)), corr.columns)
    for i in range(len(corr)):
        for j in range(len(corr)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center")
    fig.colorbar(im, label="Spearman ρ")
    ax.set_title("Correlação de Spearman (Volume em log1p)")
    plt.savefig(FIGURES / "corr_spearman.png", dpi=120, bbox_inches="tight")
    plt.close()


def scatters(df: pd.DataFrame):
    # 7,7 mi de pontos viram uma mancha: amostra fixa com a semente do relatório
    amostra = df.sample(100_000, random_state=SEED)

    fig, axes = plt.subplots(2, 2, figsize=(11, 8), layout="constrained")
    for ax, col in zip(axes.flat, ["Open", "High", "Low"]):
        ax.scatter(amostra[col], amostra[TARGET], s=1, alpha=0.3, label="minuto (amostra de 100 mil)")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(f"{col} × Close")
        ax.set_xlabel(f"{col} (USD, log)")
        ax.set_ylabel("Close (USD, log)")
        ax.legend(markerscale=10)

    ax = axes[1, 1]
    ax.scatter(np.log1p(amostra["Volume"]), amostra[TARGET], s=1, alpha=0.3, label="minuto (amostra de 100 mil)")
    ax.set_yscale("log")
    ax.set_title("log1p(Volume) × Close")
    ax.set_xlabel("log1p(Volume) (BTC)")
    ax.set_ylabel("Close (USD, log)")
    ax.legend(markerscale=10)


    fig.suptitle("Features × Close")
    plt.savefig(FIGURES / "scatter_close.png", dpi=120, bbox_inches="tight")
    plt.close()




def main():
    FIGURES.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(CSV)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="s")
    df = df.set_index("Timestamp")
    correlacoes(df)
    scatters(df)






if __name__ == "__main__":
    main()

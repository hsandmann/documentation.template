
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


def describe(df: pd.DataFrame):
    
    for col in COLUMNS:
        print(f"Analise de {col}\n")


        col_decribe = df[col].describe()
        col_assimetria = df[col].skew()
        print(col_decribe)
        print(f"assimetria: {col_assimetria}\n")

        q1, q3 = df[col].quantile([0.25, 0.75])
        limite = q3 + 1.5 * (q3 - q1)
        print(f"outliers {col}:\n", (df[col] > limite).mean() * 100, "%")

        if col == "Volume":
            log_vol = np.log(df.loc[df[col]>0, col])
            q1, q3 = log_vol.quantile([0.25, 0.75])
            limite_alto = q3 + 1.5 * (q3 - q1)
            limite_baixo = q1 - 1.5 * (q3 - q1)
            fora = (log_vol > limite_alto) | (log_vol < limite_baixo)
            print(f"outliers log({col}):\n", fora.mean() * 100, "% (dos minutos com negócio)")
        
           
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
        ax1.hist(df[col], bins=100)
        if col == "Volume" :
            ax1.set_title(f"{col} (BTC)")
        else:
            ax1.set_title(f"{col} (USD)")
        ax2.hist(np.log(df.loc[df[col]>0, col]), bins=100)
        if col == "Volume" :
            ax2.set_title(f"log({col}) - Volume > 0")
        else:
            ax2.set_title(f"log({col})")
        plt.savefig(FIGURES / f"{col}_hist.png", dpi=120, bbox_inches="tight")
        plt.close()




def main():
    FIGURES.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(CSV)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="s")
    df = df.set_index("Timestamp")
    describe(df)






if __name__ == "__main__":
    main()

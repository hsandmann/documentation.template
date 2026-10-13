
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler
from sklearn.datasets import make_blobs, make_classification

ROOT = Path(__file__).resolve().parents[4]
FIGURES = Path(__file__).resolve().parents[1] / "figures"
SEEDS = [42, 54, 67]

def data():
    X, y = make_classification(n_samples=1500, n_features=4, n_informative=4,
                           n_redundant=0, n_repeated=0, n_classes=3,
                           n_clusters_per_class=2, class_sep=1.0,
                           random_state=42)
    return X , y




def softmax(z):
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


class MLP:

    def __init__(self, sizes, lr=0.1, seed=42):
        np.random.seed(seed)
        self.lr = lr
        self.W = []
        self.b = []
        for i in range(len(sizes) - 1):
            entrada = sizes[i]
            saida = sizes[i + 1]
            self.W.append(np.random.randn(entrada, saida) / np.sqrt(entrada))
            self.b.append(np.zeros(saida))

    def forward(self, X):
        self.A = [X]
        n_camadas = len(self.W)
        for i in range(n_camadas):
            Z = self.A[i] @ self.W[i] + self.b[i]
            if i == n_camadas - 1:
                A = softmax(Z)
            else:
                A = np.tanh(Z)
            self.A.append(A)
        return self.A[-1]

    def loss(self, p, y):
        p = np.clip(p, 1e-12, 1)
        return -np.mean(np.sum(y * np.log(p), axis=1))

    def backward(self, y):
        n = len(y)
        dZ = (self.A[-1] - y) / n
        for i in range(len(self.W) - 1, -1, -1):
            dW = self.A[i].T @ dZ
            db = dZ.sum(axis=0)
            if i > 0:
                dZ = (dZ @ self.W[i].T) * (1 - self.A[i] ** 2)
            self.W[i] -= self.lr * dW
            self.b[i] -= self.lr * db

    def fit(self, X, y, epochs):
        y = np.eye(self.W[-1].shape[1])[y]
        historico = []
        for epoca in range(epochs):
            p = self.forward(X)
            historico.append(self.loss(p, y))
            self.backward(y)
        return historico

    def predict(self, X):
        p = self.forward(X)
        return np.argmax(p, axis=1)





def n_parametros(model):
    total = 0
    for i in range(len(model.W)):
        total += model.W[i].size + model.b[i].size
    return total


def Figure6(curvas):
    for nome in curvas:
        plt.plot(curvas[nome], label=nome)
    plt.xlabel("Época")
    plt.ylabel("Loss de treino (cross-entropy)")
    plt.legend()
    plt.savefig(FIGURES / "figure6.png", dpi=120, bbox_inches="tight")
    plt.close()


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)

    X, y = data()
    X_train, X_test, y_train, y_test = train_test_split(X, y,test_size=0.2, random_state=42, stratify=y)

    lr, epochs = 0.1, 2000
    redes = {"Exercício 3 — [4, 16, 3]": [4, 16, 3],
             "Exercício 4 — [4, 16, 16, 3]": [4, 16, 16, 3]}
    curvas = {}

    for nome in redes:
        sizes = redes[nome]
        historicos = []
        losses = []
        accs_treino = []
        accs_teste = []
        for seed in SEEDS:
            model = MLP(sizes, lr=lr, seed=seed)
            historico = model.fit(X_train, y_train, epochs)
            acc_treino = np.mean(model.predict(X_train) == y_train)
            acc_teste = np.mean(model.predict(X_test) == y_test)
            historicos.append(historico)
            losses.append(historico[-1])
            accs_treino.append(acc_treino)
            accs_teste.append(acc_teste)
            print(f"{nome}, seed={seed}: loss final {historico[-1]:.3f}, "
                  f"acurácia treino {acc_treino:.1%}, acurácia teste {acc_teste:.1%}")

        curvas[nome] = np.mean(historicos, axis=0)
        print(f"{nome}: {n_parametros(model)} parâmetros | média das seeds: "
              f"loss final {np.mean(losses):.3f}, acurácia treino {np.mean(accs_treino):.1%}, "
              f"acurácia teste {np.mean(accs_teste):.1%}\n")

    Figure6(curvas)


if __name__ == "__main__":
    main()

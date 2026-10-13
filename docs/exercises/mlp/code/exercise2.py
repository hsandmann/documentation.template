
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler
from sklearn.datasets import make_blobs
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[4]
FIGURES = Path(__file__).resolve().parents[1] / "figures"
SEED = 42  # mesma semente do resto do relatório


def data():
    centers = np.array([[0., 0.], [3., 3.], [-3., -3.]])
    X, c = make_blobs(n_samples=[500, 250, 250], centers=centers,
                    cluster_std=1.2, random_state=42)
    y = (c > 0).astype(int)      # class 0: 1 cluster | class 1: 2 clusters
    return X , y


def Figure1(X,y):
    sc = plt.scatter(X[:, 0], X[:, 1], c=y)
    plt.xlabel("x1")
    plt.ylabel("x2")
    plt.legend(*sc.legend_elements(), title="Classe")
    plt.savefig(FIGURES / "figure1.png", dpi=120, bbox_inches="tight")
    plt.close()


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


class MLP:

    def __init__(self, sizes, lr=0.1, seed=SEED):
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
                A = sigmoid(Z)
            else:
                A = np.tanh(Z)
            self.A.append(A)
        return self.A[-1]

    def loss(self, p, y):
        p = np.clip(p, 1e-12, 1 - 1e-12)
        return -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))

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
        y = y.reshape(-1, 1)
        historico = []
        for epoca in range(epochs):
            p = self.forward(X)
            historico.append(self.loss(p, y))
            self.backward(y)
        return historico

    def predict(self, X):
        p = self.forward(X).ravel()
        return (p >= 0.5).astype(int)


def Figure2(historico):
    plt.plot(historico)
    plt.xlabel("Época")
    plt.ylabel("Loss de treino (BCE)")
    plt.savefig(FIGURES / "figure2.png", dpi=120, bbox_inches="tight")
    plt.close()


def Figure3(model, X_test, y_test):
    eixo = np.linspace(-7, 7, 300)
    xx, yy = np.meshgrid(eixo, eixo)
    pontos = np.column_stack([xx.ravel(), yy.ravel()])
    zz = model.predict(pontos).reshape(xx.shape)
    plt.contourf(xx, yy, zz, alpha=0.3)
    sc = plt.scatter(X_test[:, 0], X_test[:, 1], c=y_test, edgecolors="k")
    plt.xlabel("x1")
    plt.ylabel("x2")
    plt.legend(*sc.legend_elements(), title="Classe")
    plt.savefig(FIGURES / "figure3.png", dpi=120, bbox_inches="tight")
    plt.close()


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)

    X, y = data()
    X_train, X_test, y_train, y_test = train_test_split(X, y,test_size=0.2, random_state=42, stratify=y)
    Figure1(X,y)
    baseline = LogisticRegression().fit(X_train, y_train)
    acc_baseline = baseline.score(X_test, y_test)
    print(f"Baseline (regressão logística) — acurácia no teste: {acc_baseline:.1%}")

    sizes, lr, epochs = [2, 8, 1], 0.1, 2000
    model = MLP(sizes, lr=lr)
    historico = model.fit(X_train, y_train, epochs)
    acc_mlp = np.mean(model.predict(X_test) == y_test)
    print(f"MLP {sizes}, lr={lr}, {epochs} épocas — acurácia no teste: {acc_mlp:.1%}")

    Figure2(historico)
    Figure3(model, X_test, y_test)






if __name__ == "__main__":
    main()

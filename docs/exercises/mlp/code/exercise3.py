
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
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay

ROOT = Path(__file__).resolve().parents[4]
FIGURES = Path(__file__).resolve().parents[1] / "figures"
SEED = 42  # mesma semente do resto do relatório


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


def Figure4(historico):
    plt.plot(historico)
    plt.xlabel("Época")
    plt.ylabel("Loss de treino (cross-entropy)")
    plt.savefig(FIGURES / "figure4.png", dpi=120, bbox_inches="tight")
    plt.close()


def Figure5(y_test, y_pred):
    ConfusionMatrixDisplay.from_predictions(y_test, y_pred, cmap="Blues")
    plt.xlabel("Classe prevista")
    plt.ylabel("Classe real")
    plt.savefig(FIGURES / "figure5.png", dpi=120, bbox_inches="tight")
    plt.close()


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)

    X, y = data()
    X_train, X_test, y_train, y_test = train_test_split(X, y,test_size=0.2, random_state=42, stratify=y)
    baseline = LogisticRegression().fit(X_train, y_train)
    acc_baseline = baseline.score(X_test, y_test)
    print(f"Baseline (regressão logística) — acurácia no teste: {acc_baseline:.1%}")

    sizes, lr, epochs = [4, 16, 3], 0.1, 2000
    model = MLP(sizes, lr=lr)
    historico = model.fit(X_train, y_train, epochs)
    y_pred = model.predict(X_test)
    acc_mlp = np.mean(y_pred == y_test)
    print(f"MLP {sizes}, lr={lr}, {epochs} épocas — acurácia no teste: {acc_mlp:.1%}")

    Figure4(historico)
    Figure5(y_test, y_pred)






if __name__ == "__main__":
    main()

# NumPy — Mini-cours

> Brief associé : P0
> Durée de lecture + pratique : ~45 min
> Pré-requis : Python de base (variables, listes, fonctions, boucles), env virtuel
> avec `numpy` installé.

## Pourquoi cette techno ?

NumPy (« Numerical Python ») est la **brique de base** de toute la stack data Python.
Pandas, scikit-learn, PyTorch, TensorFlow s'appuient tous sur NumPy en sous-main.

Tu n'écriras jamais de gros calculs NumPy à la main dans cette formation. Mais tu
**verras passer** des `np.array`, `df.values`, `np.nan`, `np.where` en permanence. Si
tu ne sais pas lire ça, tu ne sais pas lire le code IA.

**Alternatives** : il n'y en a pas vraiment dans l'écosystème Python. PyTorch propose
des tenseurs très proches mais c'est pour le deep learning. Pour la data classique,
NumPy règne.

## Concepts clés

- **`ndarray` (N-dimensional array)** : tableau multidimensionnel **homogène** (un seul
  dtype : `int64`, `float64`, `bool`, etc.). Plus rapide qu'une liste Python parce que
  contigu en mémoire et opéré en C/Fortran.
- **Vectorisation** : appliquer une opération à tout un tableau en **une seule
  expression** sans boucle Python explicite. `arr * 2` est ~100× plus rapide que
  `[x*2 for x in arr]`.
- **Broadcasting** : NumPy étire automatiquement les dimensions compatibles pour les
  opérations entre tableaux de tailles différentes (ex : ajouter un scalaire à toute
  une matrice, ou un vecteur ligne à chaque ligne d'une matrice).
- **Indexation booléenne** : sélectionner les éléments d'un tableau via un masque
  booléen (`arr[arr > 0]`). Très utilisé pour le nettoyage de données.
- **`np.nan`** : valeur spéciale pour les données manquantes en numérique. À ne jamais
  comparer avec `==` (utiliser `np.isnan(x)` ou Pandas `pd.isna(x)`).

## Exemple minimal qui tourne

```python
# Versions testées : python 3.11, numpy 2.x
import numpy as np

# Création
a = np.array([1, 2, 3, 4, 5])
b = np.arange(0, 10, 2)             # [0, 2, 4, 6, 8]
m = np.zeros((3, 4))                # matrice 3x4 de zéros
r = np.random.default_rng(42).normal(loc=0, scale=1, size=(3, 4))

# Inspection
print("a.shape  =", a.shape)        # (5,)
print("a.dtype  =", a.dtype)        # int64
print("r.mean() =", r.mean().round(3))

# Vectorisation
print("a * 10   =", a * 10)         # [10 20 30 40 50]
print("a + b[:5]=", a + b[:5])      # [1 4 7 10 13]

# Indexation booléenne
print("pairs    =", a[a % 2 == 0])  # [2 4]

# Broadcasting
print("r + 100  =\n", (r + 100).round(2))
```

Lance ce snippet dans un notebook ou via `python -c "..."`. Tu dois voir des sorties
cohérentes.

## Exercice guidé

Ouvre un notebook, fais ces 4 questions à la suite. **Cherche par toi-même
d'abord** — la solution est masquée plus bas, à révéler seulement après ta
tentative.

1. Crée un tableau `temperatures` de 30 valeurs simulées (entre 15 et 30 °C) avec un
   `random.default_rng(seed=42)`. Calcule la **moyenne**, la **médiane** et l'**écart-type**.
2. Combien de jours sont **au-dessus de 25 °C** ?
3. Remplace toutes les valeurs au-dessus de 28 °C par `np.nan`, puis recalcule la
   moyenne en ignorant les NaN.
4. Construis une matrice 5×6 d'entiers aléatoires entre 0 et 100, et extrait la
   **colonne 3** puis les **lignes paires**.

<details>
<summary>🔒 <strong>Solution</strong> — clique pour révéler (après avoir cherché)</summary>

```python
import numpy as np
rng = np.random.default_rng(42)
temperatures = rng.uniform(15, 30, 30)

# Q1
print(temperatures.mean(), np.median(temperatures), temperatures.std())

# Q2
n_chaud = (temperatures > 25).sum()
print(n_chaud)

# Q3
temperatures2 = np.where(temperatures > 28, np.nan, temperatures)
print(np.nanmean(temperatures2))

# Q4
mat = rng.integers(0, 100, size=(5, 6))
print(mat[:, 3])          # colonne 3
print(mat[::2, :])        # lignes paires
```

</details>

## Pour aller plus loin

- Doc officielle : https://numpy.org/doc/stable/
- Notebook ZTM `introduction-to-numpy.ipynb` (+ vidéo) — fourni en complément
  par la formatrice, à consulter en M1 si besoin de plus de pratique.
- *Hands-On ML* (Aurélien Géron, 3ᵉ éd.) — annexe NumPy en fin d'ouvrage.

## Vérification (checklist apprenant)

- [ ] J'ai fait tourner l'exemple minimal sans erreur.
- [ ] Je sais expliquer en 2 min ce qu'est la **vectorisation** et pourquoi c'est plus
      rapide qu'une boucle Python.
- [ ] J'ai fait les 4 questions de l'exercice guidé (sans regarder les solutions
      d'abord).
- [ ] Je sais ce que vaut `np.nan == np.nan` et pourquoi (réponse : `False` — NaN
      n'est jamais égal à NaN, il faut utiliser `np.isnan`).
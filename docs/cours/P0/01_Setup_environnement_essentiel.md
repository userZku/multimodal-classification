# Setup environnement Python pour l'IA — Mini-cours

> Brief associé : P0
> Durée de lecture + pratique : ~1 h
> Pré-requis : avoir un OS récent (Windows 10+, macOS 12+, Linux Ubuntu 22+) et un
> compte GitHub. Si tu n'as pas de compte GitHub, en créer un (5 min).

## Pourquoi cette techno ?

Travailler en IA, c'est jongler avec **plusieurs versions de Python** et **des
dizaines de librairies aux versions parfois incompatibles**. Sans environnements
virtuels, ton poste devient invivable au bout du 3ᵉ projet.

L'écosystème moderne propose plusieurs gestionnaires d'environnements :

- **`venv`** (stdlib) : minimal, suffisant pour démarrer.
- **`conda` / `miniconda`** : populaire en data science, gère aussi le binaire (utile
  pour scikit-learn sur certaines plateformes).
- **`uv`** (Astral, 2024) : plus rapide, plus moderne, gestion lock-file native. Notre
  préféré sur ce parcours pour sa vitesse.

On utilisera **`uv` en option par défaut**, mais `venv` ou `conda` sont valides aussi.
Le choix de l'outil n'est pas évalué. Ce qui compte : avoir un **environnement isolé,
reproductible et activable en une commande**.

## Concepts clés

- **Environnement virtuel** : un dossier qui contient ta version de Python et les
  librairies installées. On l'active pour qu'elles deviennent disponibles. Quand on le
  désactive, on retombe dans le Python système. **Un projet = un environnement.**
- **Lock-file (`requirements.txt` ou `uv.lock`)** : fige les versions exactes des
  libs. Permet à un collègue (ou à toi sur un autre poste) de recréer exactement le
  même environnement.
- **IDE** : VS Code, PyCharm Community, ou JupyterLab. Ce qui compte : l'IDE doit
  savoir **détecter ton environnement virtuel** (Python interpreter setting). En cas de
  doute : VS Code + extension Python est la combinaison la plus simple.
- **Git + GitHub** : versionnement local + hébergement distant. On commit toujours, on
  push souvent. On ne pousse **jamais** ses `.venv` ni ses `.env` (cf .gitignore).
- **Jupyter Notebook** : interface interactive pour exécuter du Python cellule par
  cellule. Format `.ipynb` = JSON sous le capot. C'est le format de la certif finale.

## Exemple minimal qui tourne

À exécuter dans un terminal (PowerShell sur Windows, Terminal sur macOS/Linux).

### Option A — avec `uv` (recommandée)

```bash
# 1. Installer uv (une seule fois)
# macOS / Linux :
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows (PowerShell) :
# irm https://astral.sh/uv/install.ps1 | iex

# 2. Créer un dossier projet et un env virtuel
mkdir test-env && cd test-env
uv venv --python 3.11

# 3. Activer l'env
source .venv/bin/activate            # macOS / Linux
# source .venv/Scripts/activate      # Windows — Git Bash
# .venv\Scripts\activate             # Windows — PowerShell / cmd.exe

# 4. Installer 3 libs et lancer un notebook
uv pip install jupyter pandas matplotlib

# 5. Lancer Jupyter
jupyter notebook
```

### Option B — avec `venv` (Python stdlib)

```bash
mkdir test-env && cd test-env
python3.11 -m venv .venv
source .venv/bin/activate                # macOS / Linux
# source .venv/Scripts/activate           # Windows — Git Bash
# .venv\Scripts\activate                  # Windows — PowerShell / cmd.exe
pip install --upgrade pip
pip install jupyter pandas matplotlib
jupyter notebook
```

Dans Jupyter qui s'ouvre dans ton navigateur :

```python
# Cellule 1
import pandas as pd
import matplotlib.pyplot as plt

df = pd.DataFrame({"x": range(10), "y": [i**2 for i in range(10)]})
df.plot.line(x="x", y="y", marker="o", title="Mon premier graphique")
plt.show()
```

→ Tu dois voir une parabole. Si oui, **bravo, ton poste est prêt**.

## Exercice guidé

1. Crée un dossier `atos-onboarding-<prenom>` quelque part de propre (pas le bureau).
2. Crée un environnement virtuel Python 3.11 dedans (uv ou venv, au choix).
3. Active-le. Vérifie avec `python --version` (doit afficher 3.11.x).
4. Installe : `pandas`, `numpy`, `matplotlib`, `jupyter`, `requests`.
5. Initialise un repo Git : `git init`.
6. Crée un fichier `.gitignore` avec au minimum :
   ```
   .venv/
   __pycache__/
   *.pyc
   .ipynb_checkpoints/
   .env
   .DS_Store
   ```
7. Crée un repo `atos-onboarding-<prenom>` sur GitHub (public ou privé avec accès en
   lecture pour la formatrice).
8. Lie le repo local au remote, fais un premier commit, pousse :
   ```bash
   git remote add origin git@github.com:<ton_user>/atos-onboarding-<prenom>.git
   git add .gitignore
   git commit -m "chore: initial setup"
   git branch -M main
   git push -u origin main
   ```

✅ **Solution attendue** : sur GitHub, tu vois ton repo avec un commit et un fichier
`.gitignore`. Pas de `.venv` poussé (sinon ton `.gitignore` n'a pas pris à temps).

## Pour aller plus loin

- Documentation `uv` : https://docs.astral.sh/uv/
- Documentation `venv` : https://docs.python.org/3/library/venv.html
- Guide Git « Pro Git » (chapitres 1-3 suffisent) : https://git-scm.com/book/fr/v2
- Cheat sheet `.gitignore` Python : https://github.com/github/gitignore/blob/main/Python.gitignore

## Vérification (checklist apprenant)

- [ ] `python --version` affiche `Python 3.11.x` ou plus récent (dans l'env activé).
- [ ] J'ai pu lancer Jupyter Notebook et exécuter un graphique matplotlib.
- [ ] Mon `.gitignore` exclut bien `.venv`, `__pycache__`, `.ipynb_checkpoints`.
- [ ] Mon repo `atos-onboarding-<prenom>` existe sur GitHub avec au moins 1 commit.
- [ ] Je peux expliquer à un·e collègue **pourquoi un environnement virtuel** en 2 min.
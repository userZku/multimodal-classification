# EDA orientée saisonnalité — Mini-cours

> Brief associé : M4-B1
> Durée : ~20 min
> Pré-requis : pandas + seaborn déjà vus en M1-M2-M3.

## Pourquoi cette techno ?

Un dataset **saisonnier** (Bike Sharing) demande une **EDA spécifique** :
on ne se contente pas de `describe()` global, on regarde la cible
**conditionnellement** au temps (heure / jour / saison / météo).

L'objectif est d'**anticiper** ce qu'un modèle linéaire va rater (les
**interactions** saison × heure, weekend × heure, météo × température),
et donc de **justifier** pourquoi un modèle non-linéaire (forêt, boosting)
va capter mieux.

## Concepts clés

- **Distribution conditionnelle** : `sns.boxplot(data=df, x="season", y="cnt")`
  → comment la cible varie selon une feature catégorielle.
- **Profil moyen** : `df.groupby("hour")["cnt"].mean().plot()` → forme
  typique de la journée (pic matin + soir, creux nuit).
- **Heatmap** : `df.groupby(["weekday", "hour"])["cnt"].mean()` puis pivot
  + `sns.heatmap` → carte 2D heure × jour.
- **Corrélations** : `df[num_cols].corr()` puis `sns.heatmap` (annot=True).
  ⚠️ `corr()` mesure une corrélation **linéaire** (Pearson) — une relation forte
  mais non-linéaire (comme heure ↔ demande) peut donner un coefficient faible.
  Et **corrélation ≠ causalité** : deux variables peuvent bouger ensemble sans
  lien de cause à effet.
- **Cycliques** : `hour` et `month` sont **circulaires** (heure 23 proche
  de l'heure 0). Si tu utilises un modèle linéaire, encode-les en **sin/cos**.

## Exemple minimal qui tourne

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("data/bike_sharing.csv")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. Distribution cible par saison
sns.boxplot(data=df, x="season", y="total_rentals",
            order=["winter", "spring", "summer", "fall"], ax=axes[0, 0])
axes[0, 0].set_title("Locations par saison")

# 2. Profil moyen par heure
df.groupby("hour")["total_rentals"].mean().plot(ax=axes[0, 1])
axes[0, 1].set_title("Profil moyen par heure (pic 17-19)")
axes[0, 1].set_ylabel("total_rentals moyen")

# 3. Scatter température vs cnt
sns.scatterplot(data=df.sample(2000), x="temperature_norm", y="total_rentals",
                alpha=0.3, ax=axes[1, 0])
axes[1, 0].set_title("Température vs locations")

# 4. Heatmap heure × weekday
pivot = df.pivot_table(values="total_rentals", index="weekday",
                       columns="hour", aggfunc="mean")
sns.heatmap(pivot, cmap="YlOrRd", ax=axes[1, 1])
axes[1, 1].set_title("Locations moyennes — heure × jour de semaine")

plt.tight_layout()
plt.show()
```

## Exercice guidé

Sur `bike_sharing.csv` :

1. `df.groupby("hour")["total_rentals"].mean().plot()` — repère les **deux pics**
   journaliers. À quoi correspondent-ils (indice : navetteurs) ?
2. Croise avec `is_working_day` (un groupby à deux niveaux) : les pics 8h/18h
   tiennent-ils le week-end ?
3. Note **2 features** que cette saisonnalité te donne envie de créer (ex.
   `is_rush_hour`, ou `hour` encodée en cyclique sin/cos).

**Attendu** : tu retrouves les observations listées ci-dessous, et tu sais dire
*pourquoi* `hour` est la variable la plus structurante du jeu.

> **Variable structurante** = une variable qui explique une **grande part des
> variations de la cible**. Ici, connaître l'**heure** permet déjà d'anticiper
> l'essentiel du niveau de demande (pic matin/soir, creux nuit) — bien plus que,
> par exemple, l'humidité.

## Observations attendues sur Bike Sharing

- **Pic** été (juillet-août), heures 17-19 (sortie de bureau)
- **Creux** hiver, heures 3-5 (nuit)
- **Weekend différent** : pas de pic 8h et 17h marqués, plutôt plateau journée
- **Corrélation forte** température ↔ cnt (positive)
- **Tendance** : 2012 > 2011 (croissance)

> 💡 **L'EDA ne sert pas qu'à comprendre les données — elle sert à émettre des
> hypothèses sur les modèles.** Ici, la forte non-linéarité (pics/creux selon
> l'heure, interactions weekend × heure) laisse présager qu'un modèle
> **linéaire** sera limité, et qu'un modèle à base d'**arbres / boosting**
> captera mieux ces interactions. C'est exactement l'hypothèse que le
> **benchmark** (mini-cours 04) va mettre à l'épreuve.

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| EDA globale sans conditionnement temporel | Tu rates la saisonnalité |
| Utiliser `casual_riders` ou `registered_riders` en feature | **Fuite** (composantes de la cible) — R² = 1.0 suspect |
| Pas d'encodage cyclique pour modèle linéaire | Linéaire incapable de capter la circularité (heure 23 ≠ heure 0) |
| Heatmap sans `pivot_table` | Tu obtiens un mur de chiffres illisible |
| Visualisations sans titre / sans interprétation | Inès Tabet ne sait pas quoi en faire |

## Pour aller plus loin

- **Seaborn — *Statistical relationships*** : <https://seaborn.pydata.org/tutorial/relational.html>
- **Pandas — *Time series functionality*** : <https://pandas.pydata.org/docs/user_guide/timeseries.html>

## Vérification

- [ ] ≥ 4 visualisations dans le notebook
- [ ] Au moins 1 conditionnement temporel (boxplot/courbe/heatmap)
- [ ] Paragraphe d'interprétation rédigé
- [ ] J'ai vérifié que **je n'utilise pas** `casual_riders` ou `registered_riders` en features

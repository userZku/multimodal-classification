# Grille de décision C4 — Mini-cours

> Brief associé : M4-B1
> Durée : ~15 min
> Pré-requis : avoir benchmarké 3+ modèles (mini-cours 04).

## Pourquoi cette techno ?

Tu as 3 modèles benchmarkés. Tu dois maintenant **choisir lequel
proposer à Inès Tabet**. Et pas seulement « lequel a la meilleure
métrique » — un choix de modèle implique des **trade-offs** :

- Précision vs vitesse d'inférence
- Précision vs explicabilité
- Train rapide vs train lent (impact CI/CD M5)
- Mémoire vs latence (déploiement edge ?)
- Maintenance fréquente vs modèle stable

**La grille de décision C4** est l'outil qui rend ces trade-offs
**explicites** — et qui devient le **livrable pédagogique majeur du
parcours**, réutilisé en M7, M8 et pour le notebook certif M9.

## Concepts clés

### Les 4 axes de la grille

> ⚠️ Les seuils ci-dessous sont des **heuristiques** (ordres de grandeur pour
> se repérer), pas des lois. Ils dépendent du type de donnée et de la tâche.
> Et les **foundation models / zero-shot** sont mentionnés en **anticipation
> de M4-B2 (vision, CLIP) et de M7-M8** — en M4-B1 tu restes sur le tabulaire
> (linéaire / arbre / boosting).

1. **Volume de données disponible** *(heuristiques)*
   - < 1 k : modèles linéaires — ou zero-shot foundation models *(→ M4-B2/M7)*
   - 1 k - 100 k : RF, boosting, transfer learning
   - > 100 k : boosting tuné, deep learning, foundation models fine-tunés

2. **Complexité du signal**
   - Linéaire : Ridge / Lasso (capte la tendance, rien de plus)
   - Non-linéaire faible : RandomForest, GradientBoosting
   - Non-linéaire forte : Boosting tuné, deep learning custom
   - Structurel (image, texte) : CNN, Transformer, Foundation model

3. **Contraintes métier**
   - Explicabilité ? (réglementaire ↔ ergonomique ↔ acceptable boîte noire)
   - Latence ? (< 10 ms ↔ < 100 ms ↔ > 1 s OK)
   - Coût ? (gratuit ↔ < 100 € / mois ↔ illimité)

4. **Maintenance attendue**
   - Jamais (modèle statique) : linéaire, foundation model zero-shot
   - Trimestrielle : RF, boosting (CI/CD M5 OK)
   - Continu : NN avec partial_fit, ou réentraînement programmé

### Cartographie modèles → axes

Cf. `ressources-publiques/grille_decision_C4.md` : une **amorce à trous**
(Axes 1-2 posés ; Axes 3-4, cartographie et cas types **vides exprès**). C'est
**vous, en restitution mercredi**, qui remplissez ces zones avec vos benchmarks
et vos *decision cards*.

## Construction collective mercredi 11h30-12h45

Format :
1. **Tour de table** : chacun présente sa *decision card* 4-5 min (≈ 36 min pour 8)
2. **Construction collective** sur Excalidraw partagé :
   - croix des 4 axes
   - post-its « modèles » placés (Ridge, RF, HGB)
   - verdict de chacun mappé sur la croix + cas type Bike Sharing
3. **Report** de la grille finale → archivée dans
   `ressources-publiques/grille_decision_C4.md` (v1.0)

**Géste pédagogique** : la grille **n'est pas un oracle**. C'est un
**support de raisonnement**. Tu te poses les 4 questions, tu **justifies**
ton choix.

## Exemple minimal — cas Bike Sharing, analyse axe par axe

| Axe | Lecture | Implication |
|---|---|---|
| Volume | ~17 k lignes | Boosting envisageable, foundation model superflu |
| Complexité | Saisonnalité (interactions heure×saison) | Linéaire suffit pas — non-linéaire requis |
| Explicabilité | Actuaire OK avec SHAP | RF ou HGB OK |
| Latence | Pas critique (tarif quotidien) | Tout OK |
| Maintenance | Drift saisonnier modéré | RF/HGB + CI/CD trimestriel (M5) |

**Verdict type** : **HistGradientBoostingRegressor** — rapide + précis +
SHAP-able. Argument chiffré : MAE 32 (vs 105 baseline), train 2 sec, latence
3 ms / 1 k.

## Exercice guidé — ta decision card personnelle

Tu rédiges `decision_card.md` **avant** la restitution collective. C'est
**ton point de vue** — il sera confronté aux autres pour construire la
grille commune.

Structure proposée :
1. Critères que tu privilégies (en ordre)
2. Modèles benchmarkés
3. Cas hypothétiques :
   - Si volume × 10 (170 k lignes), tu changerais ?
   - Si latence critique (< 5 ms), tu changerais ?
   - Si explicabilité réglementaire, tu changerais ?
4. Ce que tu veux apporter à la grille collective

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Choisir le modèle avec le meilleur MAE sans regarder les autres axes | Tu rates le contexte métier — un modèle 1% meilleur mais 50× plus lent = mauvais choix |
| Pas de cas hypothétique dans la decision card | Tu ne montres pas que tu maîtrises les trade-offs |
| Grille générique sans cas réel mappé | Inutile pédagogiquement — il faut **placer** Bike Sharing dessus |
| Vouloir une grille "définitive" | Elle évolue à chaque module — c'est normal |

## Pour aller plus loin

- **scikit-learn — *Choosing the right estimator*** : <https://scikit-learn.org/stable/machine_learning_map.html>
- **`ressources-publiques/grille_decision_C4.md`** — version initiale du parcours

## Vérification

- [ ] Mon `decision_card.md` est complété **avant** la restitution
- [ ] J'ai répondu aux 4 cas hypothétiques
- [ ] J'ai contribué activement à la **construction collective** mercredi
- [ ] La **grille commune** est archivée dans `ressources-publiques/`
- [ ] Je sais que la grille **évoluera** en M7-M8 (foundation models, LLM)

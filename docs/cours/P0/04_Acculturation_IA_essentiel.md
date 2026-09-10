# Acculturation IA — Mini-cours

> Brief associé : P0
> Durée de lecture : ~45 min
> Pré-requis : aucun (mini-cours de cadrage)

## Pourquoi cette techno ?

Avant de **faire de l'IA**, il faut **savoir de quoi on parle**. L'industrie utilise
le mot « IA » pour des techniques très différentes, des outils qui ne se ressemblent
pas, et des coûts qui varient d'un facteur 1 000.

Sur cette formation, tu seras amené·e à :

- intégrer un modèle déjà entraîné (M0)
- en réentraîner un (M1)
- en concevoir un (M4)
- déployer et monitorer (M5, M6)
- arbitrer entre plusieurs approches (M4, M7, M8)

Pour arbitrer, il faut **distinguer les familles d'IA** et **comprendre leurs coûts /
explicabilité / sobriété**. C'est l'objet de ce mini-cours.

⚠️ Tu n'es pas censé·e devenir data scientist. Tu es censé·e **savoir lire un cas
d'usage** et **savoir poser les bonnes questions**.

## Concepts clés

### 1. Apprentissage **supervisé** vs **non supervisé**

- **Supervisé** : on a des **étiquettes** (la « bonne réponse » connue pour chaque
  exemple). Le modèle apprend la fonction `X → y`.
  - **Régression** : prédire une valeur continue (prix, durée, score).
  - **Classification** : prédire une catégorie (spam / non-spam, criticité haute /
    moyenne / basse).
- **Non supervisé** : pas d'étiquettes. Le modèle découvre la structure cachée.
  - **Clustering** : regrouper les exemples similaires (segmentation client).
  - **Détection d'anomalies** : isoler ce qui sort du lot (fraude, défaut machine).
  - **Réduction de dimension** : compresser l'information (PCA, autoencoders).

> 80 % des cas en entreprise = supervisé.

### 2. **Transfer learning** et **foundation models**

- **Transfer learning** : on prend un modèle déjà entraîné sur **un grand corpus**
  (image, texte) et on l'**adapte** à notre tâche en réentraînant juste les dernières
  couches. Permet d'avoir de bons résultats avec **peu de données** et **peu de
  ressources**.
  - Ex : prendre un ResNet50 pré-entraîné sur ImageNet et l'ajuster sur 500 photos
    de défauts industriels.
- **Foundation model** : modèle pré-entraîné **très généraliste** sur d'énormes corpus
  (texte, image, multimodal). Utilisable directement en `zero-shot` (sans
  réentraînement), ou en `few-shot` (quelques exemples), ou via fine-tuning.
  - Ex : CLIP (image + texte), GPT-4, Llama, Mistral, Phi-3.

### 3. **LLM** (Large Language Models)

Modèles de génération de texte massifs (>1 milliard de paramètres). Tu connais
ChatGPT, Claude, Gemini. En entreprise, on parle aussi de **SLM** (Small Language
Models) : Llama 3 8B, Phi-3, Mistral 7B — déployables sur GPU modeste, voire CPU.

**Quand un LLM est-il pertinent ?**

- Compréhension de texte libre (résumé, classification thématique).
- Génération de texte structuré (extraction d'entités, JSON).
- Conversation, support, Q&A.

**Quand un LLM est-il une mauvaise réponse ?**

- Une **classification binaire** sur 20 features tabulaires : un Random Forest fera
  mieux pour 1000× moins cher.
- Une **prédiction numérique** (prix, durée) : un Gradient Boosting est le bon
  outil, pas un LLM.
- Une **détection d'anomalies** : Isolation Forest, autoencoder. Pas un LLM.
- Quand on a peu de données labellisées **et** une tâche très spécifique : commencer
  par du transfer learning, pas du LLM.

> **Règle pratique** : si tu peux résoudre le problème avec scikit-learn et 100 lignes
> de code, tu n'as pas besoin d'un LLM.
>
> ⚠️ **Inversement, ne tombe pas dans le dogme « LLM jamais »**. Le LLM est le bon outil pour :
>
> - **compréhension de langage libre** (résumé, extraction, classification thématique de texte) ;
> - **raisonnement multi-étapes** sur du texte non structuré (lecture de docs, synthèse contextualisée) ;
> - **génération de texte cohérent** (rédaction, reformulation, dialogue) ;
> - **extraction d'entités hétérogènes** où les regex craquent.
>
> Le bon réflexe n'est ni « LLM toujours » ni « LLM jamais », c'est :
> **« LLM si la tâche est langagière, ML classique sinon »**.

### 4. **RAG** et **agents** (panorama rapide)

- **RAG** (Retrieval-Augmented Generation) : on couple un LLM à une **base de
  connaissances vectorielle** pour qu'il réponde sur **tes documents internes** au
  lieu de halluciner. Très utile pour Q&A documentaire, support client.
- **Agent** : un LLM qui peut **utiliser des outils** (appeler une API, faire un
  calcul, interroger une BDD) et **planifier** plusieurs étapes. Ex : LangChain,
  LangGraph.

Ces deux notions seront approfondies en M7-M8 du parcours, **après** que tu aies
maîtrisé les bases ML classiques. Trop d'équipes IA aujourd'hui sautent cette étape
et empilent les agents sur des problèmes qui demandaient un Random Forest.

### 5. Critères de choix d'une approche IA

Quand un client te demande « est-ce qu'on peut mettre de l'IA ? », tu dois savoir
trier selon :

| Critère | Question à poser |
|---|---|
| **Coût** | Combien coûte l'entraînement ? l'inférence (€/1000 prédictions) ? |
| **Explicabilité** | Le métier doit-il comprendre les décisions du modèle ? |
| **Maintenance** | Combien de personnes peuvent maintenir cette stack à 3 ans ? |
| **Sobriété** | Conso énergétique ? CO2/prédiction ? Latence ? |
| **Conformité** | RGPD ? AI Act ? Secteur régulé ? Données sensibles ? |
| **Robustesse** | Que se passe-t-il avec une entrée bizarre / adversariale ? |

## Exemple minimal qui tourne (lecture)

Voici 5 mini-cas. Pour chacun, **identifie la famille IA pertinente** — note ta
réponse sur un brouillon **avant** d'ouvrir le corrigé.

| # | Cas |
|---|---|
| 1 | Une banque veut prédire si un client va rembourser un crédit |
| 2 | Une usine veut détecter les pièces défectueuses sur des photos de la chaîne |
| 3 | Une entreprise veut que ses employés puissent poser des questions sur les RH internes |
| 4 | Une mutuelle veut prévoir le coût total des sinistres du mois prochain |
| 5 | Un opérateur télécom veut segmenter ses 5M de clients pour le marketing |

<details>
<summary>🔒 <strong>Corrigé</strong> — clique pour révéler (après avoir réfléchi aux 5 cas)</summary>

| # | Famille IA |
|---|---|
| 1 | **Classification supervisée** — Random Forest, Gradient Boosting |
| 2 | **Vision + transfer learning** — CNN pré-entraîné (ResNet) + fine-tuning |
| 3 | **RAG** — vectorisation des docs RH + LLM (open source ou API) |
| 4 | **Régression supervisée** — séries temporelles / Gradient Boosting |
| 5 | **Clustering** (non supervisé) — K-means, GMM |

Aucune de ces 5 réponses n'est un LLM seul. Et c'est normal.

</details>

## Exercice guidé

À écrire dans la section dédiée du notebook livrable (cf. P0 — Tâche 4).

1. Avec tes mots, **3-5 lignes** : quelle est la différence entre **apprentissage
   supervisé** et **non supervisé** ? Donne un exemple métier de chaque.
2. Avec tes mots, **3-5 lignes** : à quoi sert le **transfer learning** ? Pourquoi
   est-il utile quand on a peu de données ?
3. Avec tes mots, **3-5 lignes** : pourquoi un **LLM n'est pas toujours la bonne
   réponse** à un problème métier ? Cite un cas où un LLM serait sur-dimensionné.

> Les réponses doivent être **rédigées par toi**. Pas du copier-coller de Wikipédia
> ni de ChatGPT. Mieux vaut une réponse imparfaite mais personnelle qu'une réponse
> parfaite recopiée — on lit la différence.

## Pour aller plus loin

- *Hands-On ML* (Aurélien Géron, 3ᵉ éd.) — chapitre 1 : panorama complet, lecture
  de référence pour la suite.
- *Machine Learning Workshop* (Packt, 2ᵉ éd.) — chapitres 1-3, ressource
  complémentaire fournie par la formatrice sur demande.
- Article Stanford « What is AI? » : https://hai.stanford.edu/ai-index/2024-ai-index-report
- Glossaire IA de la CNIL (FR) : https://www.cnil.fr/fr/intelligence-artificielle/glossaire-ia

## Vérification (checklist apprenant)

- [ ] Je sais distinguer apprentissage supervisé / non supervisé et donner un
      exemple métier de chacun.
- [ ] Je sais expliquer en 2 minutes ce qu'est un foundation model.
- [ ] Je peux citer **2 cas où un LLM est pertinent** et **2 cas où c'est une
      mauvaise idée**.
- [ ] J'ai rédigé mes 3 réponses dans le notebook livrable.
- [ ] Je connais au moins 3 critères pour choisir une approche IA (coût,
      explicabilité, sobriété, etc.).
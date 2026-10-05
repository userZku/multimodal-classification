# Fiche orale de certification CISIA

Support de préparation correspondant aux **24 pages du PDF partagé**. Les numéros ci-dessous sont ceux du PDF, et non ceux de l'ancien storyboard Markdown.

## Mon fil rouge

**Comment aider un conseiller à repérer les situations de chômage de longue durée, sans utiliser directement la nationalité et sans laisser le modèle décider seul ?**

Mon histoire suit quatre questions :

1. Quelles erreurs faut-il éviter et que permettent les données ?
2. Quel modèle choisir, avec quel compromis éthique ?
3. Quand faut-il demander une revue humaine ?
4. Comment rendre cette solution utilisable, observable et réversible ?

À chaque étape : **je me pose une question, je montre une preuve, je prends une décision, j'annonce sa limite**. Je ne lis pas les listes de composants : j'explique pourquoi ils sont nécessaires.

## Corrections à faire avant la soutenance

- **Slide 4 :** remplacer les proportions par classe 0 = **37,44 %**, classe 1 = **44,48 %**, classe 2 = **18,08 %**. Les valeurs 55 % et 27 % du PDF sont incorrectes.
- **Slides 10 à 12 et 24 :** distinguer la politique combinée **évaluée dans le notebook** de l'API actuelle. Le code vérifié utilise `ABSTENTION_THRESHOLD = 0.55` et uniquement la règle de faible confiance. La règle combinée à 0,70 n'est pas intégrée à l'API. Ne pas la présenter comme déjà déployée.
- **Slide 10 :** écrire `a_revoir`, sans accent. Les deux motifs d'escalade sont des conditions alternatives reliées par OU, pas des étapes successives : remplacer les flèches entre les blocs par un arbre de décision.
- **Slide 11 :** 80 % désigne la couverture de **10 erreurs critiques**, pas le rappel de toutes les personnes de classe 2. Une escalade ne garantit pas que le conseiller corrige effectivement l'erreur.
- **Slide 18 :** remplacer « sans promotion automatique » par **« sans remplacement inconditionnel du modèle »**. La promotion est automatisée, mais conditionnée par les garde-fous. La capture montre un cycle ignoré faute de feedbacks, pas un entraînement réussi.
- **Slide 21 :** elle répète les slides 19 et 20 ; la passer rapidement ou la retirer.
- **Pied de page :** remplacer la date `04/03/2026` et `Presentation Title` par la date de soutenance et le titre réel. Vérifier que la mention « internal use » convient au rendu et à sa diffusion.
- **Slide 14 :** la capture affiche encore « Portfolio ML Ops ». Prévoir une capture sans cette mention pour le rendu de certification.
- **Slides 8 et 9 :** les écarts 0,708 / 0,681 comparent les XGBoost de référence avant tuning. Ne pas confondre ces scores CV avec ceux du S2 optimisé ou du modèle actif de septembre.

## Repères pour 30 minutes

| Partie | Slides | Temps cible |
|---|---|---:|
| Sujet, données et protocole | 1 à 6 | 7 min |
| Métriques, choix et escalade | 7 à 12 | 9 min |
| API, interface, supervision et feedback | 13 à 18 | 9 min |
| Livraison, limites et conclusion | 19 à 24 | 5 min |

Les textes suivants sont une base orale, pas un script à réciter mot pour mot. Les définitions servent surtout à préparer les questions ; ne pas toutes les développer pendant les 30 minutes.

---

## Slide 1 - Classification multimodale

**Message à retenir :** je présente une aide à l'orientation, pas une décision automatisée sur l'usager.

**Ce que je peux dire :**

« Le sujet de cette certification est de prédire le délai de retour à l'emploi à partir d'informations socio-professionnelles et d'une synthèse d'entretien. Mon objectif est d'aider le conseiller à repérer les situations qui nécessitent davantage d'attention. Je vais vous montrer comment j'ai analysé les données, comparé les solutions, assumé un compromis éthique, puis construit une chaîne technique pour servir et surveiller le modèle. »

**Transition :** « Pour comprendre mes choix, il faut d'abord comprendre quelle erreur aurait la conséquence métier la plus grave. »

**Définition :** multimodal signifie ici combiner des données structurées en colonnes et du texte libre. Cela ne signifie pas que le projet traite aussi des images ou de l'audio.

## Slide 2 - Toutes les erreurs ne se valent pas

**Message à retenir :** une bonne moyenne ne suffit pas si les situations les plus fragiles passent inaperçues.

**Ce que je peux dire :**

« Le modèle distingue trois classes : un retour rapide, intermédiaire ou un risque de longue durée. L'erreur critique est de prédire un retour rapide pour une personne réellement en classe 2. Le risque est de sous-estimer son besoin d'accompagnement. C'est pour cela que j'examine cette erreur séparément du score global. Je parle d'un risque métier à prévenir, pas d'un impact social déjà mesuré sur le terrain. »

**Transition :** « Pour détecter ces situations, de quelles informations disposais-je ? »

**Définitions :** classification = attribution à une catégorie ; apprentissage supervisé = apprentissage sur des exemples dont la catégorie est connue ; erreur `2 -> 0` = classe réelle 2, classe prédite 0.

## Slide 3 - Les données disponibles

**Message à retenir :** les données sont riches, mais certaines posent une question de gouvernance.

**Ce que je peux dire :**

« Le jeu fourni contient 2 500 dossiers et 10 colonnes, dont la cible. Les informations comprennent l'âge, l'ancienneté, le diplôme, le métier visé, la situation administrative, la géographie et le texte de l'entretien. Je distingue les identifiants, les variables prédictives et la cible. La nationalité est présente dans les données sources et dans la comparaison expérimentale S1, mais elle est retirée du scénario S2 et du contrat d'inférence. »

**Transition :** « Avant de faire apprendre un modèle, j'ai vérifié la qualité et la répartition de ces données. »

**Définitions :** cible = réponse à apprendre, ici `classe_retour_emploi` ; feature = variable utilisée pour prédire ; variable catégorielle = valeur parmi des modalités ; variable sensible = dans ce projet, donnée présentant un risque de discrimination. Cette dernière expression ne remplace pas une qualification juridique précise au sens du RGPD.

## Slide 4 - Ce que l'analyse des données révèle

**Message à retenir :** l'analyse exploratoire transforme les constats en décisions.

**Ce que je peux dire, après correction du graphique :**

« La classe 2 représente 452 dossiers, soit 18,08 % du jeu. Les classes 0 et 1 représentent respectivement 37,44 % et 44,48 %. J'ai également observé des valeurs manquantes, des écarts selon la nationalité et un texte peu diversifié. Ces constats justifient l'imputation, le découpage stratifié et une vigilance sur les biais. Un écart statistique ne démontre pas à lui seul une causalité ou une discrimination du modèle. »

**Transition :** « Ces observations ne sont utiles que si la méthode d'évaluation reste fiable. »

**Définitions :** EDA = analyse exploratoire des données ; proxy = variable pouvant refléter indirectement une caractéristique exclue ; surapprentissage = apprendre des particularités du jeu plutôt qu'une règle qui généralise à de nouveaux dossiers.

## Slide 5 - Séparer apprentissage et évaluation

**Message à retenir :** apprendre et se tester doivent être deux opérations distinctes.

**Ce que je peux dire :**

« J'ai réservé 80 % des dossiers à l'apprentissage, soit 2 000 lignes, et 20 % à l'évaluation, soit 500 lignes. La stratification conserve approximativement les proportions des classes ; le test contient 90 personnes de classe 2. Les transformations apprennent leurs paramètres uniquement sur les données d'entraînement. Pendant la validation croisée, le pipeline ajuste aussi le prétraitement uniquement sur la partie d'apprentissage de chaque fold. »

« Le schéma représente la logique du protocole : le test est une branche réservée au moment du split, pas un jeu fabriqué après le choix du modèle. »

**Transition :** « Avec ce cadre commun, je peux comparer les contributions des différentes données. »

**Définitions :** split stratifié = séparation conservant les proportions des classes ; imputation = remplacement des valeurs manquantes ; encodage ordinal = ordre explicite pour le diplôme ; one-hot = colonnes indicatrices pour les catégories ; TF-IDF = représentation numérique des mots selon leur fréquence et leur caractère distinctif ; fuite de données = utilisation, pendant le choix ou l'apprentissage, d'informations qui devraient rester réservées à l'évaluation.

## Slide 6 - Pourquoi quatre scénarios ?

**Message à retenir :** je compare des hypothèses, pas seulement des algorithmes.

**Ce que je peux dire :**

« S1 combine toutes les modalités retenues, avec la nationalité. S2 retire cette variable. S3 mesure ce que le texte peut apporter seul. S4 examine les données tabulaires sans le texte. Le notebook teste ces scénarios avec plusieurs modèles : régression logistique, forêt aléatoire, XGBoost et LightGBM. Je veux comprendre d'où vient la performance et ce que coûte chaque choix. Attention : S4 n'est pas automatiquement un scénario sans nationalité ; c'est S2 qui impose cette exclusion. »

**Transition :** « Pour comparer ces solutions, il faut décider ce que signifie un bon résultat. »

**Définitions :** baseline = solution de référence ; régression logistique = classifieur linéaire simple ; Random Forest = ensemble d'arbres qui combinent leurs décisions ; XGBoost et LightGBM = méthodes de boosting, qui construisent successivement des arbres pour améliorer les prédictions.

## Slide 7 - Relier métriques et risque métier

**Message à retenir :** le score global et le risque critique répondent à des questions différentes.

**Ce que je peux dire :**

« Pour la qualité globale, je suis le F1 macro, qui donne le même poids aux trois classes. Pour le risque métier, je regarde le rappel de classe 2 et le nombre d'erreurs 2 vers 0. Le ROC-AUC complète la lecture du classement probabiliste. Enfin, la latence et le coût situent l'exploitation. Une bonne accuracy ne suffit pas : elle peut masquer les difficultés sur une classe minoritaire. »

**Transition :** « Voyons maintenant ce que ces indicateurs disent des quatre scénarios. »

**Définitions :** accuracy = proportion totale de prédictions correctes ; précision = parmi les dossiers prédits dans une classe, combien sont corrects ; rappel = parmi les dossiers réellement dans cette classe, combien sont détectés ; F1 = équilibre entre précision et rappel ; macro = moyenne donnant le même poids à chaque classe ; ROC-AUC = qualité de classement des scores, pas preuve que les probabilités sont bien calibrées ; p95 = valeur sous laquelle se trouvent 95 % des mesures.

## Slide 8 - Les résultats ne désignent pas un vainqueur unique

**Message à retenir :** maximiser le F1 ne suffit pas à décider de la production.

**Ce que je peux dire :**

« En validation croisée, le XGBoost S1 atteint environ 0,708 de F1 et 0,572 de rappel classe 2. Le XGBoost S2 de référence atteint 0,681 et 0,558. Le texte seul a un rappel relativement élevé, mais un F1 global inférieur. Le comparateur tabulaire compte moins d'erreurs 2 vers 0 dans ce test, sans être le meilleur sur tous les axes. Ce tableau me pousse à arbitrer, pas à retenir mécaniquement le plus grand nombre. »

« Les barres décrivent la validation croisée ; les effectifs 9, 10, 12 et 8 décrivent le test. Ils ne viennent pas du même calcul. Les scores CV de référence S2 ne sont pas ceux du S2 optimisé. »

**Transition :** « Le compromis que je dois assumer est celui de l'exclusion de la nationalité. »

**Définitions :** validation croisée = plusieurs entraînements et évaluations sur des sous-ensembles du train ; fold = un de ces sous-ensembles ; moyenne CV = moyenne des résultats des folds, pas résultat final sur le test.

## Slide 9 - Assumer le coût du choix éthique

**Message à retenir :** je mesure le compromis au lieu de le cacher.

**Ce que je peux dire :**

« À configuration de référence comparable, retirer la nationalité fait passer le F1 de 0,708 à 0,681 : la baisse est de 0,027. Le rappel classe 2 baisse de 0,014. J'accepte cette perte mesurée pour ne pas exploiter directement la nationalité dans l'orientation. Cela ne garantit pas l'absence de biais : l'âge, la géographie ou les formulations du conseiller peuvent conserver des signaux indirects. »

**Transition :** « Exclure la variable sensible règle une question de conception ; il reste à traiter les erreurs graves du modèle retenu. »

**Définitions :** delta = différence entre deux valeurs ; baisse absolue de 0,027 = 2,7 points sur une échelle de 0 à 100, pas une baisse relative de 2,7 % ; non-discrimination = exigence à contrôler au-delà du simple retrait d'une colonne.

## Slide 10 - Ajouter un mécanisme de revue humaine

**Message à retenir :** le classifieur et la politique de décision sont deux éléments distincts.

**Ce que je peux dire :**

« Le modèle produit une classe et des probabilités. J'ai étudié deux motifs de revue humaine : une confiance insuffisante, ou une prédiction rapide qui conserve une probabilité de classe 2 d'au moins 0,20. La politique combinée relie ces conditions par OU. Elle est évaluée dans le notebook pour réduire les erreurs critiques qui resteraient sans revue. Elle ne transforme pas automatiquement une prédiction erronée en prédiction correcte. »

« Je distingue cette expérimentation de l'API actuelle : celle-ci applique encore la règle simple de confiance inférieure à 0,55. La politique combinée à 0,70 est évaluée et recommandée, mais pas encore branchée dans le service. »

**Transition :** « Le choix du seuil doit lui aussi reposer sur une méthode d'évaluation séparée du test. »

**Définitions :** confiance = plus grande probabilité prédite, sans garantie de certitude ; abstention = signaler qu'une revue est nécessaire ; HITL = intervention humaine dans le processus ; risk-gate = condition supplémentaire ciblant un risque métier.

## Slide 11 - Choisir le seuil avec des prédictions OOF

**Message à retenir :** je règle la politique sur le train, puis j'en examine le résultat sur le test.

**Ce que je peux dire :**

« Je divise le train en cinq folds. Pour chaque dossier, j'obtiens une prédiction faite par un modèle qui n'a pas appris sur ce dossier. Ce sont les prédictions out-of-fold. Je teste ensuite la grille de seuils sur ces prédictions. Avec une limite technique d'escalade de 41 %, et une couverture minimale de 70 % des erreurs critiques OOF, la règle combinée retient 0,70. »

« L'escalade est de 40,2 % et la couverture de 72,5 % en OOF. Sur le test, 200 dossiers sur 500 sont orientés vers une revue ; cela capture 8 des 10 erreurs critiques. Deux restent non escaladées. Je ne dis pas que le rappel de classe 2 atteint 80 %, ni que les huit erreurs ont été corrigées par un conseiller : je mesure leur signalement. »

**Transition :** « Cette règle donne une recommandation concrète, mais aussi une charge humaine à assumer. »

**Définitions :** OOF = prédictions hors du fold d'apprentissage ; couverture critique = erreurs 2 vers 0 escaladées / toutes les erreurs 2 vers 0 ; taux d'escalade = dossiers escaladés / tous les dossiers ; calibration du seuil = choix de la règle, à distinguer de la calibration des probabilités.

**Si le jury approfondit :** les hyperparamètres ont été choisis avec la CV du train ; l'OOF obtenu n'est pas une validation imbriquée indépendante de ce choix. De plus, le test avait déjà été exploré dans une version antérieure. La procédure actuelle ne choisit plus le seuil sur le test, mais je ne présente pas ce test historique comme un holdout jamais consulté. Une confirmation externe serait nécessaire pour une évaluation complètement indépendante.

## Slide 12 - Formuler la recommandation

**Message à retenir :** le choix porte sur un modèle, des données et des conditions d'usage.

**Ce que je peux dire :**

« Je retiens S2 et XGBoost, avec la nationalité exclue et les deux modalités conservées. L'optimisation privilégie le rappel de classe 2. La recommandation métier est d'ajouter la politique combinée évaluée, sous réserve de pouvoir traiter environ 40 % des dossiers en revue humaine. Le modèle S2 est servi dans l'API ; la nouvelle politique reste à intégrer. Un dossier non escaladé reste une proposition, pas une décision administrative autonome. »

**Transition :** « Une recommandation dans un notebook doit ensuite devenir un service utilisable. »

**Définitions :** hyperparamètre = réglage choisi avant l'apprentissage ; tuning = recherche de ces réglages ; production = ici service de démonstration local, pas déploiement attesté dans le SI d'une agence.

## Slide 13 - L'API comme contrat de service

**Message à retenir :** le modèle peut être appelé avec des entrées et des réponses définies.

**Ce que je peux dire :**

« FastAPI reçoit un dossier, valide ses champs et appelle le pipeline chargé en mémoire. La réponse contient la classe, la confiance, le statut, la version du modèle et un identifiant de requête. Les autres routes permettent de vérifier la santé, de consulter les métriques, de lancer un réentraînement ou de restaurer un modèle. L'intérêt n'est pas le nombre de routes : c'est de rendre l'usage contrôlable et traçable. »

**Transition :** « Ce contrat technique doit aussi être compréhensible pour son utilisateur. »

**Définitions :** API = interface permettant à deux logiciels d'échanger ; endpoint = adresse d'une fonction du service ; GET = lecture ; POST = envoi de données ou demande d'action ; payload = contenu envoyé ; JSON = format structuré d'échange ; Swagger = documentation interactive de l'API ; `request_id` = identifiant d'un appel, pas identifiant personnel de l'usager.

## Slide 14 - Montrer une prédiction et son incertitude

**Message à retenir :** l'interface montre aussi les raisons de ne pas laisser passer la proposition sans revue.

**Ce que je peux dire :**

« Dans cette capture, le dossier retourne une classe 1 avec 47 % de confiance. Ce score est inférieur au seuil de l'API, 0,55 ; l'interface affiche donc une revue humaine recommandée. On voit également la version et le request_id, utiles pour relire l'appel. Le formulaire et l'historique démontrent le parcours d'inférence. Les boutons de réentraînement et rollback sont des fonctions d'administration de la démonstration, pas des droits que je donnerais nécessairement à tous les conseillers. »

**Transition :** « Cet écran s'appuie sur plusieurs composants ; je vais montrer comment ils échangent. »

**Définitions :** UI / IHM = interface utilisateur ; front-end = partie visible ; back-end = service qui traite l'appel ; historique d'inférences = traces des prédictions passées.

## Slide 15 - Lire l'architecture par parcours

**Message à retenir :** suivre un dossier est plus utile que réciter toutes les boîtes du schéma.

**Ce que je peux dire :**

« Je lis ce schéma en trois parcours. D'abord, le dataset permet l'entraînement d'un artefact, chargé par l'API et interrogé par l'interface. Ensuite, les appels produisent des logs et des métriques pour l'observation. Enfin, un retour terrain est joint aux données de la requête et permet d'entraîner un candidat. Ce candidat est comparé au modèle actif avant remplacement. Le schéma décrit la réalisation locale ; il ne démontre pas une connexion réelle au référentiel national des usagers. »

**Transition :** « Le premier besoin d'exploitation est de détecter ce qui se passe dans le service. »

**Définitions :** artefact = fichier issu de l'entraînement, ici pipeline sérialisé ; inférence = utilisation du modèle pour prédire ; JSONL = un objet JSON par ligne de journal ; SQLite = base de données stockée dans un fichier ; jointure = rapprochement de données grâce à une clé commune.

## Slide 16 - Observer sans confondre activité et qualité

**Message à retenir :** le monitoring rend le service visible, mais ne remplace pas les vraies étiquettes terrain.

**Ce que je peux dire :**

« Dans cette capture, le service est UP, les requêtes n'affichent pas d'erreur et la latence p95 affichée est d'environ 29 ms. Le dashboard montre également les classes prédites, la confiance et le taux d'abstention. Ce sont des observations sur la fenêtre de trafic simulé de la capture, pas une garantie pour toutes les charges. Le F1 affiché, 0,713, est une métrique enregistrée du modèle actif : ce n'est pas un F1 recalculé en direct à partir des requêtes. »

« Pour mesurer une baisse de qualité réelle, il faut joindre les prédictions aux labels terrain. Une variation de confiance ou des classes prédites est un signal à examiner, pas une preuve automatique de dérive de performance. »

**Transition :** « À cette observation du service, j'ajoute une trace des expériences qui ont produit les modèles. »

**Définitions :** Prometheus = collecte de métriques ; Grafana = visualisation de ces métriques ; compteur = total d'événements ; histogramme = répartition de mesures ; drift = changement des données ou de leur relation avec la cible ; latence = durée d'une réponse.

## Slide 17 - Un réentraînement peut réussir tout en étant rejeté

**Message à retenir :** MLflow permet d'expliquer une décision, même quand le nouveau modèle n'est pas promu.

**Ce que je peux dire :**

« Cette capture est un exemple concret de rejet. Le candidat a un F1 d'environ 0,695 contre 0,706 pour la production, et un rappel classe 2 de 0,489 contre 0,544. Son rappel baisse d'environ 5,6 points ; il ne respecte pas la politique de promotion. Le run est marqué Finished parce que l'exécution s'est terminée, mais son résultat métier est rejected. Les sept feedbacks joints et les 2 007 lignes d'entraînement sont également tracés. »

« Cela ne signifie pas que MLflow a automatiquement recalibré le modèle, ni que tous les artefacts sont dans un registre de modèles : je montre le tracking réellement utilisé. »

**Transition :** « Ce rejet illustre la règle de contrôle que je vais détailler. »

**Définitions :** run = une exécution suivie ; tracking = enregistrement de paramètres, métriques et fichiers ; tag = étiquette de contexte ; candidat = modèle entraîné mais pas encore actif ; Finished = exécution achevée, pas validation de la qualité.

## Slide 18 - Améliorer sans remplacer aveuglément

**Message à retenir :** automatisation ne signifie pas promotion systématique.

**Ce que je peux dire :**

« Un feedback est rattaché à la prédiction grâce au request_id. Le candidat est entraîné puis comparé à la production sur le même jeu de référence figé. La politique contrôle d'abord le rappel de classe 2, puis le F1. Il existe aussi un garde-fou sur le nombre de feedbacks joints. Si le candidat est accepté, l'ancien modèle est archivé ; sinon, la production reste inchangée. Le rollback permet de restaurer une version archivée. »

« La capture du cron montre six retours non consommés alors que le seuil de déclenchement est 200 : le cycle se termine en SKIP. C'est un résultat normal qui démontre le garde-seuil, pas un entraînement ou une promotion. La capture MLflow précédente illustre, elle, un cycle réellement exécuté et rejeté. »

**Transition :** « Ces étapes doivent être répétables au-delà de mon environnement de développement. »

**Définitions :** feedback = classe réelle ou annotation validée après prédiction ; reference_set = jeu figé pour comparer les versions, ici 500 dossiers dont 90 de classe 2 ; promotion = activation du candidat ; rollback = restauration d'une version précédente ; cron = planification périodique ; SKIP = cycle ignoré normalement, sans apprentissage.

**Si le jury demande les règles :** tolérance de baisse du rappel = 0,005, soit 0,5 point ; tolérance de F1 = 0,01, soit 1 point, avec exception si le gain de rappel dépasse 0,01. Le garde-fou de volume exige 20 feedbacks joints pour une promotion hors bootstrap ; c'est distinct des 200 retours déclenchant le cron. Ces règles sont des heuristiques, pas un test de significativité statistique. Réutiliser souvent le reference_set pour sélectionner les versions expose aussi à un surajustement progressif à ce jeu.

## Slide 19 - Docker : construire un environnement transportable

**Message à retenir :** je peux reconstruire les services à partir de leur définition.

**Ce que je peux dire :**

« Docker Compose décrit les services et leurs connexions : API, MLflow, Prometheus, Grafana et réentraînement planifié. La sortie affichée montre la construction réussie des trois images locales API, MLflow et retrain-cron. Prometheus et Grafana utilisent des images existantes. Cette sortie prouve le build ; les captures du service apportent une preuve d'exécution à une autre étape. Le build seul ne prouve pas que tout fonctionne. »

**Transition :** « J'ai également automatisé les contrôles déclenchés par les évolutions du code. »

**Définitions :** image Docker = paquet servant à lancer un service ; conteneur = instance en exécution d'une image ; Dockerfile = recette de construction ; Compose = définition de plusieurs services ; volume = stockage conservé indépendamment du conteneur.

## Slide 20 - GitHub Actions : vérifier et publier

**Message à retenir :** chaque modification peut être soumise à une chaîne de vérifications automatisées.

**Ce que je peux dire :**

« La capture montre un workflow réussi pour le commit 9d3d644 sur main, en 7 minutes 56 secondes. Il exécute les tests, un entraînement de vérification, le build et la publication de l'image. Le lint est présent mais non bloquant dans le workflow actuel. Le déploiement est conditionnel : un job vert peut correspondre à une étape ignorée si le webhook n'est pas configuré. Je ne présente donc pas ce vert comme la preuve d'un déploiement réel chez l'agence. »

**Transition :** « Docker prépare l'environnement ; la CI vérifie et prépare sa livraison. »

**Définitions :** CI = intégration continue, vérifications automatiques du code ; CD = livraison ou déploiement continus selon la configuration ; workflow = processus automatisé ; job = groupe d'étapes ; smoke test = vérification minimale qu'une fonction essentielle s'exécute ; lint = analyse de qualité du code ; GHCR = registre d'images de GitHub ; commit = version enregistrée du code.

## Slide 21 - Relier environnement et livraison

**Message à retenir :** les deux preuves précédentes ont des rôles différents et complémentaires.

**Ce que je peux dire en 15 à 20 secondes :**

« Cette slide résume les deux couches : Compose décrit l'environnement local, GitHub Actions automatise les contrôles et la publication. Ensemble, ils rendent le livrable reconstructible et traçable. Les mêmes vérifications restent nécessaires avant un hébergement réel. »

**Transition :** « Mais une chaîne technique opérationnelle ne fait pas disparaître les limites métier et réglementaires. »

**Conseil :** retirer cette slide si le temps manque ; elle reprend les deux précédentes.

## Slide 22 - Ne pas confondre garde-fous et garanties

**Message à retenir :** j'explicite les conditions d'un usage responsable, sans annoncer une conformité totale.

**Ce que je peux dire :**

« La nationalité est exclue de S2, les identifiants ne sont pas utilisés pour prédire, les appels sont journalisés et l'incertitude est visible. Mais les proxys et les textes peuvent encore porter des biais. La capacité humaine à absorber 40 % d'escalade doit être validée. Il reste également à durcir l'accès à l'API et à définir la conservation des logs. Retirer une colonne et rédiger une documentation RGPD ne suffisent pas à certifier la conformité juridique de tout le système. »

**Transition :** « En tenant compte de ces limites, voici ce que le projet livre effectivement. »

**Définitions :** RGPD = cadre européen de protection des données personnelles ; minimisation = ne traiter que les données nécessaires ; pseudonymisation = remplacer un identifiant sans rendre toute réidentification impossible ; authentification = vérifier qui appelle ; autorisation = vérifier ses droits ; TLS = chiffrement du transport.

## Slide 23 - Ce qui est livré et ce qui est recommandé

**Message à retenir :** distinguer réalisation technique, évaluation expérimentale et validation terrain.

**Ce que je peux dire :**

« Le livrable comprend le notebook, la comparaison des scénarios, le modèle S2, l'API, l'interface, Docker, le monitoring, le tracking et la boucle de réentraînement avec historique et rollback. La politique combinée est évaluée dans le notebook ; elle doit encore être alignée avec le service. L'usage est démontré localement et documenté, mais pas validé en situation réelle dans une agence. C'est cette distinction qui rend la présentation défendable. »

**Transition :** « Je peux donc conclure en revenant à la question initiale, plutôt qu'à une liste d'outils. »

**Définition :** MLOps = pratiques qui relient apprentissage, livraison, suivi et gestion des versions d'un système de machine learning.

## Slide 24 - Conclusion et questions

**Message à retenir :** mon résultat est un compromis mesuré, accompagné de moyens de contrôle.

**Ce que je peux dire :**

« Je suis parti d'une erreur métier à éviter : sous-estimer une situation de longue durée. J'ai comparé les solutions, accepté une baisse mesurée de score pour exclure la nationalité et évalué une politique qui dirige davantage d'erreurs critiques vers une revue humaine. J'ai ensuite construit un service local traçable, observable et réversible. Ma recommandation est S2 avec une politique d'escalade humaine, en distinguant son évaluation dans le notebook de son intégration encore nécessaire dans l'API. »

« Je ne présente pas une IA qui décide seule. Je présente une aide à la décision dont les compromis et les limites sont visibles. Je suis prêt à répondre à vos questions. »

---

## Mes chiffres de secours

| Question | Réponse courte |
|---|---|
| Combien de données ? | 2 500 dossiers, 10 colonnes sources, dont la cible. |
| Répartition réelle ? | 936 classe 0 ; 1 112 classe 1 ; 452 classe 2. |
| Taille du split ? | 2 000 train, 500 test ; 90 vrais classe 2 dans le test. |
| Coût de l'exclusion, avant tuning ? | F1 CV : 0,708 -> 0,681 ; rappel classe 2 : 0,572 -> 0,558. |
| Règle simple à 0,55 dans le notebook ? | 3 erreurs critiques sur 10 escaladées ; 19,8 % des dossiers escaladés. |
| Règle combinée choisie ? | Seuil 0,70, OU prédiction 0 avec P(classe 2) >= 0,20. |
| Résultat OOF ? | Environ 40,2 % d'escalade et 72,5 % de couverture critique. |
| Résultat test de cette règle ? | 200/500 dossiers escaladés, 8/10 erreurs critiques signalées ; 2 non escaladées. |
| API actuelle ? | Seuil simple 0,55 ; politique combinée non intégrée. |
| Cron local ? | Toutes les 6 heures, seuil de 200 retours non consommés. |
| Workflow retrain GitHub ? | Quotidien à 3 h UTC et lancement manuel possible. |
| Vert signifie promotion ? | Non : SKIP, rejet et promotion sont des résultats possibles ; Finished signifie exécution terminée. |

## Réponses aux questions difficiles

**Pourquoi ne pas choisir S1 si son score est meilleur ?**

« Parce que mon critère de choix inclut le risque de discrimination directe. Je mesure le coût de l'exclusion et je conserve S1 comme comparaison, pas comme modèle de service. »

**Pourquoi garder l'âge alors que vous retirez la nationalité ?**

« Je l'ai conservé pour sa pertinence socio-professionnelle dans ce cas d'usage, en le considérant comme un facteur potentiel de biais. Ce choix nécessite un audit par tranche d'âge ; il ne dispense pas d'une justification métier et juridique. »

**Est-ce que votre système corrige 80 % des erreurs ?**

« Non. Dans le test, la règle signale pour revue huit des dix erreurs 2 vers 0. Je n'ai pas mesuré le taux réel de correction par des conseillers. »

**Est-ce que la confiance de 80 % veut dire 80 % de chances d'avoir raison ?**

« Pas nécessairement. C'est un score du modèle. Pour interpréter ce score comme une probabilité fiable, il faudrait vérifier et éventuellement calibrer les probabilités. »

**Le modèle est-il en production ?**

« Il est servi dans une stack locale conteneurisée de démonstration. Je ne prétends pas qu'il est déployé dans le SI réel de l'agence. »

**Pourquoi la latence du notebook et celle de Grafana sont-elles différentes ?**

« Le notebook mesure un temps de traitement de batch divisé par le nombre de dossiers ; ce n'est pas le p95 de requêtes individuelles. Grafana mesure la latence instrumentée de l'API. Ces mesures n'ont pas le même périmètre et ne doivent pas être assimilées. »

**Le coût CPU annoncé est-il un coût d'hébergement réel ?**

« Non. C'est une estimation illustrative sous une hypothèse de prix, pas une facture. Le temps mur mesuré ne représente pas directement les secondes CPU, surtout avec du parallélisme. Il faut intégrer les ressources allouées, le stockage, les services annexes et le coût de disponibilité pour chiffrer l'hébergement. »

**La promotion refuse-t-elle tous les petits gains statistiques ?**

« Non. Elle applique des tolérances de métriques et un seuil de volume des feedbacks. Ce ne sont pas des intervalles de confiance ni des tests statistiques de significativité. »

## Mots à remplacer quand je bloque

| Terme | Formulation simple à l'oral |
|---|---|
| Features | Informations utilisées pour prédire |
| Preprocessing | Préparation des données |
| Fit | Apprentissage des paramètres |
| Transform | Application de la préparation déjà apprise |
| Pipeline | Chaîne de préparation et de prédiction |
| Stratifié | Qui conserve la proportion des classes |
| Fold | Un des groupes de la validation croisée |
| OOF | Prédiction d'un dossier par un modèle qui ne l'a pas appris |
| Recall | Part des situations réelles que le modèle détecte |
| Inférence | Calcul d'une prédiction |
| Endpoint | Fonction accessible par une adresse de l'API |
| Artefact | Fichier du modèle et de sa préparation |
| Monitoring | Surveillance du service et de son comportement |
| Tracking | Historique des expériences et de leurs résultats |
| Retrain | Réentraînement sur les données disponibles |
| Promotion | Activation d'un modèle candidat |
| Rollback | Retour à une version précédente |
| CI/CD | Vérification et livraison automatisées du code |

**Dernier repère :** si je ne sais pas répondre, je distingue ce qui est mesuré, ce qui est implémenté et ce qui reste une hypothèse. Je n'invente pas une garantie pour combler une hésitation.
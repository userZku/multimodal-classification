# Fiche orale de certification CISIA

Script à prononcer pour le **PPTX v2 (31 slides)**. Les textes entre guillemets sont une base mot pour mot ; les repères en dehors des guillemets servent à préparer les questions.

## À régler avant la soutenance

- Le PPTX contient 31 slides, mais le PDF actuel en contient 30 : la slide 29 du PPTX (« Les garde-fous réduisent le risque… ») n’apparaît pas dans le PDF ; la page 29 du PDF correspond à la slide 30 du PPTX. Le PDF et le PPTX ne sont donc pas alignés. Réexporter le PDF ou décider explicitement quel support sera projeté. Cette fiche suit l’ordre du PPTX.
- La couverture porte la date 14/10/2026 et les pieds de page 12/10/2026. Harmoniser les dates.
- La slide 14 est intitulée « SHAP », mais le graphique visible correspond à l’importance native XGBoost (`feature_importances_`) du notebook, pas à une explication SHAP. Avant l’oral, soit remplacer l’image par une vraie analyse SHAP, soit renommer la slide et la présenter comme une importance native. Ne pas appeler ce graphique « SHAP ».
- Le PPTX final affirme « S2 + XGBoost ». Le récit doit être honnête : XGBoost a été sélectionné initialement parce qu’il obtenait le meilleur F1 macro en S2, pas parce qu’il avait le meilleur rappel de classe 2. Avec le recul, un Random Forest ou une régression logistique aurait mérité d’être réévalué. Ne prétends pas que ce nouveau choix a déjà été entraîné ou validé.

## Fil rouge

« Mon projet classe les dossiers selon le délai potentiel de retour à l’emploi. Comme ce tri peut influer sur l’accompagnement proposé, je me suis intéressé aux erreurs, à la sélection du modèle et aux conditions d’une revue humaine. Je vais aussi distinguer ce que j’ai mesuré, ce qui fonctionne dans ma démonstration locale et ce qui reste à valider avant tout usage réel. »

## Script des slides

### Slide 1 — Couverture

« Bonjour. Je vais vous présenter mon projet d’orientation multimodale des demandeurs d’emploi. Je vais partir du besoin métier, puis expliquer les données, les choix de modèles et les limites de la solution. »

### Slide 2 — Cas d’usage et cadre réglementaire

« Ce modèle peut influencer le type d’accompagnement proposé à une personne. Il doit donc rester une aide : le conseiller doit pouvoir confirmer, corriger ou contester la recommandation. L’AI Act et le RGPD sont des cadres à examiner avec les personnes compétentes. Je ne conclus pas moi-même que le système est ou n’est pas “à haut risque” : cela dépend de sa finalité et de son usage effectif. Je distingue aussi trois notions : une donnée personnelle au sens du RGPD, une catégorie particulière de données au sens de son article 9, et une caractéristique qui doit être protégée contre la discrimination. Âge et nationalité sont des données personnelles et peuvent soulever des enjeux de discrimination ; ils ne sont pas automatiquement des catégories particulières au sens de l’article 9. La nationalité peut toutefois, selon le contexte, révéler l’origine ethnique ; cette qualification doit être examinée avec le DPO ou le juriste. »

### Slide 3 — L’erreur critique

« Les trois classes correspondent à un retour rapide, intermédiaire ou à un risque de dépasser douze mois. L’erreur que je surveille en priorité est une personne réellement en classe 2 prédite en classe 0 : le dossier pourrait alors ne pas être priorisé. Je l’appelle critique en raison de cette conséquence possible ; je n’ai pas mesuré une perte de chance réelle chez des usagers. »

### Slide 4 — Données structurées, texte et cible

« J’ai 2 500 dossiers et dix colonnes, avec des informations numériques, catégorielles, une synthèse d’entretien et la classe à prédire. La nationalité hors UE est présente dans le jeu source, mais je l’ai retirée des entrées de S2 pour éviter de faire dépendre directement le tri de cette caractéristique. J’ai aussi exclu l’identifiant technique et le code communal brut des variables de prédiction. L’âge, lui, reste utilisé : c’est une donnée personnelle qui peut soulever un enjeu de discrimination, pas une variable sans risque. J’explique ce choix et sa limite dans l’audit. »

### Slide 5 — Répartition et premiers risques

« La classe 2 représente 18,08 % des dossiers, contre 37,44 % pour la classe 0 et 44,48 % pour la classe 1. Ce déséquilibre m’oblige à regarder le rappel de la classe 2, et pas seulement un score global. J’ai aussi repéré des écarts entre groupes et des textes répétitifs ; ce sont des signaux à étudier, pas des preuves de causalité ou de discrimination du modèle. »

### Slide 6 — Valeurs manquantes et imputation

« J’ai repéré 84 diplômes manquants, soit 3,36 %. Dans le pipeline actuel, une valeur catégorielle manquante est remplacée par la modalité la plus fréquente ; pour le diplôme, c’est “Bac”. Cela décrit le traitement informatique, pas le diplôme réel de la personne : une case vide ne veut dire ni “Bac”, ni “sans diplôme”. Il faudrait vérifier le sens du blanc dans la source et comparer une modalité “inconnu” ou un indicateur de valeur manquante. »

### Slide 7 — OOF et réserve sur le test

« J’ai séparé 2 000 dossiers d’apprentissage et 500 dossiers de test. Dans le train, la validation croisée en cinq groupes permet de prédire chaque dossier avec un modèle qui ne l’a pas appris : ce sont les prédictions OOF. Le prétraitement est réappris dans chaque groupe pour éviter la fuite de données. Elles servent à comparer et à choisir sans régler directement le seuil sur le test. J’ai aussi transformé le code INSEE communal en département et exclu le code communal brut du modèle. Le test a toutefois été consulté dans une version antérieure ; je ne le présente donc pas comme totalement vierge. »

### Slide 8 — Comparaison des modèles

« Cette table compare quatre modèles dans chacun des scénarios. Chaque case donne le F1 macro puis le rappel de la classe 2, en validation croisée et avant le tuning final. En S2, le meilleur F1 de la grille est celui de XGBoost, à 0,681. Le meilleur rappel est celui de Random Forest, à 0,694 ; la régression logistique atteint 0,674, contre 0,558 pour XGBoost. Le modèle gagnant dépend donc du critère retenu. »

### Slide 9 — S1, toutes les variables

« S1 est ma référence avec toutes les variables, y compris la nationalité. Il obtient un F1 macro de 0,708 et un rappel de classe 2 de 0,572 en validation croisée. Le test compte neuf erreurs `2→0`. Je garde ce scénario comme point de comparaison, pas comme le choix de conception, car il utilise directement la nationalité. »

### Slide 10 — S2, sans nationalité

« S2 retire la nationalité des variables utilisées pour prédire, mais conserve l’âge et les autres informations du dossier ainsi que le texte. Son F1 macro est de 0,681 et son rappel de classe 2 de 0,558 en validation croisée ; le test compte dix erreurs `2→0`. Je préfère dire “S2 sans nationalité” plutôt que “sans variable sensible” : l’âge reste dans le modèle, et d’autres proxys peuvent subsister. »

### Slide 11 — S3, texte seul

« S3 ne conserve que la synthèse d’entretien. Le rappel de classe 2 affiché est de 0,661 et le F1 macro de 0,635 en validation croisée. Il montre que le texte contient un signal, mais il compte douze erreurs `2→0` sur le test et le texte est peu diversifié. Le texte peut aussi refléter les choix de rédaction et les biais des conseillers ; je ne le traite donc pas comme une source neutre. »

### Slide 12 — S4, tabulaire seul

« S4 retire le texte et utilise les colonnes tabulaires. Son F1 macro est de 0,672, son rappel classe 2 de 0,589 en validation croisée et il compte huit erreurs `2→0` sur le test. Mais le S4 actuel conserve la nationalité. Il ne respecte donc pas la même contrainte que S2, et deux erreurs d’écart sur ce petit nombre ne suffisent pas à établir une supériorité robuste. »

### Slide 13 — Résultat test de S2 + XGBoost

« Après le tuning effectué sur XGBoost, le résultat test affiché est une accuracy de 0,730, un F1 macro de 0,704, un rappel classe 2 de 0,533 et un ROC-AUC macro de 0,871. Sur les 90 dossiers réellement en classe 2, le modèle en retrouve 48 et en manque 42. Dix des 90 sont prédits classe 0, l’erreur prioritaire ; 32 sont prédits classe 1. Le test a déjà été consulté auparavant : ces chiffres décrivent cet échantillon, pas une performance indépendante garantie. »

### Slide 14 — Interprétation globale / SHAP

**Correction préalable :** le visuel actuellement visible est une importance native XGBoost, pas SHAP. Si tu le gardes, renommer la slide et dire :

« Le graphique montre l’importance native attribuée aux variables par XGBoost. Les variables catégorielles et le texte ressortent dans cette mesure. Ce graphique ne me dit pas si une variable augmente ou diminue la probabilité de classe 2, ne démontre aucune causalité et n’est pas une analyse SHAP. »

**Si un vrai graphique SHAP est inséré avant la soutenance, remplacer par :**

« Cette analyse SHAP résume comment les variables contribuent aux sorties du modèle pour la classe 2. Elle décrit le comportement appris par le modèle, pas les causes du retour à l’emploi ni une justification suffisante pour une décision administrative. »

### Slide 15 — La revue humaine se déclenche par une règle OU

« La règle combinée envoie un dossier en revue si la confiance maximale est inférieure à 0,70, ou si le modèle prédit la classe 0 tout en donnant au moins 0,20 de probabilité à la classe 2. Un seul de ces deux critères suffit. La confiance est le score le plus élevé du modèle, pas une certitude. La règle combinée est évaluée dans le notebook, mais l’API actuelle utilise encore le seuil simple de 0,55. »

### Slide 16 — Couverture et charge de revue

« Le seuil 0,70 a été choisi sur les prédictions OOF avec un budget d’escalade proche de 40 % et une cible de couverture d’au moins 70 % des erreurs critiques. En OOF, la règle escalade 40,2 % des dossiers et couvre 72,5 % des `2→0`. Sur le test, elle escalade 200 dossiers sur 500 et en signale huit sur dix ; deux ne le sont pas. Cela ne veut pas dire que le rappel général classe 2 vaut 80 %, ni que les huit signalements ont été corrigés par un conseiller. »

### Slide 17 — Courbes de seuil

« Ces courbes montrent le compromis entre le seuil, la part des dossiers envoyés en revue et la couverture des erreurs critiques sur OOF. Ici, “calibrer le seuil” veut dire choisir une règle de signalement ; ce n’est pas recalibrer les probabilités du modèle. Plus on demande de revues, plus on peut couvrir d’erreurs, mais cela augmente la charge des conseillers. »

### Slide 18 — Audit d’équité : âge et nationalité

« J’ai comparé le rappel de classe 2 par groupe sur le test. Il est de 11,8 % chez les moins de 30 ans, soit 2 sur 17, et de 73,7 % chez les 50 ans et plus, soit 42 sur 57. Il est de 45 % hors UE, 9 sur 20, contre 55,7 % pour les personnes UE, 39 sur 70. Les effectifs sont petits ; ces résultats sont des signaux d’alerte, pas une preuve causale ni un certificat d’équité. J’ai conservé l’âge parce qu’il peut aider à adapter l’accompagnement et qu’il s’agit d’une information directement observée. Ce choix ne le rend pas neutre : l’écart mesuré chez les jeunes justifie une analyse approfondie. Je n’ai pas encore entraîné de variante S2 avec et sans âge ; cette ablation reste à faire. »

### Slide 19 — Décision sur S2

« J’ai retenu S2 pour ne pas utiliser directement la nationalité dans la prédiction. Historiquement, j’ai d’abord choisi XGBoost parce qu’il avait le meilleur F1 macro parmi les modèles S2 de la comparaison initiale. Ensuite, j’ai réglé ses hyperparamètres en privilégiant le rappel parmi les configurations XGBoost. Cela n’a pas comparé ce XGBoost optimisé à des Random Forest et régressions logistiques optimisés selon le même objectif. Avec le recul, si le rappel classe 2 est prioritaire, j’aurais réévalué ces candidats avec le même protocole et une règle fixée à l’avance : rappel visé, plancher de F1 et capacité de revue. Je ne prétends pas avoir déjà établi lequel gagnerait cette nouvelle comparaison. »

**Si le jury demande le tuning, dire :**

« J’ai procédé en deux étapes. D’abord, j’ai retenu XGBoost comme candidat S2 parce qu’il avait le meilleur F1 macro de la comparaison initiale. Ensuite, j’ai testé huit configurations XGBoost sur les cinq folds du train, soit quarante évaluations. J’ai fait varier le nombre d’arbres entre 300 et 450, leur profondeur entre 5 et 7, et le taux d’apprentissage entre 0,03 et 0,05. Le sous-échantillonnage des lignes et des colonnes est resté fixé à 0,9 : il n’a pas été optimisé. Dans la grille XGBoost, j’ai classé les configurations d’abord par rappel classe 2, puis par F1 macro. La configuration retenue est 300 arbres, profondeur 5, taux d’apprentissage 0,03, avec les deux sous-échantillonnages à 0,9. Elle obtient 0,575 de rappel et 0,691 de F1 macro en CV. »

« Ce résultat est meilleur que la configuration XGBoost initiale en rappel, qui était à 0,558, mais le gain reste limité : 0,017. Et je n’ai pas appliqué le même tuning aux autres familles. Je ne peux donc pas dire que ce XGBoost réglé est meilleur qu’un Random Forest ou une régression logistique réglés selon le même critère. Avec le recul, c’est cette comparaison équitable que je referais avant de confirmer le modèle. »

**En une phrase :** « J’ai d’abord choisi XGBoost au F1 macro, puis optimisé ses réglages sur le rappel classe 2 en CV ; cela n’a pas suffi à prouver qu’il était le meilleur candidat pour l’objectif métier. »

### Slide 20 — Parcours d’un dossier dans le service

« Le parcours commence par la saisie du dossier, puis l’API appelle le modèle et renvoie une classe, un niveau de confiance, un statut, la version du modèle et un identifiant de requête. Le résultat peut être tracé et un feedback reçu ensuite. Les routes de santé, de métriques, de réentraînement et de rollback soutiennent ce parcours. La démonstration est locale : elle n’est pas connectée au système d’information d’une agence. »

### Slide 21 — Interface du conseiller

« Cette capture montre le parcours dans l’interface : saisir, lancer la prédiction, lire la classe et la confiance, voir le statut “à revoir”, puis retrouver la trace. Dans l’exemple, le modèle propose la classe 1 avec 47 % de confiance ; le seuil API de 0,55 déclenche la revue. C’est une capture de démonstration, pas la preuve d’un usage réel en agence. »

### Slide 22 — Feedback humain et label terrain

« Il faut distinguer deux informations. Le feedback humain est l’avis ou la correction du conseiller au moment de la revue ; il peut refléter son expertise, les règles locales et ses propres biais. Le label terrain est le délai de retour à l’emploi réellement observé, qui arrive six à douze mois plus tard et peut être incomplet ou censuré. Je ne dois pas traiter l’avis immédiat comme la vérité future. »

### Slide 23 — Biais de sélection des feedbacks

« Si je ne collecte que les dossiers envoyés en revue, mes retours porteront surtout sur les dossiers incertains ou complexes. Le modèle apprendrait alors sur un échantillon sélectionné par sa propre règle. Pour limiter ce biais, il faudrait aussi qualifier un échantillon de dossiers non signalés et établir un plan de collecte représentatif, avant d’utiliser ces labels pour réentraîner. »

### Slide 24 — Monitoring

« Le monitoring présenté suit l’activité, le comportement du modèle et la fiabilité du service : volume et classes prédites, confiances et abstentions, latence, erreurs HTTP et disponibilité. Il permet de repérer des changements ou des incidents. Sans labels terrain fiables, il ne mesure pas à lui seul le rappel réel, les erreurs `2→0` ou l’équité. Les indicateurs d’équité doivent être suivis par groupes avec des effectifs suffisants et un accès autorisé aux données d’audit. »

### Slide 25 — MLflow : run terminé ne veut pas dire promu

« Cette capture montre un candidat terminé mais rejeté. Son F1 est d’environ 0,695 contre 0,706 pour le modèle de production ; son rappel classe 2 est d’environ 0,489 contre 0,544. Le run a fini son exécution, mais le candidat n’a pas été promu. Les paramètres, les métriques, les artefacts et la décision permettent de reconstituer ce qui s’est passé. »

### Slide 26 — Cycle de réentraînement et SKIP

« Le cycle complet prévoit une prédiction, un feedback, un réentraînement, une comparaison, puis une décision de promotion ou de rejet. Mais la capture montre six feedbacks disponibles pour un minimum de 200 : le cycle s’arrête donc avec `SKIP`. Il n’y a eu ni nouvel entraînement ni promotion ; le modèle actif reste inchangé. »

### Slide 27 — Docker

« Cette preuve montre la construction locale des images de l’API, de MLflow et du réentraînement planifié, avec une orchestration reproductible. Elle prouve le build des images, pas un déploiement en agence ni un dimensionnement cible. Je garde ce point bref et reviens aux risques métier. »

### Slide 28 — CI/CD

« Le workflow automatise des contrôles, un entraînement de vérification, la construction et la publication de l’image. La réussite du workflow prouve que cette chaîne technique a passé ses étapes ; elle ne prouve ni la qualité métier du modèle ni un déploiement réel. Le job de déploiement dépend du webhook configuré. »

### Slide 29 — Garde-fous : slide présente dans le PPTX, absente du PDF actuel

« Plusieurs garde-fous sont visibles : S2 exclut la nationalité de la prédiction, l’identifiant technique est séparé, les inférences sont tracées et les cas incertains peuvent être orientés en revue. Mais la classe 2 reste minoritaire, le texte est peu diversifié, l’âge est conservé et des proxys restent possibles. L’exclusion d’une variable ne garantit ni l’équité ni la conformité. »

**Important :** cette slide figure dans le PPTX mais ne semble pas avoir été exportée dans le PDF actuel. Réexporter le PDF avant la présentation ou confirmer le support qui sera projeté.

### Slide 30 — Du prototype local à l’architecture cible

« Le prototype local réunit une interface, une API, de la traçabilité et du monitoring. L’intégration au référentiel usagers, la minimisation des flux, la sécurité, l’hébergement, la latence et les ressources CPU/RAM restent à construire ou à arbitrer. Je n’annonce pas un choix définitif entre hébergement local et cloud souverain sans validation des exigences et des capacités d’exploitation. »

### Slide 31 — Décision finale

« Ma décision de projet a été S2, sans nationalité en entrée, avec XGBoost et une règle de revue humaine étudiée. Je précise aujourd’hui la limite de cet arbitrage : XGBoost a été retenu initialement pour son F1 macro, alors que Random Forest et la régression logistique avaient un meilleur rappel classe 2 en validation croisée. Si je reprenais la sélection, je fixerais d’abord avec le métier le rappel visé, le plancher de F1 et la capacité de revue, puis je comparerais à nouveau ces candidats sur OOF. La revue ne doit être intégrée qu’avec un processus humain réel, une collecte de labels fiable, un audit d’équité et une validation de l’architecture. Le modèle signale ; le conseiller décide. »

## Chiffres à garder sous la main

| Sujet | Réponse |
|---|---|
| Jeu de données | 2 500 dossiers ; classes 0/1/2 : 37,44 % / 44,48 % / 18,08 %. |
| Split | 2 000 train, 500 test ; 90 vrais cas de classe 2 au test. |
| Manquants | Âge 122 ; diplôme 84 ; synthèse 81 ; allocataire 44. Le mode du diplôme est Bac. |
| S2, CV avant tuning | XGBoost F1 0,681 / rappel 0,558 ; Random Forest 0,645 / 0,694 ; régression logistique 0,660 / 0,674 ; LightGBM 0,664 / 0,591. |
| Tuning XGBoost en S2 | 8 configurations × 5 folds = 40 évaluations sur le train ; choix par rappel classe 2 puis F1. Paramètres retenus : 300 arbres, profondeur 5, taux 0,03, sous-échantillonnages lignes/colonnes 0,9. CV après tuning : rappel 0,575, F1 0,691. |
| XGBoost, test | Accuracy 0,730 ; F1 macro 0,704 ; rappel classe 2 0,533 ; ROC-AUC OVR macro 0,871. Test déjà consulté auparavant. |
| Matrice XGBoost test | Réel en lignes, prédit en colonnes : `[[148,36,3],[34,169,20],[10,32,48]]`. |
| Erreurs test | 10 `2→0` sur 90 ; 32 `2→1` ; 3 `0→2` sur 187 vrais classe 0. |
| Politique combinée OOF | Seuil 0,70 OU prédiction 0 et `P(classe 2) >= 0,20` ; escalade 40,2 %, couverture `2→0` 72,5 %. |
| Politique combinée, test | 200/500 signalés ; 8/10 `2→0` signalés ; 2 non signalés. Ce n’est pas 80 % de rappel classe 2. |
| API actuelle | Seuil simple 0,55 ; politique combinée non intégrée. |
| Audit âge | Rappel classe 2 : 2/17 (<30 ans), 3/11 (30–49 ans), 42/57 (50 ans et plus), 1/5 (âge manquant). Résultats descriptifs avec petits effectifs. |
| Audit nationalité | Rappel classe 2 : 9/20 hors UE (45,0 %) et 39/70 UE (55,7 %). Résultats descriptifs avec petits effectifs. |

## Questions probables du jury

**Pourquoi garder l’âge et retirer la nationalité ?**

« J’ai gardé l’âge parce que je pensais qu’il pouvait apporter une information directement utile pour adapter l’accompagnement. C’est une hypothèse métier, pas une causalité démontrée. J’ai retiré la nationalité des variables de prédiction parce que je ne voulais pas que cette caractéristique influe directement sur le classement, d’autant que l’EDA montrait un écart de classe 2 entre groupes. Je ne dis pas pour autant que l’âge est neutre : l’audit montre un écart marqué entre les moins de 30 ans et les 50 ans et plus. Il faut justifier cet usage, faire l’ablation avec et sans âge et examiner les résultats avant toute conclusion. »

**L’âge et la nationalité sont-ils des données sensibles ?**

« Je distingue une donnée personnelle, une catégorie particulière de données au sens de l’article 9 du RGPD et une caractéristique protégée contre la discrimination. L’âge et la nationalité sont des données personnelles et peuvent créer des risques de discrimination ; ils ne sont pas automatiquement des catégories particulières au sens de l’article 9. La nationalité peut néanmoins révéler l’origine ethnique selon le contexte. Je ne tranche pas la qualification juridique : elle doit être validée par le DPO ou le juriste. Dans mon modèle, l’âge reste une entrée ; la nationalité n’est pas envoyée pour prédire en S2 et son usage d’audit doit être séparé et autorisé. »

**Alors pourquoi ne pas retirer aussi l’âge ?**

« C’est une option que je dois évaluer, pas écarter par principe. Je l’ai conservé au départ comme information potentiellement utile à l’accompagnement. Mais mon audit montre un écart important de rappel selon l’âge. Je n’ai pas encore entraîné la variante sans âge ; je ne peux donc pas affirmer que le conserver améliore le service, ni que le retirer réduirait le biais. »

**Pourquoi XGBoost si son rappel classe 2 est le plus faible en S2 ?**

« Au départ, j’ai sélectionné XGBoost parce qu’il avait le meilleur F1 macro de la comparaison S2. Avec le recul, ce critère ne suffisait pas : son rappel classe 2 était de 0,558 avant tuning, contre 0,694 pour Random Forest et 0,674 pour la régression logistique. J’ai ensuite optimisé le rappel parmi les réglages de XGBoost, mais je n’ai pas comparé ce modèle optimisé à des Random Forest et régressions logistiques réglés de la même façon. Si le rappel classe 2 est prioritaire, je dois refaire cette comparaison sur OOF, avec un seuil de F1 macro et une capacité de revue définis à l’avance. Je présente donc XGBoost comme le choix historique du projet, pas comme un choix définitivement démontré. »

**Quelle erreur est acceptable ?**

« Je ne peux pas décider seul du niveau de risque acceptable. Le cadrage du notebook reprend une cible de rappel brut classe 2 entre 0,55 et 0,60, complétée par une revue humaine, et une cible révisée d’au plus 2 % d’erreurs critiques résiduelles après escalade. Le XGBoost testé a un rappel brut de 0,533, en dessous de cette fourchette. La règle combinée a laissé deux erreurs `2→0` non signalées sur 500 dossiers, soit 0,4 % de ce test, mais huit signalements sur dix ne prouvent pas que les conseillers les auraient corrigés. Le test est petit et a été consulté auparavant. Il faut faire valider ces seuils par le métier et les confirmer sur des données indépendantes avec le devenir réel des dossiers. »

**Pourquoi surveiller aussi l’erreur `0→2` ?**

« Elle est moins grave selon le brief, mais son coût n’est pas nul : elle peut provoquer une revue inutile, mobiliser du temps et retarder d’autres dossiers. Dans la matrice test de XGBoost, il y a 3 erreurs `0→2` sur 187 vrais cas de classe 0, soit 1,6 %. Je n’ai pas mesuré le coût opérationnel de ces erreurs ; je ne les présente donc ni comme gratuites ni comme équivalentes aux `2→0`. »

**La slide SHAP est-elle réellement une analyse SHAP ?**

« Dans la version actuelle, non : le graphique visible représente l’importance native des variables fournie par XGBoost. Il ne donne pas le sens de l’effet et ne doit pas être appelé SHAP. Je dois soit remplacer le visuel par une vraie analyse SHAP vérifiée, soit renommer la slide et expliquer cette importance native. Dans les deux cas, aucune importance ne prouve une causalité. »

**Le modèle est-il déployé et la règle combinée est-elle appliquée ?**

« La démonstration locale sert le modèle S2, mais elle n’est pas intégrée au système d’information réel. L’API applique encore le seuil simple de 0,55 ; la règle combinée à 0,70 est évaluée dans le notebook et n’est pas intégrée à l’API. Le workflow CI/CD et la construction Docker ne prouvent pas un déploiement en agence. »

**Que signifie le résultat de réentraînement `SKIP` ?**

« Il signifie que le cycle n’a pas démarré l’entraînement, car il n’y avait que six retours non consommés pour un minimum de 200. Ce n’est ni un candidat rejeté ni une promotion. Le modèle actif est resté inchangé. »

## Correspondance avec la grille CISIA

| Compétence | Preuves à mobiliser dans la présentation | Limite à annoncer |
|---|---|---|
| C1 — Données adaptées au besoin | Slides 2 à 8 : usage, cible, sources fournies, variables, répartition et valeurs manquantes. | La représentativité pour une agence réelle, les droits d’accès et la qualité à long terme ne sont pas démontrés par ce jeu d’examen. |
| C2 — Risques éthiques et sociétaux | Slides 2 à 5, 10, 18 et 29 : erreur critique, retrait de la nationalité, âge conservé, proxys, texte conseiller et écarts mesurés. | Pas de certification de conformité ni de validation DPO/juridique attestée ; ne pas conclure à l’absence de biais. |
| C3 — Préparer les données | Slides 6 et 7 : imputations, encodages, TF-IDF, extraction du département et prétraitement dans les folds. | Le sens des blancs du diplôme reste à vérifier ; l’imputation par le mode peut masquer leur cause. |
| C4 — Choisir un modèle adapté | Slides 8 à 19 : familles, CV, F1, rappel, ROC-AUC, matrices, coûts d’erreurs et décision. | Le critère de sélection initial (F1) est en tension avec la priorité de rappel ; les concurrents n’ont pas tous été tunés selon le même objectif. L’ablation d’âge et le recalcul comparable des scénarios restent à faire. |
| C5 — Entraîner et optimiser | Slides 7, 8, 13 et 19 : apprentissage supervisé, validation croisée, hyperparamètres XGBoost et sélection historique. | Ne pas prétendre que les hyperparamètres des autres modèles ont été optimisés à armes égales ; pas de transfert de connaissances effectué. |
| C6 — Intégrer les briques techniques | Slides 20 à 28 : API, interface, version, logs, MLflow, retrain, Docker et CI/CD. | La règle combinée n’est pas dans l’API ; le déploiement et l’intégration réels ne sont pas démontrés. |
| C7 — Architecture cible | Slide 30 : flux local démontré versus intégration, sécurité, hébergement, latence et dimensionnement à arbitrer. | Pas de décision d’hébergement final ni de preuve de consultation formelle des acteurs métier/techniques. |
| C8 — Mesurer performance et impacts | Slides 13, 16 à 18 et 24 : erreurs, OOF, test, sous-groupes, métriques de service et seuils. | La performance réelle à long terme exige des labels terrain ; l’audit porte sur de petits effectifs et le test n’est pas historiquement vierge. |
| C9 — Amélioration continue | Slides 22 à 28 : feedback, biais de sélection, monitoring, run rejeté, `SKIP`, versioning et CI/CD. | Le feedback humain n’est pas le résultat réel différé ; prévoir une collecte représentative, un contrôle des dossiers non signalés et une évaluation périodique. |

**Conclusion sur la grille :** la présentation apporte des éléments pour les neuf compétences, mais certaines preuves restent des propositions ou des limites déclarées plutôt que des réalisations. Les nommer ainsi est plus solide que les présenter comme déjà validées.

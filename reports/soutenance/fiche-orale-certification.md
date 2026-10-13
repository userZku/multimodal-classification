# Fiche orale de certification CISIA

Support de préparation correspondant aux **24 slides du PPTX v2**. Les numéros ci-dessous suivent directement la présentation.

## Mon fil rouge

**Comment aider un conseiller à repérer les situations de chômage de longue durée, sans utiliser directement la nationalité et sans laisser le modèle décider seul ?**

Mon histoire suit quatre questions :

1. Quelles erreurs faut-il éviter et que permettent les données ?
2. Quel modèle choisir, avec quel compromis éthique ?
3. Quand faut-il demander une revue humaine ?
4. Comment rendre cette solution utilisable, observable et réversible ?

À chaque étape : **je pose une question, je montre une preuve, j'explique les options, je prends une décision, j'annonce sa limite**. Je ne lis pas les listes de composants : j'explique pourquoi ils sont nécessaires.

## Repères à garder pendant la soutenance

- **Couverture :** elle porte la date 14/10/2026 ; les pieds de page des slides intérieures portent 12/10/2026. Vérifier si cet écart est intentionnel.
- **Slide 5 :** les proportions affichées sont 37,44 % / 44,48 % / 18,08 %.
- **Slide 6 :** le test a été consulté dans une version antérieure. Le seuil actuel est choisi sur OOF, mais le test n'est pas historiquement vierge.
- **Slides 7 à 10 :** les résultats des scénarios sont répartis sur quatre slides. F1 et rappel viennent de la validation croisée ; les erreurs `2 -> 0` sont comptées sur le test.
- **Slide 8 :** S2 exclut `nationalite_hors_ue` ; cela n'élimine pas les proxys possibles.
- **Slides 11 et 12 :** la règle combinée à 0,70 est évaluée dans le notebook ; l'API applique encore le seuil simple de 0,55.
- **Slide 12 :** 8/10 signifie huit erreurs critiques signalées sur dix pour S2. Ce n'est ni le rappel général de classe 2, ni la preuve que les conseillers les ont corrigées.
- **Slide 13 :** S2 est retenu malgré son score inférieur à S1 ; S4 compte 8 erreurs critiques au test mais conserve actuellement la nationalité.
- **Slide 18 :** `Finished` signifie que le run est terminé, pas que le candidat est accepté.
- **Slide 19 :** la capture montre un cycle `SKIP` faute de feedbacks suffisants, pas un entraînement ni une promotion.
- **Slide 21 :** le job de déploiement est conditionnel ; le workflow peut être vert alors que le déploiement est ignoré si le webhook n'est pas configuré.
- **Slides 22 et 23 :** l'intégration au référentiel, l'hébergement, la sécurité, la latence et le dimensionnement sont à valider, pas des réalisations démontrées.

## Repères pour 30 minutes

| Partie | Slides | Temps cible |
|---|---|---:|
| Sujet, données et protocole | 1 à 6 | 7 min |
| Comparaison des scénarios et recommandation | 7 à 13 | 10 min |
| API, interface, traçabilité et suivi | 14 à 19 | 7 min |
| Livraison, limites et cible SI | 20 à 24 | 6 min |

Les textes suivants sont une base orale, pas un script à réciter mot pour mot. Pendant les 30 minutes, privilégier le message, la décision et sa preuve ; garder les concepts détaillés et les réponses difficiles pour les questions du jury.

### La formule pour raconter une décision

Pour chaque choix, suivre quatre temps : **besoin → options → critère d'arbitrage → limite**. Par exemple : « Je voulais réduire les erreurs critiques. J'ai comparé plusieurs scénarios et plusieurs règles. J'ai retenu S2 avec une politique de revue évaluée sur OOF, car je ne voulais pas utiliser directement la nationalité. Ce choix a un coût mesuré et impose de vérifier que les équipes peuvent traiter le volume de revues. »

Ne pas confondre trois niveaux de preuve : **mesuré dans le notebook**, **implémenté dans la démonstration locale**, **à valider avant intégration réelle**. C'est le repère le plus utile si une question dépasse les résultats disponibles.

---

## Slide 1 - Titre

**Message à retenir :** annoncer le sujet et le fil conducteur, sans entrer trop tôt dans les détails.

**Ce que je peux dire :**

« Je vais vous présenter un prototype qui estime le délai de retour à l'emploi à partir des informations du dossier et de la synthèse d'entretien. Je vais surtout expliquer comment j'ai comparé les scénarios, traité une erreur métier importante et posé des limites à l'usage du modèle. »

**Transition :** « Je commence par le besoin concret auquel ce système essaie de répondre. »

## Slide 2 - Classification multimodale

**Message à retenir :** je construis une aide qui signale un risque, pas un outil qui décide du parcours d'une personne.

**Ce que je peux dire :**

« Le sujet me demande d'estimer si le retour à l'emploi sera rapide, intermédiaire ou risque de dépasser douze mois. Pour cela, j'ai combiné des informations du dossier et le texte de la synthèse d'entretien. Mais mon objectif n'est pas de décider à la place du conseiller : je cherche à mieux repérer les dossiers qui méritent son attention. Je vais expliquer comment j'ai comparé les solutions et pourquoi j'en ai retenu une, avec ses limites. »

**Transition :** « Pour comprendre mes choix, il faut d'abord comprendre quelle erreur aurait la conséquence métier la plus grave. »

**Définition :** multimodal signifie ici combiner des données structurées en colonnes et du texte libre. Cela ne signifie pas que le projet traite aussi des images ou de l'audio.

## Slide 3 - Toutes les erreurs ne se valent pas

**Message à retenir :** je donne la priorité à une erreur métier précise, plutôt qu'à une moyenne flatteuse.

**Ce que je peux dire :**

« J'ai commencé par traduire le sujet en trois classes : moins de six mois, six à douze mois, et plus de douze mois. Puis j'ai défini avec le brief l'erreur à surveiller en priorité : une personne réellement en classe 2 que le modèle annonce en classe 0. Cette erreur pourrait faire passer un besoin d'accompagnement renforcé sous le radar. Je l'appelle “critique” à cause de cette conséquence potentielle ; je n'affirme pas avoir mesuré un impact réel sur des usagers. »

**Transition :** « Cette priorité métier posée, voyons les informations dont je disposais pour construire une prédiction. »

**Définitions :** classification = attribution à une catégorie ; apprentissage supervisé = apprentissage sur des exemples dont la catégorie est connue ; erreur `2 -> 0` = classe réelle 2, classe prédite 0.

## Slide 4 - Les données disponibles

**Message à retenir :** j'ai séparé les types de données et repéré dès le départ la variable sensible.

**Ce que je peux dire :**

« J'ai commencé par inventorier les 2 500 dossiers et leurs dix colonnes. J'ai regroupé les champs en trois familles : les informations numériques et catégorielles, le texte libre de l'entretien, et la cible à prédire. J'ai aussi identifié la nationalité hors UE comme variable sensible. Elle reste dans la comparaison S1 pour mesurer son effet, mais je l'exclus du scénario S2 retenu et de ses entrées de prédiction. »

**Transition :** « Avant d'entraîner un modèle, j'ai vérifié la qualité des champs et la répartition des résultats connus. »

**Définitions :** cible = réponse à apprendre, ici `classe_retour_emploi` ; feature = variable utilisée pour prédire ; variable catégorielle = valeur parmi des modalités ; variable sensible = dans ce projet, donnée présentant un risque de discrimination. Cette dernière expression ne remplace pas une qualification juridique précise au sens du RGPD.

## Slide 5 - Ce que l'analyse des données révèle

**Message à retenir :** l'exploration m'a servi à comprendre les données avant de choisir comment les préparer et les évaluer.

**Ce que je peux dire, après correction du graphique :**

« Concrètement, j'ai inspecté la répartition des classes, les valeurs manquantes et les différences entre groupes. La classe 2 représente 18,08 % des dossiers ; elle est moins fréquente que les classes 0 et 1. J'ai aussi repéré des écarts associés à la nationalité et des formulations textuelles répétitives. Ces constats m'ont conduit à prévoir des traitements adaptés et à garder les proxys en tête. Un écart observé dans les données ne prouve pas à lui seul que le modèle discrimine ou qu'une variable cause le résultat. »

**Transition :** « Cette exploration m'indique quoi surveiller ; il me faut maintenant une méthode d'évaluation qui évite de faire apprendre au modèle les réponses. »

**Définitions :** EDA = analyse exploratoire des données ; proxy = variable pouvant refléter indirectement une caractéristique exclue ; surapprentissage = apprendre des particularités du jeu plutôt qu'une règle qui généralise à de nouveaux dossiers.

## Slide 6 - Séparer apprentissage et évaluation

**Message à retenir :** apprendre et se tester doivent être deux opérations distinctes.

**Ce que je peux dire :**

« J'ai séparé les données en 2 000 dossiers d'apprentissage et 500 de test. J'ai utilisé un split stratifié : il garde à peu près la même proportion de chaque classe dans les deux groupes, dont 90 dossiers de classe 2 dans le test. Ensuite, j'ai regroupé la préparation et le modèle dans un pipeline. Ainsi, les imputations, encodages et transformations du texte sont appris sur le train, puis appliqués au test sans être réajustés dessus. »

« Pour choisir la règle de revue, j'ai ensuite produit des prédictions OOF dans le train : chaque dossier est prédit par un modèle qui n'a pas appris sur lui. Le test sert ensuite à lire le résultat final. Il y a une réserve importante : le test a été consulté dans une version antérieure du projet. Le protocole actuel sépare le choix du seuil de cette lecture, mais je ne prétends pas que le test soit historiquement resté vierge. »

**Transition :** « Avec ce protocole commun, je peux comparer l'apport des données complètes, du texte seul et des variables tabulaires. »

**Concepts simples :**

- **Imputation :** remplacer une valeur manquante par une valeur calculée à partir du train.
- **Encodage ordinal :** représenter le diplôme avec un ordre défini, du niveau le plus faible au plus élevé.
- **One-hot :** transformer une catégorie, comme un métier, en indicateurs numériques séparés.
- **TF-IDF :** transformer le texte en nombres qui donnent plus de poids aux mots informatifs qu'aux mots très courants.
- **Fuite de données :** laisser entrer dans l'apprentissage une information qui devrait rester inconnue au moment où l'on prédit.

## Slide 7 - S1 : la référence avec toutes les variables

**Message à retenir :** S1 montre le meilleur F1, mais utilise aussi la variable sensible directe.

**Ce que je peux dire :**

« J'ai d'abord gardé toutes les variables, y compris la nationalité hors UE, pour obtenir un point de comparaison. C'est S1. Son F1 macro moyen en validation croisée est de 0,708 et son rappel de classe 2 de 0,572. Sur le test, il fait neuf erreurs critiques `2 -> 0`. Cette expérience répond à la question : quel score obtient-on avec toutes les informations disponibles ? Je ne retiens pas S1 comme choix final, parce qu'il utilise directement la variable sensible. »

**Transition :** « Je regarde maintenant ce que coûte le retrait de cette variable. »

**Concepts simples :** le **F1 macro** fait la moyenne des scores F1 des trois classes, en leur donnant le même poids. Le **rappel de classe 2** indique quelle part des vrais dossiers de classe 2 est retrouvée. Ces deux scores viennent de la validation croisée ; les neuf erreurs critiques sont comptées sur le test.

## Slide 8 - S2 : le compromis sans variable sensible directe

**Message à retenir :** S2 garde les colonnes et le texte, mais retire `nationalite_hors_ue`.

**Ce que je peux dire :**

« Dans S2, j'ai retiré directement la nationalité, tout en gardant les autres colonnes et le texte de l'entretien. Le F1 macro passe de 0,708 à 0,681, et le rappel de classe 2 de 0,572 à 0,558. Sur le test, S2 compte dix erreurs critiques, contre neuf pour S1. J'accepte cette baisse mesurée pour ne pas donner directement cette information au modèle. Cela ne prouve pas l'absence de biais : d'autres informations peuvent encore jouer le rôle de proxys. »

**Transition :** « Pour comprendre la contribution de l'entretien, j'ai aussi évalué le texte tout seul. »

**Concepts simples :** un **proxy** est une autre information qui peut refléter indirectement une caractéristique sensible. Retirer une colonne ne retire donc pas nécessairement tous les signaux qui lui sont associés.

## Slide 9 - S3 : le texte seul

**Message à retenir :** le texte aide à retrouver la classe 2, mais ne suffit pas à faire le choix final.

**Ce que je peux dire :**

« Pour S3, j'ai retiré toutes les colonnes et gardé seulement la synthèse d'entretien. En validation croisée, c'est le scénario qui retrouve le mieux la classe 2 : son rappel est de 0,661. Son F1 macro est de 0,635. Mais sur le test, il compte douze erreurs critiques `2 -> 0`, et les textes sont assez répétitifs. Je vois donc un apport du texte, mais aussi un risque de mal généraliser ; je ne le retiens pas seul. »

**Transition :** « Enfin, je vérifie ce que les colonnes peuvent apporter sans le texte. »

**Concept simple :** le **rappel** répond à la question « parmi les personnes réellement en classe 2, combien le modèle a-t-il repérées ? ». Un meilleur rappel ne signifie pas qu'il fait moins toutes les autres erreurs.

## Slide 10 - S4 : les données tabulaires sans le texte

**Message à retenir :** S4 est intéressant sur ce test, mais il ne respecte pas la même contrainte que S2.

**Ce que je peux dire :**

« Dans S4, j'ai gardé les colonnes du dossier et retiré le texte. Le F1 macro est de 0,672 et le rappel de classe 2 de 0,589 en validation croisée. Sur le test, S4 compte huit erreurs critiques, contre dix pour S2. Mais le scénario S4 actuel conserve la nationalité ; il ne constitue donc pas une comparaison équivalente au choix éthique de S2. Et deux dossiers d'écart sur cet échantillon ne suffisent pas à prouver qu'il serait meilleur. »

**Transition :** « Après avoir comparé les données et leurs résultats, je montre comment je signale les prédictions qui méritent une revue humaine. »

**À retenir :** les scores de F1 et de rappel sont des moyennes de validation croisée ; les nombres d'erreurs `2 -> 0` sont mesurés sur le test. Le test a été consulté dans une version antérieure du projet : ce n'est pas un holdout historiquement vierge.

## Slide 11 - Ajouter un mécanisme de revue humaine

**Message à retenir :** le classifieur et la politique de décision sont deux éléments distincts.

**Ce que je peux dire :**

« J'ai séparé la prédiction de la décision de revue. Le modèle donne une classe et trois scores ; une règle regarde ensuite s'il faut demander une vérification. Dans le notebook, il y a deux portes d'entrée vers la revue : une confiance maximale sous 0,70, OU une prédiction 0 avec `P(classe 2) >= 0,20`. Si l'une des deux conditions est vraie, le dossier est signalé. Cela attire l'attention sur un risque ; cela ne corrige pas automatiquement la prédiction. »

« Cette règle combinée est évaluée dans le notebook, mais pas intégrée au service actuel. L'API utilise encore la règle simple de confiance sous 0,55. Il faut donc distinguer le seuil 0,70 étudié ici du seuil 0,55 effectivement utilisé par l'API. »

**Transition :** « Le choix du seuil doit lui aussi reposer sur une méthode d'évaluation séparée du test. »

**Concepts simples et exemple :**

- La **confiance** est le plus grand des trois scores de probabilité du modèle. Ce n'est pas une certitude.
- Le seuil **0,70** est celui de la règle combinée étudiée dans le notebook ; le seuil **0,55** est celui que l'API utilise actuellement.
- Exemple : le modèle donne classe 0 avec une confiance de 0,74 et `P(classe 2) = 0,23`. Le premier critère est faux, car 0,74 dépasse 0,70. Le second est vrai : le dossier va quand même en revue.
- Autre exemple : si la confiance maximale est 0,62, le premier critère suffit pour demander la revue, quelle que soit la classe prédite.
- **Revue humaine / abstention :** le système signale qu'une personne doit vérifier la proposition ; ce n'est pas une quatrième classe.

## Slide 12 - Choisir le seuil avec des prédictions OOF

**Message à retenir :** je règle la politique sur le train, puis j'en examine le résultat sur le test.

**Ce que je peux dire :**

« Pour choisir le seuil sans le régler directement sur le test, j'ai découpé les données d'entraînement en cinq groupes. Chaque dossier reçoit ensuite une prédiction faite par un modèle qui ne l'a pas vu pendant son apprentissage : c'est une prédiction OOF. Sur ces prédictions, j'ai testé plusieurs seuils pour la règle de revue. J'ai retenu 0,70 : ce seuil respecte deux contraintes fixées à l'avance, un taux d'escalade sous environ 41 % et une couverture d'au moins 70 % des erreurs critiques. »

« Le résultat OOF est proche des contraintes : 40,2 % des dossiers seraient revus et 72,5 % des erreurs critiques seraient signalées. J'ai ensuite regardé la règle sur le test : 200 dossiers sur 500 sont signalés. Parmi les dix erreurs `2 -> 0` de S2, huit sont repérées et deux passent à travers. Cela ne veut pas dire que le rappel général de la classe 2 est de 80 %, ni que les conseillers ont réellement corrigé les huit dossiers : je n'ai pas mesuré ce dernier point. »

« Je garde deux réserves. D'abord, le test avait déjà été consulté dans une version antérieure du projet : je ne le présente donc pas comme un test resté secret depuis le début. Ensuite, les prédictions OOF ne sont pas indépendantes du choix des hyperparamètres, car je n'ai pas fait de validation imbriquée. Il faudrait une évaluation externe pour confirmer ces chiffres dans de meilleures conditions. »

**Transition :** « Cette règle donne une recommandation concrète, mais aussi une charge humaine à assumer. »

**Concepts simples :** OOF signifie que le dossier est prédit sans avoir servi à entraîner le modèle qui le prédit. La **couverture critique** est la part des erreurs `2 -> 0` signalées. Le **taux d'escalade** est la part de tous les dossiers envoyés en revue. Ici, choisir un seuil consiste à choisir la règle de signalement ; ce n'est pas la même chose que vérifier si les probabilités du modèle sont bien calibrées.

**Si le jury approfondit :** les hyperparamètres ont été choisis avec la CV du train ; l'OOF obtenu n'est pas une validation imbriquée indépendante de ce choix. De plus, le test avait déjà été exploré dans une version antérieure. La procédure actuelle ne choisit plus le seuil sur le test, mais je ne présente pas ce test historique comme un holdout jamais consulté. Une confirmation externe serait nécessaire pour une évaluation complètement indépendante.

## Slide 13 - Formuler la recommandation

**Message à retenir :** le choix porte sur un modèle, des données et des conditions d'usage.

**Ce que je peux dire :**

« Ma recommandation est S2 avec XGBoost : il utilise à la fois les colonnes du dossier et le texte, sans utiliser directement la nationalité. Je ne le choisis pas parce qu'il gagne tous les scores, mais parce que j'accepte son compromis pour respecter cette contrainte. S1 sert de référence, S3 montre ce que le texte peut apporter, et S4 compare les colonnes sans le texte, mais conserve la nationalité. La règle de revue serait aussi à prévoir, à condition de pouvoir traiter environ 40 % des dossiers. Aujourd'hui, le modèle est accessible dans l'API de démonstration, mais cette règle combinée n'y est pas encore intégrée. Dans tous les cas, le résultat reste une aide au conseiller, pas une décision automatique. »

**Transition :** « Pour rendre cette recommandation utilisable, j'ai ensuite construit une API de démonstration. »

**Si le jury demande pourquoi ne pas choisir S4 :** « S4 compte deux erreurs critiques de moins sur ce test, mais ce résultat porte sur dix cas et peut varier. Surtout, le S4 actuel conserve la nationalité ; il ne répond donc pas à la même contrainte que S2. Je le garde comme diagnostic tabulaire, pas comme alternative éthique prête à déployer. »

**Définitions :** hyperparamètre = réglage choisi avant l'apprentissage ; tuning = recherche de ces réglages ; production = ici service de démonstration local, pas déploiement attesté dans le SI d'une agence.

## Slide 14 - Le parcours d'un dossier dans l'API

**Message à retenir :** l'API accompagne un dossier de la saisie jusqu'à la trace et au feedback.

**Ce que je peux dire :**

« Je présente le fonctionnement comme un parcours. L'application envoie les informations du dossier à l'API ; l'API vérifie les champs et appelle le modèle chargé. Elle renvoie une classe, une confiance et un statut, par exemple “à revoir”, avec la version du modèle et un identifiant de requête. Le résultat peut ensuite être retrouvé dans l'historique et associé à un retour terrain. Les routes de santé, de métriques ou de réentraînement soutiennent ce parcours, mais ne sont pas le parcours lui-même. »

**Transition :** « Je montre maintenant ce parcours du point de vue du conseiller. »

**Concepts simples :** API = interface qui permet à deux logiciels d'échanger ; requête = informations envoyées au service ; réponse = résultat renvoyé ; endpoint = adresse d'une fonction de l'API ; `request_id` = identifiant technique d'un appel, pas identifiant personnel de l'usager.

## Slide 15 - Montrer une prédiction et son incertitude

**Message à retenir :** l'interface montre aussi les raisons de ne pas laisser passer la proposition sans revue.

**Ce que je peux dire :**

« Dans cette capture, le dossier retourne une classe 1 avec 47 % de confiance. Ce score est inférieur au seuil de l'API, 0,55 ; l'interface affiche donc une revue humaine recommandée. On voit également la version et le request_id, utiles pour relire l'appel. Le formulaire et l'historique démontrent le parcours d'inférence. Les boutons de réentraînement et rollback sont des fonctions d'administration de la démonstration, pas des droits que je donnerais nécessairement à tous les conseillers. »

**Transition :** « Cet écran s'appuie sur plusieurs composants ; je vais montrer comment ils échangent. »

**Définitions :** UI / IHM = interface utilisateur ; front-end = partie visible ; back-end = service qui traite l'appel ; historique d'inférences = traces des prédictions passées.

## Slide 16 - Tracer une prédiction et son modèle

**Message à retenir :** relier une prédiction à sa requête, à la version du modèle et à la décision prise.

**Ce que je peux dire :**

« Pour expliquer la traçabilité, je suis un dossier. L'entrée produit une prédiction avec une classe et une confiance ; l'appel reçoit un `request_id` et la version du modèle. Si un retour terrain arrive, il peut être rattaché à cette prédiction. Les expériences d'entraînement gardent aussi leurs paramètres et leurs métriques ; enfin, la décision de promotion ou de rejet est conservée et un rollback est disponible. L'objectif est de pouvoir comprendre quelle version a répondu et ce qui a été décidé ensuite. »

**Transition :** « Cette trace répond à la question “quelle version a répondu ?” ; le monitoring répond à “comment le service se comporte-t-il ?”. »

**Concepts simples :** `request_id` = identifiant technique d'une requête ; version du modèle = version qui a produit la réponse ; feedback = retour terrain rattaché à une prédiction ; rollback = retour à une version précédente. Un identifiant technique ne prouve pas à lui seul qu'une identité personnelle est nécessaire ou doit être conservée.

## Slide 17 - Observer sans confondre activité et qualité

**Message à retenir :** le monitoring rend le service visible, mais ne remplace pas les vraies étiquettes terrain.

**Ce que je peux dire :**

« Dans cette capture, le service est UP, les requêtes n'affichent pas d'erreur et la latence p95 affichée est d'environ 29 ms. Le dashboard montre également les classes prédites, la confiance et le taux d'abstention. Ce sont des observations sur la fenêtre de trafic simulé de la capture, pas une garantie pour toutes les charges. Le F1 affiché, 0,713, est une métrique enregistrée du modèle actif : ce n'est pas un F1 recalculé en direct à partir des requêtes. »

« Pour mesurer une baisse de qualité réelle, il faut joindre les prédictions aux labels terrain. Une variation de confiance ou des classes prédites est un signal à examiner, pas une preuve automatique de dérive de performance. »

**Transition :** « À cette observation du service, j'ajoute une trace des expériences qui ont produit les modèles. »

**Définitions :** Prometheus = collecte de métriques ; Grafana = visualisation de ces métriques ; compteur = total d'événements ; histogramme = répartition de mesures ; drift = changement des données ou de leur relation avec la cible ; latence = durée d'une réponse.

## Slide 18 - Un réentraînement peut réussir tout en étant rejeté

**Message à retenir :** MLflow permet d'expliquer une décision, même quand le nouveau modèle n'est pas promu.

**Ce que je peux dire :**

« Cette capture est un exemple concret de candidat rejeté. Son F1 est d'environ 0,695 contre 0,706 pour le modèle actif ; son rappel de classe 2 est de 0,489 contre 0,544, soit environ 5,6 points de moins. Le run est marqué `Finished` parce que l'exécution s'est terminée ; la décision métier est `rejected`. Les sept feedbacks joints et les 2 007 lignes d'entraînement sont également tracés. »

« Cela ne signifie pas que MLflow a automatiquement recalibré le modèle, ni que tous les artefacts sont dans un registre de modèles : je montre le tracking réellement utilisé. »

**Transition :** « Ce rejet illustre la règle de contrôle que je vais détailler. »

**Définitions :** run = une exécution suivie ; tracking = enregistrement de paramètres, métriques et fichiers ; tag = étiquette de contexte ; candidat = modèle entraîné mais pas encore actif ; Finished = exécution achevée, pas validation de la qualité.

## Slide 19 - Cycle de réentraînement : un SKIP normal

**Message à retenir :** le cycle automatique peut s'arrêter normalement avant l'entraînement si les retours sont trop peu nombreux.

**Ce que je peux dire :**

« Le schéma montre le cycle prévu : prédiction, retour terrain, réentraînement, comparaison, puis décision de promouvoir ou de rejeter le candidat. Mais la capture présentée s'arrête avant ces étapes. Elle indique six feedbacks disponibles alors que le seuil du cycle est de 200 ; le résultat est donc `SKIP`. C'est un arrêt normal : aucun entraînement, aucune comparaison et aucune promotion n'ont eu lieu. Le modèle actif reste inchangé. »

« Il faut distinguer trois résultats possibles : `SKIP` si le volume de retours est insuffisant, candidat rejeté après comparaison, ou candidat promu s'il satisfait les garde-fous. La capture de cette slide montre le premier cas. La capture MLflow précédente montre le deuxième. »

**Transition :** « Pour exécuter les services de façon reproductible, je les ai aussi empaquetés avec Docker. »

**Définitions :** feedback = classe réelle ou annotation validée après prédiction ; reference_set = jeu figé pour comparer les versions, ici 500 dossiers dont 90 de classe 2 ; promotion = activation du candidat ; rollback = restauration d'une version précédente ; cron = planification périodique ; SKIP = cycle ignoré normalement, sans apprentissage.

**Si le jury demande les règles :** tolérance de baisse du rappel = 0,005, soit 0,5 point ; tolérance de F1 = 0,01, soit 1 point, avec exception si le gain de rappel dépasse 0,01. Le garde-fou exige 20 feedbacks joints pour une promotion hors bootstrap ; c'est distinct des 200 retours déclenchant le cron. Ces règles sont des heuristiques, pas un test de significativité statistique. Réutiliser souvent le `reference_set` expose aussi à un surajustement progressif à ce jeu.

## Slide 20 - Docker : construire un environnement transportable

**Message à retenir :** je peux reconstruire les services à partir de leur définition.

**Ce que je peux dire :**

« Docker Compose décrit les services et leurs connexions : API, MLflow, Prometheus, Grafana et réentraînement planifié. La sortie affichée montre la construction réussie des trois images locales API, MLflow et retrain-cron. Prometheus et Grafana utilisent des images existantes. Cette sortie prouve le build ; les captures du service apportent une preuve d'exécution à une autre étape. Le build seul ne prouve pas que tout fonctionne. »

**Transition :** « J'ai également automatisé les contrôles déclenchés par les évolutions du code. »

**Définitions :** image Docker = paquet servant à lancer un service ; conteneur = instance en exécution d'une image ; Dockerfile = recette de construction ; Compose = définition de plusieurs services ; volume = stockage conservé indépendamment du conteneur.

## Slide 21 - GitHub Actions : vérifier et publier

**Message à retenir :** chaque modification peut être soumise à une chaîne de vérifications automatisées.

**Ce que je peux dire :**

« La capture montre un workflow réussi pour le commit 9d3d644 sur main, en 7 minutes 56 secondes. Il exécute les tests, un entraînement de vérification, le build et la publication de l'image. Le lint est présent mais non bloquant dans le workflow actuel. Le déploiement est conditionnel : un job vert peut correspondre à une étape ignorée si le webhook n'est pas configuré. Je ne présente donc pas ce vert comme la preuve d'un déploiement réel chez l'agence. »

**Transition :** « Docker prépare l'environnement ; la CI vérifie et prépare sa livraison. »

**Définitions :** CI = intégration continue, vérifications automatiques du code ; CD = livraison ou déploiement continus selon la configuration ; workflow = processus automatisé ; job = groupe d'étapes ; smoke test = vérification minimale qu'une fonction essentielle s'exécute ; lint = analyse de qualité du code ; GHCR = registre d'images de GitHub ; commit = version enregistrée du code.

## Slide 22 - Les garde-fous réduisent le risque, sans supprimer les limites

**Message à retenir :** j'explicite les conditions d'un usage responsable, sans annoncer une conformité totale.

**Ce que je peux dire :**

« J'ai mis en place des garde-fous : la nationalité est exclue de S2, les identifiants ne servent pas à prédire, les appels sont tracés et les cas incertains peuvent être revus. Mais ces mesures ne garantissent pas l'absence de biais : des proxys peuvent subsister. Il reste à valider la capacité de revue, à sécuriser l'API et à définir les durées d'accès et de conservation des traces. Le retrait d'une colonne ne certifie pas à lui seul la conformité juridique du système. »

**Transition :** « Ces limites montrent ce qu'il faudrait arbitrer avant de relier la démonstration au système d'information réel. »

**Définitions :** RGPD = cadre européen de protection des données personnelles ; minimisation = ne traiter que les données nécessaires ; pseudonymisation = remplacer un identifiant sans rendre toute réidentification impossible ; authentification = vérifier qui appelle ; autorisation = vérifier ses droits ; TLS = chiffrement du transport.

## Slide 23 - Du prototype local à la cible SI

**Message à retenir :** la démonstration existe ; l'intégration au système d'information reste une cible à concevoir et valider.

**Ce que je peux dire :**

« Jusqu'ici, j'ai montré une chaîne locale : une interface appelle une API, le service renvoie une classe et un niveau de confiance, puis des traces alimentent le suivi. Pour une intégration réelle, l'application conseiller devrait échanger avec le référentiel usagers et transmettre à l'API uniquement les informations nécessaires. Cette connexion n'est pas réalisée dans le projet : la slide distingue le démontré de la cible à valider. »

« Le choix entre un hébergement sur site et un cloud souverain dépendrait des exigences de sécurité, de localisation des données, d'exploitation, de coût et de disponibilité. Je n'annonce pas un choix final. De même, le dimensionnement CPU/RAM et la latence en situation de charge sont à mesurer ; le temps de prédiction local ne suffit pas à les déterminer. »

**Transition :** « Cette séparation entre ce qui est démontré et ce qui reste à valider résume aussi ma recommandation finale. »

**Concepts à expliquer simplement :**

- **Architecture cible :** le plan de circulation des données et des responsabilités dans le système futur ; ce n'est pas la preuve que les connexions sont déjà construites.
- **Minimisation :** ne transmettre que les champs nécessaires à la prédiction, et ne pas envoyer l'identité si elle n'est pas utile au modèle.
- **On-premise / cloud souverain :** héberger dans l'infrastructure de l'organisation ou chez un fournisseur répondant à des exigences de souveraineté ; le choix implique sécurité, compétences d'exploitation, coût et disponibilité.
- **Dimensionnement :** estimer CPU, mémoire, stockage et capacité sous charge ; il faut tester avec un trafic représentatif, pas extrapoler d'un benchmark local seul.

## Slide 24 - S2 + escalade humaine : le choix responsable à confirmer en conditions réelles

**Message à retenir :** mon résultat est un compromis mesuré, accompagné de moyens de contrôle.

**Ce que je peux dire :**

« Je suis parti d'une erreur métier à éviter : sous-estimer une situation de longue durée. J'ai comparé plusieurs options et retenu S2, qui exclut la variable sensible directe au prix d'une baisse de performance mesurée. J'ai aussi évalué une règle qui signale huit des dix erreurs critiques du test, mais oriente environ 40 % des dossiers vers une revue. La démonstration est traçable et observable ; l'intégration SI et la capacité réelle de revue restent à valider. Ma recommandation est donc S2 avec une politique de revue humaine, sous ces conditions. »

« Je ne présente pas une IA qui décide seule. Je présente une aide à la décision dont les compromis, les limites et les prochaines validations sont visibles. »

**Concept à expliquer simplement :** une recommandation responsable ne consiste pas seulement à choisir un modèle ; elle précise aussi les conditions d'usage, les contrôles humains et les preuves encore nécessaires.

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

**Pourquoi S4 a-t-il moins d'erreurs critiques que S2 ?**

« Dans cette partition de test, S4 en compte huit et S2 dix. C'est un signal à discuter, pas une preuve de supériorité : il n'y a que dix erreurs critiques, et le S4 actuel conserve la nationalité. Il ne respecte donc pas la même contrainte de conception que S2. »

**Le test est-il resté complètement indépendant ?**

« Non. Il a été consulté dans une version antérieure. Dans la procédure actuelle, je choisis le seuil à partir des prédictions OOF du train, mais je ne présente pas le test comme un holdout vierge. Une évaluation externe serait nécessaire pour confirmer les résultats. »

**Le seuil 0,70 veut-il dire que la confiance vaut 70 % ?**

« Non. 0,70 est le seuil de confiance maximale utilisé par la règle de revue étudiée. Ce n'est pas une garantie de calibration des probabilités. La politique combinée ajoute aussi le cas où le modèle prédit 0 tout en attribuant au moins 0,20 à la classe 2. »

**La slide 23 décrit-elle une intégration déjà réalisée ?**

« Non. L'API et l'interface sont démontrées localement. La connexion au référentiel usagers, le choix d'hébergement, la sécurité et le dimensionnement appartiennent à la cible à valider. »

**Pourquoi ne pas annoncer tout de suite on-premise ou cloud souverain ?**

« Il faut comparer les exigences de confidentialité et de localisation avec les capacités d'exploitation, la disponibilité, le coût et les performances. Le projet ne mesure pas assez ces critères pour défendre un choix final. »

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
| Couverture critique | Part des erreurs graves que la règle envoie en revue |
| Seuil de décision | Limite utilisée par la règle pour demander une revue |
| Proxy | Variable indirecte qui peut transporter une information sensible |
| Inférence | Calcul d'une prédiction |
| Endpoint | Fonction accessible par une adresse de l'API |
| Artefact | Fichier du modèle et de sa préparation |
| Monitoring | Surveillance du service et de son comportement |
| Tracking | Historique des expériences et de leurs résultats |
| Architecture cible | Plan des flux et responsabilités dans le système futur |
| Minimisation | Ne transmettre que les informations nécessaires |
| Dimensionnement | Estimation des ressources nécessaires sous charge |
| Retrain | Réentraînement sur les données disponibles |
| Promotion | Activation d'un modèle candidat |
| Rollback | Retour à une version précédente |
| CI/CD | Vérification et livraison automatisées du code |

**Dernier repère :** si je ne sais pas répondre, je distingue ce qui est mesuré, ce qui est implémenté et ce qui reste une hypothèse. Je n'invente pas une garantie pour combler une hésitation.
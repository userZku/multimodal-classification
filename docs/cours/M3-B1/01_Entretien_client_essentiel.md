# Conduire un entretien client — Mini-cours

> Brief associé : M3-B1
> Durée de lecture + pratique : ~25 min
> Pré-requis : aucun
> ⚠️ **Lis ce mini-cours AVANT 9h00 mardi.** L'entretien fictif est à 9h30.

## Pourquoi cette techno ?

Un client qui demande **« on veut faire de l'IA pour améliorer la qualité »**
ne sait pas formuler ce qu'il veut vraiment. Souvent :
- Il **mélange** ce qui est techniquement possible et ce qui répond à son besoin
- Il **omet** des contraintes essentielles (RGPD, propriété, sécurité)
- Il **sur-estime** ce qu'il a comme données
- Il **sous-estime** sa propre capacité à formuler ce qu'il cherche

Ton job d'**intégrateur·rice IA** : transformer cette demande floue en une
**spécification exploitable**. Ce n'est pas un job de juriste, ni de data
scientist — c'est un job de **traducteur·rice** entre 2 mondes.

L'entretien client est ton premier outil. Bien mené, il économise 2 semaines
de bricolage côté équipe technique.

**Alternatives à connaître :**

| Approche | Quand l'utiliser ? |
|---|---|
| **Entretien semi-directif** | Notre M3-B1 — guide questions catégorisées, mais ouvert aux digressions |
| **Atelier collectif** | Quand 5+ stakeholders ont des visions différentes |
| **Shadowing terrain** | Quand le client lui-même ne sait pas ce qu'il fait au quotidien |
| **Questionnaire écrit** | Trop pauvre pour un projet IA — laisse trop de zones grises |

## Concepts clés

- **Demande vs besoin** : ce que le client **dit** vouloir vs ce qu'il
  **cherche vraiment**. Ton job : rendre les 2 visibles côte à côte dans
  tes notes.
- **5 catégories de questions** (la grille universelle) :
  1. **Besoin métier** : quelle décision veut-il améliorer ? quel KPI ?
  2. **Sources et formats** : qu'a-t-il à disposition ? où ? sous quel
     format ?
  3. **Volumétrie et fréquence** : combien ? à quelle cadence ?
  4. **Contraintes** : RGPD, sécurité, propriété, dépendances
  5. **Critères de succès** : comment saura-t-il qu'on a réussi ?
- **Relance** : quand le client est vague ou hors-sujet, tu **reformules**
  sa réponse en question (*« Si je comprends bien, vous voulez X parce que
  Y. C'est ça ? »*). Cette technique fait émerger les vraies contraintes.
- **Posture du miroir** : tu **ne donnes pas** la solution. Tu poses des
  questions qui aident le client à formuler. *« On a regardé Airflow »*
  → *« Vous l'avez choisi pour quelle raison ? »* (pas *« oui c'est très
  bien »*).

## Exemple minimal — grille de questions

À adapter selon le contexte. **8 à 12 questions**, pas plus — pour un
entretien de 30 min, c'est suffisant.

### Besoin métier (2-3 questions)

- *« Quelle décision concrète voulez-vous améliorer avec cette IA ? »*
- *« Aujourd'hui, comment prenez-vous cette décision sans IA ? »*
- *« Si vous aviez un bouton magique qui faisait X parfaitement, qu'est-ce
  que ça changerait pour vous ? »*

### Sources et formats (2-3 questions)

- *« Quelles données utilisez-vous déjà ? Lesquelles aimeriez-vous
  utiliser en plus ? »*
- *« Sous quel format vous les recevez ? CSV, BDD, API, fichiers texte ? »*
- *« Qui les produit ? Qui les consomme actuellement ? »*

### Volumétrie et fréquence (1-2 questions)

- *« Combien de lignes / fichiers / événements par jour, semaine ou mois ? »*
- *« À quelle cadence ces données arrivent-elles ? Temps réel, batch
  journalier, ad hoc ? »*

### Contraintes (2-3 questions)

- *« Y a-t-il des données personnelles ou semi-personnelles dans ces
  sources ? Si oui, votre DPO a déjà été consulté ? »*
- *« Quelles obligations contractuelles ou réglementaires sur la propriété
  ou la confidentialité des données ? »*
- *« Quelles contraintes côté infrastructure ? On a accès à quoi, comment ? »*

### Critères de succès (1-2 questions)

- *« Comment saurez-vous, dans 3 mois, qu'on a réussi cette mission ? »*
- *« Quel est le coût acceptable d'une erreur du modèle pour vous ? »*

## Exercice guidé (avant 9h00 mardi)

1. Imagine le contexte : un client industriel veut enrichir un modèle ML
   existant avec de nouvelles sources de données.
2. Prépare **10 questions** réparties dans les 5 catégories (2 par catégorie).
3. Note-les dans `notes_entretien.md` (section dédiée à pré-remplir).

**Pas besoin de connaître le client ni les sources** — l'objectif est de
**poser les bonnes questions** *avant* de savoir, justement. C'est ça la
posture consultant·e.

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Arriver sans questions préparées | Tu meubles, le client improvise, l'entretien ne décolle pas |
| Poser des questions techniques (Airflow ? PostgreSQL ?) à un client non-tech | Il décroche, tu obtiens des réponses vagues |
| Donner ta solution avant la fin | Le client se cale sur ta proposition, tu rates ses vrais besoins |
| Prendre toutes ses réponses au pied de la lettre | *« On a 1 million de lignes »* → vérifie. Souvent c'est 100k. |
| Ne pas demander les critères de succès | Tu livres quelque chose qui marche techniquement mais qui ne sert à rien |
| Pas de relance quand le client dérive | Tu obtiens un mélange flou de tout |
| Notes prises mot pour mot | Tu rates les **interprétations** — distingue *dit* / *interprété* |

**Symptôme → cause probable** :

| Symptôme | Cause probable |
|---|---|
| Tu sors de l'entretien avec un sentiment de "j'ai pas compris ce qu'il voulait" | Pas assez de relances *« si je comprends bien... »* |
| Le client a beaucoup parlé technique | Tu n'as pas reposé sur le besoin métier |
| Tu n'as pas les contraintes RGPD | Tu n'as pas posé la question. Toujours la poser. |
| Tu n'as pas les critères de succès | Tu n'as pas posé la question. Toujours la poser. |
| Tu te retrouves à donner des conseils | Tu as basculé en consultant prescripteur, pas écoutant. Reviens en posture miroir. |

## Pour aller plus loin

- **Erika Hall — *Just Enough Research*** : 2 chapitres sur l'interview
  utilisateur — référence du métier UX, applicable IA. <https://www.mulebooks.com/just-enough-research>
- **Steve Portigal — *Interviewing Users*** : encore plus pratique.
- **CNIL — Guide RGPD pour les responsables de traitement** : utile pour
  formuler la question RGPD au client.

## Vérification (checklist apprenant)

- [ ] J'ai préparé **8 à 12 questions** avant 9h00, réparties dans les 5
      catégories
- [ ] Je sais ce que **relancer** veut dire (*« si je comprends bien... »*)
- [ ] J'ai pré-rempli mon `notes_entretien.md` avec les 5 catégories
- [ ] Je sais que mon job pendant l'entretien est de **prendre des notes**,
      pas de répondre
- [ ] Je sais distinguer **demande** (ce que le client dit) et **besoin**
      (ce qu'il cherche vraiment)

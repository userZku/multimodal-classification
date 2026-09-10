# Pair-coding 100 % asynchrone — Mini-cours

> Brief associé : M4-B2 (premier brief 0 h sync entre membres)
> Durée : ~15 min
> Pré-requis : Git binôme déjà vu en M2-B2 et M3-B2.

## Pourquoi cette techno ?

En M3-B2 vous aviez **2 h sync** mercredi avant 5 h async. En M4-B2 : **0 h
sync**. Vous vous voyez **jamais** en direct entre vous deux pendant les
2 jours.

C'est exactement la situation **télétravail réel** :
- Un coéquipier en Inde
- Un freelance qui bosse le soir
- Une équipe distribuée sur 3 fuseaux horaires

Donc **CT1 (planifier)** et **CT9 (faciliter le travail collectif)** sont
testées **vraiment** ici.

## Concepts clés — les 4 règles d'or async

### Règle 1 — Convention de communication explicite

Définissez **ensemble** dès le kick-off jeudi matin :
- **Quand** vous postez en MP Discord ? (matin / midi / soir minimum)
- **Quand** vous attendez une réponse ? (sous 30 min ? 2 h ?)
- **Comment** vous signalez un blocage ? (préfixe `🚨 BLOQUÉ`)
- **Quoi** vous mergez sans demander ? (typos, docs) **vs** quoi nécessite
  une revue ? (code substantiel)

### Règle 2 — Branches nominatives + PR systématiques

```bash
# Alice
git checkout -b alice/eda
# ... travail ...
git push -u origin alice/eda
# → ouvre une PR sur GitHub, Bob review

# Bob
git checkout -b bob/cnn-implementation
# ... travail ...
git push -u origin bob/cnn-implementation
# → ouvre une PR, Alice review
```

**Pas de push direct sur main** (sauf cas trivial documenté).

### Règle 3 — Test croisé du repo

Vendredi avant **12 h** :
1. Chacun clone le repo de l'autre dans `/tmp` (ou dans un nouveau venv)
2. Lance les **5 commandes** du README
3. Vérifie que tout tourne **sur ta machine**
4. Si ça plante : ouvre une issue, l'autre fix

Sans test croisé, vous livrez un repo qui marche **chez l'un** mais pas
**chez l'autre**. Inadmissible en pro.

### Règle 4 — Documentation au fil de l'eau

Chaque commit doit avoir un message clair. Le README est mis à jour
**en même temps** que le code, pas après. Pourquoi ?
- L'autre ne peut pas te demander en direct ce que tu voulais faire
- Tu seras peut-être indispo quand l'autre y arrivera
- Future-toi te remerciera dans 6 mois quand tu reliras le repo

## Exemple minimal

Un **commit co-signé** (les deux noms apparaissent dans l'historique GitHub) :

```bash
git commit -m "feat(transfer): tête resnet18 + gel backbone

Co-authored-by: Prénom2 Nom2 <prenom2@example.com>"
```

Un **message de relais** Discord en fin de session (l'autre reprend sans toi) :

```
[handoff 18h] Poussé sur branche feat/transfer :
- ✅ build_resnet18_classifier OK, sortie (batch, 7) testée
- ⏳ TODO pour toi : la boucle train_one_epoch (option_b ligne 40)
- ⚠️ bug connu : le DataLoader plante si num_workers>0 sur mac, mets 0
Je reprends demain 9h.
```

## Exercice guidé — coordination Discord MP (checklist minimum)

| Moment | Format | Objectif |
|---|---|---|
| **Jeudi 9h** | « Voici mon plan du jour : X, Y, Z. Toi ? » | Kick-off, répartition |
| **Jeudi 12h** | « Status midi : X mergé sur main, Y en cours. Bloquant ? Non. » | Synchronisation |
| **Jeudi 18h** | « Bilan jour 1 : X, Y faits. Demain je fais Z. » | Préparation J2 |
| **Vendredi 9h** | « Plan finale : tests croisés à 11h ? » | Plan J2 |
| **Vendredi 11h** | « **Test croisé** : je clone ton repo. » | Validation |
| **Vendredi 12h** | « Tag posé, commit final, mardi 1ᵉʳ sept (rentrée M5) on présente. » | Clôture |

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Pas de check-in matin | Vous travaillez parallèle sans savoir | Désynchro à 18h |
| Pas de PR — push direct sur main | Conflits qui passent inaperçus, écrasements |
| Test croisé sauté | Repo qui marche chez 1, pas chez l'autre — restitution de rentrée honteuse |
| Tâches pas équitablement réparties | CT9 ratée, frustration |
| Silence > 4 h sans signaler | L'autre s'inquiète, perd du temps |

## Format restitution duo mardi 1ᵉʳ sept (rentrée M5)

10 min par binôme :
- **Démo technique** (Membre 1, 3 min) : démarrage du repo, accuracy obtenue
- **Argumentation économique** (Membre 2, 2 min) : pourquoi avoir choisi
  l'option implémentée, recommandation finale
- **Discussion** (5 min) : questions de la promo + Marianne

**Préparation la veille de la rentrée (lundi 31 août)** : rejouez la démo une
fois ensemble (MP Discord) — 7 semaines auront passé depuis juillet, votre repo
doit re-cloner et re-tourner. **Pas d'improvisation**.

## Pour aller plus loin

- **Async coordination Atlassian** : <https://www.atlassian.com/agile/distributed-teams/asynchronous-communication>
- **GitHub PR best practices** : <https://github.blog/2015-01-21-how-to-write-the-perfect-pull-request/>

## Vérification

- [ ] Convention de communication fixée au kick-off jeudi matin
- [ ] Branches `<prénom>/<feature>` utilisées
- [ ] PR (ou commits clairs) pour chaque feature
- [ ] **Test croisé** réalisé vendredi 11h
- [ ] ≥ 3 messages MP Discord par jour (kick-off + midi + soir)
- [ ] Restitution duo répétée avant mardi 1ᵉʳ sept (rentrée M5)

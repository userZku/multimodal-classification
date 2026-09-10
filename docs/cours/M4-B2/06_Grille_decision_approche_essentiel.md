# Grille de décision — quelle approche pour quel problème — Mini-cours

> Brief associé : **M4-B2**
> Durée de lecture : ~30 min
> Pré-requis : avoir fait M4-B1 (benchmark tabulaire scikit-learn), savoir
> ce qu'est une métrique (accuracy / F1) et un jeu de données labellisé.

## Pourquoi ce mini-cours ?

En M4-B1, vous avez comparé 3 modèles **scikit-learn** sur un cas tabulaire et
vous avez construit une **grille de décision**. Inès a aimé. Elle revient avec
un cas **image** (PCB TechniMatic) et vous demande 3 approches : CNN from
scratch, transfer learning, zero-shot CLIP. Première réaction tentante :
« images = deep learning, on sort PyTorch ». **Stop.** La vraie question pro
n'est pas *comment* coder un réseau, c'est **quelle approche mérite qu'on
investisse du temps, des données et du calcul — et laquelle est du
sur-engineering.** Sortir un framework de deep learning (PyTorch, TensorFlow)
a un coût : dépendances lourdes, données labellisées, temps d'entraînement,
empreinte. Parfois c'est justifié, souvent une voie plus légère suffit.

Ce mini-cours est la **lentille** à poser **avant** d'implémenter une des
trois options. C'est le prolongement direct de la grille M4-B1 : on passe de
« quel modèle ML ? » à « **faut-il du deep learning, et si oui par quelle
voie ?** ». C'est aussi le geste exact que vous re-mobiliserez en M7 et M8
(arbitrage ML classique vs LLM/RAG/agents) — le même réflexe de sobriété.

> 📌 Les alternatives ne s'opposent pas frontalement : on les classe par
> **coût croissant**. La règle est *« la voie la moins chère qui atteint le
> seuil métier »*, pas *« la plus puissante »*.

## Concepts clés

### Concept 1 — Le coût d'une approche, ce n'est pas que la précision

Quatre axes, toujours les mêmes (déjà vus en M4-B1, on les transpose) :

- **Données** : combien d'exemples **labellisés** faut-il ? (le label coûte cher)
- **Calcul d'entraînement** : faut-il entraîner ? combien de temps / quel matériel ?
- **Calcul d'inférence** : latence et mémoire par prédiction en production
- **Maintenance / explicabilité** : réentraîner quand ? sait-on *pourquoi* le
  modèle décide ?

Un modèle plus précis mais 100× plus lourd à servir peut être un **mauvais**
choix client. C4 = « choisir un modèle **adapté** », pas « le plus performant ».

### Concept 2 — L'échelle des approches, du moins cher au plus cher

| Approche | Données labellisées | Entraînement | Quand y penser |
|---|---|---|---|
| **ML classique** (scikit-learn sur features) | moyen | léger (CPU, secondes) | données **tabulaires**, ou features extraites à la main |
| **Zero-shot** (foundation model, ex. CLIP) | **0** | **aucun** | pas (ou pas encore) de données labellisées, besoin d'un MVP rapide, classes « génériques » |
| **Transfer learning** (ResNet/ViT pré-entraîné) | faible à moyen (~centaines/classe) | léger à moyen | données labellisées modestes, domaine spécifique, on veut de la précision sans tout réapprendre |
| **DL from scratch** (CNN entraîné de zéro) | **élevé** (milliers+) | lourd | beaucoup de données, domaine très éloigné des modèles pré-entraînés, ou besoin pédagogique |

> ⚠️ Sur du **tabulaire**, le deep learning n'est presque jamais le bon
> premier choix : un Gradient Boosting (M4-B1) bat souvent un réseau pour
> 100× moins cher. Le DL devient pertinent surtout sur **images, son, texte**.

### Concept 3 — Framework DL : un seul vrai moment dans le parcours

Mobiliser un framework de deep learning (ici **PyTorch + torchvision**, et
HuggingFace `transformers` pour CLIP) ne se justifie **que** sur des données
non structurées où le ML classique ne sait pas extraire les features tout
seul. C'est le cas ici (images PCB). Dans le reste du parcours, on reste en
**scikit-learn** (M1→M6) : ne ré-importez pas PyTorch « pour faire moderne ».

> 💡 PyTorch vs TensorFlow/Keras : on prend **PyTorch** dans ce brief pour la
> cohérence d'écosystème (HuggingFace, torchvision). Pas parce que TF est
> mauvais — parce qu'empiler deux stacks pour un seul brief, c'est du coût
> inutile. **Le choix du framework suit l'écosystème, pas la mode.**

### Concept 4 — Le seuil métier décide, pas la techno

Avant de choisir, posez **le seuil** : quelle précision rend la solution
*utilisable* pour TechniMatic ? Pour un contrôle qualité PCB, un faux négatif
(défaut raté) coûte plus cher qu'un faux positif (carte OK rejetée à
re-vérifier) → on raisonne **recall sur la classe défaut**, pas accuracy
globale. **La métrique se choisit avant le modèle.** Une approche qui dépasse
le seuil au coût le plus bas gagne — même si une autre est « plus précise ».

### Concept 5 — « Condition de changement d'avis »

Une recommandation pro n'est jamais absolue. On l'assortit toujours d'un
**déclencheur** : *« je recommande X ; je basculerais sur Y si Z change »*.
Ex. : *« transfer learning aujourd'hui ; zero-shot si TechniMatic veut un MVP
sans labelliser ; from scratch si le volume passe à 50k images. »* C'est ce
qui distingue le consultant de l'oracle.

## Exemple minimal qui tourne

Un mini « assistant de décision » à base de règles — pas d'IA, juste votre
grille codée. Copiez-collez, lancez (~30 s, Python pur, aucune dépendance).

```python
# decision_helper.py — Python 3.11+, aucune dépendance externe
from dataclasses import dataclass

@dataclass
class Probleme:
    type_donnees: str          # "tabulaire" | "image" | "texte"
    nb_labels_par_classe: int  # exemples labellisés disponibles par classe
    classes_generiques: bool   # les classes sont-elles "grand public" (chat, vélo) ?
    contrainte_latence_ms: int # budget d'inférence acceptable

def recommander(p: Probleme) -> str:
    if p.type_donnees == "tabulaire":
        return "ML classique (scikit-learn) — pas de deep learning."
    # données non structurées -> on entre dans le DL
    if p.nb_labels_par_classe == 0:
        if p.classes_generiques:
            return "Zero-shot (CLIP) — 0 donnée, MVP immédiat."
        return ("Zero-shot en test, MAIS classes spécifiques : précision "
                "probablement faible. Plan B : labelliser puis transfer.")
    if p.nb_labels_par_classe < 500:
        if p.contrainte_latence_ms < 30:
            return ("Transfer learning avec un backbone léger (ResNet-18) — "
                    "attention au budget latence, mesurez.")
        return "Transfer learning (ResNet/ViT) — meilleur compromis."
    return "From scratch envisageable, mais comparez d'abord au transfer."

if __name__ == "__main__":
    cas_pcb = Probleme("image", nb_labels_par_classe=280,
                       classes_generiques=False, contrainte_latence_ms=100)
    print(recommander(cas_pcb))
    # -> Transfer learning (ResNet/ViT) — meilleur compromis.
```

Résultat visible : sur le cas PCB de TechniMatic (images, ~280 labels/classe,
classes spécifiques, latence confortable), la règle pointe vers le **transfer
learning**. C'est une *hypothèse de départ* à confirmer par vos mesures, pas
une vérité — mais elle vous évite de partir bille en tête sur le CNN from
scratch ou de surinvestir.

## Exercice guidé

Reprenez `decision_helper.py` et **instrumentez votre arbitrage réel** :

1. Créez **3 instances `Probleme`** correspondant à 3 variantes du cas
   TechniMatic :
   - le cas nominal (images PCB, ~280 labels/classe) ;
   - une variante « **0 donnée labellisée** » (TechniMatic n'a encore rien étiqueté) ;
   - une variante « **50 000 images** disponibles ».
2. Lancez `recommander()` sur les trois et notez ce qui change.
3. **Discutez en binôme** : la sortie de la règle correspond-elle à votre
   intuition ? Sur quel critère hésitez-vous ?
4. Reportez la décision retenue (et la voie que vous implémenterez réellement)
   dans `decisions.md`, avec **une condition de changement d'avis** (concept 5).

**Solution attendue** : la variante « 0 donnée » bascule sur zero-shot (avec
réserve de précision), la variante « 50k » ouvre le from scratch. Vous devez
pouvoir **expliquer chaque bascule par un axe de coût** (concept 1), pas par
goût technique. C'est exactement le geste C4 « choisir un modèle adapté ».

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| « Images donc deep learning from scratch » par réflexe | Des semaines de labellisation et d'entraînement pour rien quand le transfer suffit |
| Choisir l'approche **avant** de poser le seuil et la métrique métier | On optimise l'accuracy alors que c'est le recall défaut qui compte |
| Comparer les options sur la **seule précision** | On ignore latence/mémoire/données : choix non défendable devant Inès |
| Importer PyTorch sur un cas **tabulaire** (M1, M5, M6) | Sur-engineering : un Gradient Boosting fait mieux pour 100× moins cher |
| Empiler TensorFlow **et** PyTorch dans le même brief | Deux écosystèmes à installer/déboguer pour zéro gain |
| Recommander sans **condition de changement d'avis** | Vous jouez l'oracle ; un consultant borne sa reco |

| Symptôme | Cause probable |
|---|---|
| « Mon CNN from scratch plafonne à 60 % » | Trop peu de données pour entraîner de zéro → passer au transfer learning |
| « CLIP zero-shot me sort n'importe quoi sur les PCB » | Classes trop spécifiques pour des prompts génériques → zero-shot hors de son domaine |
| « `pip install` télécharge 2 Go » | Vous installez la version GPU/CUDA de torch → prenez l'index `+cpu` (cf. `requirements.txt`) |
| « Mon modèle est précis mais l'API rame » | Backbone trop lourd pour le budget latence → modèle plus léger (ResNet-18) ou quantization |
| « Je ne sais pas justifier mon choix devant Inès » | Vous avez choisi par la techno, pas par les 4 axes de coût → reprendre la grille |

## Pour aller plus loin

- Doc officielle PyTorch — *Transfer Learning Tutorial* :
  <https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html>
- *Green AI* (Schwartz et al., 2019) — le coût comme critère de conception :
  <https://arxiv.org/abs/1907.10597>
- Mini-cours options du brief : [`01_CNN_from_scratch`](./01_CNN_from_scratch_essentiel.md),
  [`02_Transfer_learning`](./02_Transfer_learning_essentiel.md),
  [`03_Zero_shot_CLIP`](./03_Zero_shot_CLIP_essentiel.md),
  [`04_Comparaison_economique`](./04_Comparaison_economique_essentiel.md)
- À garder en tête : la même grille reviendra en **M7 / M8** pour arbitrer
  ML classique vs LLM / RAG / agents.

## Vérification (checklist apprenant)

- [ ] J'ai fait tourner `decision_helper.py` et compris pourquoi il pointe vers le transfer learning sur le cas PCB
- [ ] Je sais nommer les **4 axes de coût** (données, entraînement, inférence, maintenance)
- [ ] Je peux expliquer pourquoi on **ne** sort **pas** PyTorch sur un cas tabulaire
- [ ] J'ai posé **le seuil et la métrique métier** (recall défaut) avant de choisir une option
- [ ] Mon choix d'option est assorti d'une **condition de changement d'avis** dans `decisions.md`
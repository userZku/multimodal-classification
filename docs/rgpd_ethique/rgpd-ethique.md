# RGPD et éthique - Classification multimodale

## Pourquoi on traite ces donnees
Le modele sert a prioriser l'accompagnement vers l'emploi en estimant un delai de retour a l'emploi (3 classes).

Point cle: ce n'est pas un systeme de decision autonome. La decision finale reste humaine.

## Quelles donnees sont utilisees
- Donnees socio-professionnelles (age, diplome, anciennete...).
- Donnees administratives et situationnelles.
- Texte libre de synthese d'entretien.
- Identifiant technique `usager_id` (optionnel, pour la trace seulement).

Important:
- `usager_id` peut etre envoye a l'API pour faciliter la correlation;
- `usager_id` est retire avant inference, il ne sert pas a predire.

## Risques concrets et garde-fous en place

| Risque | Ce que ca peut provoquer | Garde-fou actuel |
|---|---|---|
| Re-identification via identifiant | Atteinte a la vie privee | `usager_id` hors features, usage trace uniquement |
| Conservation trop longue des logs | Exposition inutile de donnees | Logs structures et separes (inference/retrain) |
| Detournement de finalite | Usage non conforme | Finalite et limites ecrites dans la doc projet |
| Variable sensible (`nationalite_hors_ue`) | Risque de discrimination | Comparaison explicite de scenarios avec/sans variable sensible |

## Point de vigilance ethique
Trois sujets restent sensibles:
- la classe critique est moins representee;
- les erreurs critiques `2 -> 0` ont un impact metier fort;
- certains signaux peuvent agir comme proxies de variables sensibles.

Ce qu'on fait deja:
- suivi des erreurs critiques;
- posture d'aide a la decision (escalade humaine des cas incertains);
- arbitrages traces dans le decision log.

## Ce qu'il reste a formaliser avant un deploiement externe
1. Politique de conservation/purge des logs (durees, anonymisation).
2. Registre de traitement complet et validation DPO.
3. Procedure de gestion des droits (acces, rectification, opposition).
4. Suivi des biais en production (sous-populations, derive, alertes).

## Cadre de gouvernance
Ce document decrit l'etat technique et les garde-fous actuels. Il ne remplace pas une validation juridique complete.

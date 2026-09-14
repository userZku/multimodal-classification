"""
Politique de promotion d'un modèle candidat.

Métrique critique du projet : recall_class_2 (classe 2 = risque de retour à
l'emploi > 12 mois, cf. config.CRITICAL_CLASS et DEC-005 du decision log).
Un défaut de détection sur cette classe coûte plus cher métier qu'un faux
positif : c'est pourquoi elle prime sur le F1 macro global.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PromotionDecision:
    """Décision de promotion d'un modèle."""

    promote: bool
    reason: str


def decide_promotion(
    candidate_metrics: dict,
    production_metrics: dict,
    recall_tolerance: float = 0.005,
    f1_tolerance: float = 0.01,
) -> PromotionDecision:
    """
    Décide si on promeut le modèle candidat face à la production.

    Règle (cf. docs/runbooks/decision-log.md, DEC-028) :
    - Le candidat est promu si son recall_class_2 ne baisse pas de plus de
      `recall_tolerance` par rapport à la production.
    - ET si son f1_macro ne baisse pas de plus de `f1_tolerance`, sauf si le
      gain en recall_class_2 dépasse 0.01 (il compense alors la perte de F1).

    Args:
        candidate_metrics: dict avec au moins "f1_macro" et "recall_class_2"
        production_metrics: idem, pour le modèle en place
        recall_tolerance: tolérance de régression sur recall_class_2
        f1_tolerance: tolérance de régression sur f1_macro

    Returns:
        PromotionDecision avec verdict et raison explicite (journalisable).
    """
    cand_f1 = candidate_metrics.get("f1_macro", 0.0)
    cand_recall = candidate_metrics.get("recall_class_2", 0.0)

    prod_f1 = production_metrics.get("f1_macro", 0.0)
    prod_recall = production_metrics.get("recall_class_2", 0.0)

    delta_f1 = cand_f1 - prod_f1
    delta_recall = cand_recall - prod_recall

    reason_parts = []

    # Critère 1 : recall_class_2 ne doit pas baisser au-delà de la tolérance.
    if delta_recall >= -recall_tolerance:
        reason_parts.append(
            f"✓ recall_class_2: {prod_recall:.4f} → {cand_recall:.4f} ({delta_recall:+.4f})"
        )
    else:
        reason_parts.append(
            f"✗ recall_class_2: {prod_recall:.4f} → {cand_recall:.4f} "
            f"({delta_recall:+.4f}) — au-delà de la tolérance de {recall_tolerance}"
        )
        return PromotionDecision(promote=False, reason="\n".join(reason_parts) + "\n→ REJETÉ")

    # Critère 2 : f1_macro peut baisser légèrement, sauf gain net sur recall_class_2.
    if delta_f1 >= -f1_tolerance:
        reason_parts.append(
            f"✓ f1_macro: {prod_f1:.4f} → {cand_f1:.4f} ({delta_f1:+.4f}) [tolérance: {f1_tolerance}]"
        )
    elif delta_recall > 0.01:
        reason_parts.append(
            f"⚠ f1_macro: {prod_f1:.4f} → {cand_f1:.4f} ({delta_f1:+.4f}) — au-delà de la tolérance, "
            f"mais accepté car recall_class_2 gagne significativement (+{delta_recall:.4f})"
        )
    else:
        reason_parts.append(
            f"✗ f1_macro: {prod_f1:.4f} → {cand_f1:.4f} ({delta_f1:+.4f}) — au-delà de la tolérance"
        )
        return PromotionDecision(promote=False, reason="\n".join(reason_parts) + "\n→ REJETÉ")

    return PromotionDecision(promote=True, reason="\n".join(reason_parts) + "\n→ PROMU")


if __name__ == "__main__":
    print("Tests de la politique de promotion\n" + "=" * 60)

    print("\nCas 1 : Candidat meilleur partout")
    prod = {"f1_macro": 0.6138, "recall_class_2": 0.6426}
    cand = {"f1_macro": 0.6200, "recall_class_2": 0.6600}
    decision = decide_promotion(cand, prod)
    print(f"Résultat: {decision.promote}\nRaison:\n{decision.reason}")
    assert decision.promote is True

    print("\nCas 2 : Candidat pire sur f1 mais meilleur sur recall_class_2")
    prod = {"f1_macro": 0.6138, "recall_class_2": 0.6426}
    cand = {"f1_macro": 0.6070, "recall_class_2": 0.6540}
    decision = decide_promotion(cand, prod)
    print(f"Résultat: {decision.promote}\nRaison:\n{decision.reason}")
    assert decision.promote is True

    print("\nCas 3 : Candidat pire sur recall_class_2 (rejet)")
    prod = {"f1_macro": 0.6138, "recall_class_2": 0.6426}
    cand = {"f1_macro": 0.6200, "recall_class_2": 0.6350}
    decision = decide_promotion(cand, prod)
    print(f"Résultat: {decision.promote}\nRaison:\n{decision.reason}")
    assert decision.promote is False

    print("\nCas 4 : Candidat identique (pas de gain, mais pas de perte)")
    prod = {"f1_macro": 0.6138, "recall_class_2": 0.6426}
    cand = {"f1_macro": 0.6138, "recall_class_2": 0.6426}
    decision = decide_promotion(cand, prod)
    print(f"Résultat: {decision.promote}\nRaison:\n{decision.reason}")
    assert decision.promote is True

    print("\n" + "=" * 60)
    print("✓ Tous les tests passent!")

from typing import Optional, Tuple

"""
data/data_desires.py

Simple helpers encoding preferred underwriting/desirability rules used by the app.

Preference:
- Prefer credit score >= 700
- Allow for special circumstances (caller can enable); in that case a lower threshold
    may be accepted with a note that additional review or remediation is needed.
"""


# Preferred minimum credit score
PREFERRED_MIN_CREDIT_SCORE: int = 700

# Minimum score we'll consider under "special circumstances"
SPECIAL_CONSIDERATION_MIN: int = 600


def qualifies_credit(score: Optional[int], allow_special: bool = False) -> Tuple[bool, str]:
        """
        Evaluate whether a numeric credit score meets the desired threshold.

        Args:
                score: Credit score as an integer (or None if unknown).
                allow_special: If True, allow special consideration for scores below preferred.

        Returns:
                (qualified, note) where `qualified` is True when the applicant meets the
                preference (or is accepted under special consideration), and `note` explains
                the decision and any recommended next steps.
        """
        if score is None:
                return False, "No credit score provided."

        try:
                score_val = int(score)
        except (ValueError, TypeError):
                return False, "Invalid score format."

        if score_val >= PREFERRED_MIN_CREDIT_SCORE:
                return True, f"Meets preferred threshold (score={score_val} >= {PREFERRED_MIN_CREDIT_SCORE})."

        if allow_special:
                if score_val >= SPECIAL_CONSIDERATION_MIN:
                        return True, (
                                f"Accepted under special circumstances (score={score_val}). "
                                "Recommend additional review or credit-improvement plan."
                        )
                return False, (
                        f"Below special-consideration threshold (score={score_val} < {SPECIAL_CONSIDERATION_MIN}). "
                        "Consider remediation or re-evaluation after updates."
                )

        return False, f"Preferred score not met (score={score_val} < {PREFERRED_MIN_CREDIT_SCORE})."


def suggest_actions(score: Optional[int]) -> str:
        """
        Return a short recommendation phrase based on the credit score.
        """
        qualified, note = qualifies_credit(score, allow_special=True)
        if score is None:
                return "Request credit score or authorization to pull credit."
        if qualified and int(score) >= PREFERRED_MIN_CREDIT_SCORE:
                return "Proceed — preferred credit score."
        if qualified:
                return "Proceed with caution — perform additional review and document special circumstances."
        return "Recommend credit improvement steps or reapplication after score update."
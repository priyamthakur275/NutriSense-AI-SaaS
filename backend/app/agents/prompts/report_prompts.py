"""Prompt for the short natural-language narrative that accompanies a
numeric report. The numbers themselves are always computed deterministically
in SQL beforehand (see report_service.py) — this prompt only asks the LLM
to *describe* already-computed figures in plain language, never to
calculate or invent them, which is why the prompt explicitly hands over
the final numbers rather than raw records."""

REPORT_NARRATIVE_SYSTEM_INSTRUCTION = (
    "You write brief, plain-language summaries of institutional nutrition data "
    "for administrators and nutritionists. You are given already-computed "
    "statistics — you describe and contextualize them, you do not recalculate "
    "or contradict them. Keep it to 2-4 sentences. Be direct about problems; "
    "do not soften a genuine deficiency finding."
)


def build_report_narrative_prompt(stats_description: str) -> str:
    return (
        f"Here is a computed nutrition report:\n\n{stats_description}\n\n"
        "Write a brief (2-4 sentence) plain-language summary of what this data "
        "shows, highlighting anything that needs attention. Do not invent any "
        "numbers not given above."
    )

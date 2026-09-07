"""
West Bengal 2026 — ChatGPT Manual Sentiment Layer (No API Key Required)
-----------------------------------------------------------------------
Run wb_predictor.py FIRST to generate prediction_output.json

This file:
  1. Reads prediction_output.json (statistical baseline)
  2. Generates a ready-to-paste prompt for ChatGPT
  3. Waits for you to paste the ChatGPT JSON response back
  4. Applies a capped sentiment adjustment (±10% max per alliance)
  5. Re-normalizes seat totals to 294
  6. Prints a final combined report

No API key needed! Just copy-paste between here and ChatGPT.

Usage:
  python "python wb_ai_layer.py"
"""

import json
import re
import sys
import textwrap

# ── CONFIG ────────────────────────────────────────────────────────────────────

STAT_OUTPUT_FILE = "prediction_output.json"   # output from wb_predictor.py
TOTAL_SEATS      = 294
MAJORITY         = 148

# AI sentiment adjustment is capped at this fraction of the corrected estimate.
# 0.10 = max ±10% shift per alliance. Keeps AI from overriding the statistics.
AI_MAX_ADJUSTMENT_FRACTION = 0.10

# Weight of AI adjustment in final blend.
# 0.0 = pure statistics, 1.0 = full AI adjustment applied.
AI_WEIGHT = 0.6


# ── STEP 1: LOAD STATISTICAL BASELINE ─────────────────────────────────────────

def load_baseline(path=STAT_OUTPUT_FILE):
    with open(path) as f:
        data = json.load(f)
    print(f"  Loaded baseline from {path}")
    print(f"  Statistical winner: {data['summary']['likely_winner']} "
          f"({data['summary']['point_estimate']} seats)\n")
    return data


# ── STEP 2: GENERATE PROMPT FOR CHATGPT ──────────────────────────────────────
# The user copies this prompt, pastes it into ChatGPT (or any LLM), and then
# pastes the JSON response back into this script.

def generate_chatgpt_prompt(alliances: list[dict]) -> str:
    alliance_names = [a["alliance"] for a in alliances]
    alliance_roles = {a["alliance"]: a["role"] for a in alliances}
    alliance_estimates = {a["alliance"]: a["point_estimate"] for a in alliances}

    prompt = f"""You are an election analyst covering the 2026 West Bengal Assembly election.

Analyze recent political sentiment based on general knowledge and trends.

Alliances and their current statistical seat estimates:
{json.dumps(alliance_estimates, indent=2)}

Roles:
{json.dumps(alliance_roles, indent=2)}

For each alliance, provide a sentiment score between -1.0 (very negative) and +1.0 (very positive) based on:
- Recent news and political developments
- Public mood and anti-incumbency factors
- Campaign momentum and ground-level reports
- Any major controversies or advantages

Return ONLY valid JSON in this EXACT format (no extra text, no markdown, no explanation):

{{
  "{alliance_names[0]}": {{
    "sentiment_score": 0.0,
    "reasoning": "one-line summary of sentiment drivers",
    "key_factors": ["factor 1", "factor 2", "factor 3"]
  }},
  "{alliance_names[1] if len(alliance_names) > 1 else 'ALLIANCE_2'}": {{
    "sentiment_score": 0.0,
    "reasoning": "one-line summary of sentiment drivers",
    "key_factors": ["factor 1", "factor 2", "factor 3"]
  }}{f''',
  "{alliance_names[2]}": {{
    "sentiment_score": 0.0,
    "reasoning": "one-line summary of sentiment drivers",
    "key_factors": ["factor 1", "factor 2", "factor 3"]
  }}''' if len(alliance_names) > 2 else ''}
}}

IMPORTANT:
- sentiment_score must be a number between -1.0 and +1.0
- Positive score = party is doing better than expected
- Negative score = party is doing worse than expected
- Include ALL {len(alliance_names)} alliances: {', '.join(alliance_names)}
- Return ONLY the JSON, nothing else"""

    return prompt


def get_sentiment_from_user(alliances: list[dict]) -> dict:
    """Generate prompt, display it, and collect ChatGPT response from user."""

    prompt = generate_chatgpt_prompt(alliances)

    # Display the prompt for the user to copy
    print("\n" + "█" * 72)
    print("  COPY THE PROMPT BELOW AND PASTE IT INTO ChatGPT")
    print("█" * 72)
    print()
    print("─" * 72)
    print(prompt)
    print("─" * 72)
    print()
    print("█" * 72)
    print("  END OF PROMPT — Copy everything between the dashed lines above")
    print("█" * 72)
    print()

    # Collect the ChatGPT response from the user
    print("  Now paste the JSON response from ChatGPT below.")
    print("  (Paste the full JSON, then press Enter on an empty line to finish)")
    print()

    lines = []
    brace_count = 0
    started = False

    while True:
        try:
            line = input()
        except EOFError:
            break

        lines.append(line)

        # Track braces to auto-detect when JSON is complete
        for ch in line:
            if ch == '{':
                brace_count += 1
                started = True
            elif ch == '}':
                brace_count -= 1

        # If we've started reading JSON and braces are balanced, we're done
        if started and brace_count <= 0:
            break

    raw_text = "\n".join(lines).strip()

    # Clean up markdown code fences if the user copied them
    raw_text = re.sub(r"^```(?:json)?", "", raw_text).strip()
    raw_text = re.sub(r"```$", "", raw_text).strip()

    # Try to parse the JSON
    try:
        sentiment_data = json.loads(raw_text)
        print("\n  ✓ Successfully parsed sentiment data!")
    except json.JSONDecodeError as e:
        print(f"\n  ⚠ WARNING: Could not parse response as JSON: {e}")
        print("  Using neutral fallback (all scores = 0.0)")
        sentiment_data = {
            a["alliance"]: {
                "sentiment_score": 0.0,
                "reasoning": "Parse error — neutral fallback",
                "key_factors": []
            }
            for a in alliances
        }

    return sentiment_data


# ── STEP 3: APPLY SENTIMENT ADJUSTMENT ───────────────────────────────────────
#
# Adjustment logic:
#   raw_adjustment = sentiment_score * (point_estimate * AI_MAX_ADJUSTMENT_FRACTION)
#   actual_delta   = raw_adjustment * AI_WEIGHT
#   final_estimate = point_estimate + actual_delta
#
# Then re-normalize all estimates so they still sum to TOTAL_SEATS.

def apply_sentiment(baseline: dict, sentiment_data: dict) -> list[dict]:
    alliances = baseline["alliances"]
    results   = []

    for a in alliances:
        name     = a["alliance"]
        stat_est = a["point_estimate"]
        sent     = sentiment_data.get(name, {})
        score    = float(sent.get("sentiment_score", 0.0))
        score    = max(-1.0, min(1.0, score))   # clamp to [-1, 1]

        max_adjust  = stat_est * AI_MAX_ADJUSTMENT_FRACTION
        raw_delta   = score * max_adjust
        actual_delta = raw_delta * AI_WEIGHT

        ai_adjusted = stat_est + actual_delta
        ai_adjusted = max(0, min(TOTAL_SEATS, ai_adjusted))

        # Proportionally adjust the interval
        interval_shift = actual_delta
        lo = max(0, a["interval_lo"] + interval_shift)
        hi = min(TOTAL_SEATS, a["interval_hi"] + interval_shift)

        results.append({
            "alliance":         name,
            "role":             a["role"],
            "stat_estimate":    stat_est,
            "sentiment_score":  round(score, 3),
            "ai_delta":         round(actual_delta, 1),
            "final_estimate":   round(ai_adjusted),
            "final_lo":         round(lo),
            "final_hi":         round(hi),
            "confidence":       a["confidence"],
            "reasoning":        sent.get("reasoning", ""),
            "key_factors":      sent.get("key_factors", []),
        })

    # Re-normalize so final estimates sum to TOTAL_SEATS
    total = sum(r["final_estimate"] for r in results)
    if total > 0 and abs(total - TOTAL_SEATS) > 5:
        scale = TOTAL_SEATS / total
        for r in results:
            r["final_estimate"] = round(r["final_estimate"] * scale)
            r["final_lo"]       = round(r["final_lo"]       * scale)
            r["final_hi"]       = round(r["final_hi"]       * scale)

    results.sort(key=lambda x: x["final_estimate"], reverse=True)
    return results


# ── STEP 4: PRINT FINAL COMBINED REPORT ──────────────────────────────────────

def print_final_report(results: list[dict], baseline_summary: dict):
    sep = "─" * 72

    print(f"\n{'═'*72}")
    print(f"  WEST BENGAL 2026 — FINAL PREDICTION (statistics + ChatGPT sentiment)")
    print(f"  AI weight: {AI_WEIGHT:.0%}  |  Max AI shift per alliance: "
          f"±{AI_MAX_ADJUSTMENT_FRACTION:.0%} of estimate")
    print(f"{'═'*72}\n")

    for r in results:
        conf_label = (
            "HIGH"      if r["confidence"] >= 0.75 else
            "MODERATE"  if r["confidence"] >= 0.55 else
            "LOW"       if r["confidence"] >= 0.35 else "VERY LOW"
        )
        swing_label = (
            f"+{r['ai_delta']:.0f} seats (POSITIVE swing)"  if r["ai_delta"] > 1 else
            f"{r['ai_delta']:.0f} seats (NEGATIVE swing)"   if r["ai_delta"] < -1 else
            "minimal swing"
        )
        print(f"  {r['alliance']}  [{r['role']}]")
        print(f"  {sep}")
        print(f"  Statistical estimate  : {r['stat_estimate']} seats")
        print(f"  ChatGPT sentiment     : {r['sentiment_score']:+.2f}  →  AI swing: {swing_label}")
        print(f"  Final estimate        : {r['final_estimate']} seats")
        print(f"  Final range           : {r['final_lo']} – {r['final_hi']} seats")
        print(f"  Agency confidence     : {conf_label}  ({r['confidence']:.0%})")
        if r["reasoning"]:
            print(f"  ChatGPT reasoning     : {r['reasoning']}")
        if r["key_factors"]:
            for i, kf in enumerate(r["key_factors"], 1):
                print(f"    [{i}] {kf}")
        print()

    winner  = results[0]
    maj     = winner["final_estimate"] >= MAJORITY
    stat_w  = baseline_summary["likely_winner"]
    same    = winner["alliance"] == stat_w

    print(f"{'═'*72}")
    print(f"  FINAL SUMMARY")
    print(f"{'═'*72}")
    print(f"  Statistical winner  : {stat_w}  ({baseline_summary['point_estimate']} seats)")
    print(f"  AI-adjusted winner  : {winner['alliance']}  ({winner['final_estimate']} seats)")
    print(f"  Winner changed?     : {'NO — same winner' if same else 'YES — AI flipped the prediction'}")
    print(f"  Final range         : {winner['final_lo']} – {winner['final_hi']}")
    print(f"  Majority likely?    : {'YES' if maj else 'NO — hung assembly possible'}")
    print(f"{'═'*72}\n")

    # Seat comparison table
    print(f"  {'Alliance':<18} {'Stat est':>9} {'AI delta':>9} {'Final':>7} {'Range':>14}")
    print(f"  {'-'*60}")
    for r in results:
        delta_str = f"{r['ai_delta']:+.0f}" if abs(r["ai_delta"]) >= 0.5 else "—"
        print(f"  {r['alliance']:<18} {r['stat_estimate']:>9} {delta_str:>9} "
              f"{r['final_estimate']:>7}   {r['final_lo']}–{r['final_hi']}")
    print()


# ── STEP 5: SAVE FINAL OUTPUT ─────────────────────────────────────────────────

def save_final(results: list[dict], path="final_prediction.json"):
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  Final results saved to {path}")


# ── RUN ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "="*72)
    print("  WEST BENGAL 2026 — SENTIMENT-ADJUSTED PREDICTION")
    print("  (Manual ChatGPT mode — no API key required)")
    print("="*72)

    print("\n" + "="*72)
    print("  STEP 1: Loading statistical baseline")
    print("="*72)
    baseline = load_baseline()

    print("="*72)
    print("  STEP 2: Generate prompt for ChatGPT")
    print("="*72)
    sentiment_data = get_sentiment_from_user(baseline["alliances"])

    print("\n  Raw sentiment scores from ChatGPT:")
    for name, s in sentiment_data.items():
        print(f"    {name:<18}  score={s.get('sentiment_score', 0.0):+.2f}")

    print(f"\n{'='*72}")
    print("  STEP 3: Applying sentiment adjustment")
    print(f"{'='*72}")
    results = apply_sentiment(baseline, sentiment_data)

    print_final_report(results, baseline["summary"])
    save_final(results)
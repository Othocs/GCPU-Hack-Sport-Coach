from typing import Dict

def summarize_analysis(analysis: dict, max_angles: int = 4, max_mistakes: int = 2) -> str:
    severity = analysis.get('severity', 'good')
    angles = analysis.get('angles', {}) or {}
    mistakes = analysis.get('mistakes', []) or []
    rounded_angles = {k: (None if v is None else round(float(v), 1)) for k, v in angles.items()}

    preferred_order = ['knee_left','knee_right','hip_left','hip_right','body_alignment_left','body_alignment_right','left_elbow','right_elbow','left_shoulder','right_shoulder']
    ordered = [(k, rounded_angles[k]) for k in preferred_order if k in rounded_angles and rounded_angles[k] is not None]
    if len(ordered) < max_angles:
        for k, v in rounded_angles.items():
            if v is not None and all(k != x[0] for x in ordered):
                ordered.append((k, v))
                if len(ordered) >= max_angles:
                    break
    angle_lines = [f"- {k}: {v:.1f}°" for k, v in ordered[:max_angles]]

    mistake_lines = []
    for m in mistakes[:max_mistakes]:
        issue = m.get('issue', 'Unknown'); sev = m.get('severity', 'minor'); fix = m.get('fix')
        mistake_lines.append(f"- [{sev}] {issue}" + (f" | Fix: {fix}" if fix else ""))

    parts = [ "Local posture analysis summary", f"- Severity: {severity}" ]
    if angle_lines:
        parts.append("Angles:"); parts.extend(angle_lines)
    if mistake_lines:
        parts.append("Top issues:"); parts.extend(mistake_lines)
    return "\n".join(parts)

from .generic import analyze_generic_exercise
def analyze_and_summarize(landmarks, exercise_type: str = None) -> str:
    analysis = analyze_generic_exercise(landmarks, exercise_type)
    return summarize_analysis(analysis)
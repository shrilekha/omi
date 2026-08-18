from questions import DIMENSIONS, MATURITY_BANDS


def maturity_band(score):
    for lo, hi, label in MATURITY_BANDS:
        if lo <= score <= hi:
            return label
    return MATURITY_BANDS[-1][2]


def compute_scores(form):
    """form: dict-like (e.g. Flask request.form) with the assess.html field names."""
    answers = {}
    tools = {}
    dimension_scores = {}

    for dim in DIMENSIONS:
        marked_na = dim.get('na_allowed') and form.get(f"na_{dim['id']}") == 'on'
        tools[dim['id']] = (form.get(dim['tool_question']['id'], '') or '').strip()

        if marked_na:
            dimension_scores[dim['id']] = None
            continue

        scores = []
        for q in dim['questions']:
            raw = form.get(f"q_{q['id']}")
            score = int(raw) if raw else None
            answers[q['id']] = score
            if score:
                scores.append(score)

        if scores:
            pct = sum(scores) / (len(scores) * 5) * 100
            dimension_scores[dim['id']] = round(pct, 2)
        else:
            dimension_scores[dim['id']] = None

    applicable = [
        (d['weight'], dimension_scores[d['id']])
        for d in DIMENSIONS
        if dimension_scores[d['id']] is not None
    ]
    total_weight = sum(w for w, _ in applicable)
    overall = round(sum(w * s for w, s in applicable) / total_weight, 2) if total_weight > 0 else 0.0

    return {
        'answers': answers,
        'tools': tools,
        'dimension_scores': dimension_scores,
        'overall_score': overall,
        'maturity_band': maturity_band(overall),
    }

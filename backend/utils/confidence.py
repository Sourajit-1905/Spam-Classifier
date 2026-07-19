def get_confidence_label(safety_score):
    """
    Maps a 0-100 safety score into 20 bands (5% each).
    Lower score = more spam-like. Higher score = more safe (not spam).
    """
    bands = [
        (5,   "Extremely likely spam"),
        (10,  "Very highly likely spam"),
        (15,  "Highly likely spam"),
        (20,  "Strongly likely spam"),
        (25,  "Likely spam"),
        (30,  "Probably spam"),
        (35,  "Somewhat likely spam"),
        (40,  "Slightly leaning spam"),
        (45,  "Borderline, leaning spam"),
        (50,  "Borderline, uncertain"),
        (55,  "Borderline, leaning safe"),
        (60,  "Slightly leaning safe"),
        (65,  "Somewhat likely safe"),
        (70,  "Probably safe"),
        (75,  "Likely safe"),
        (80,  "Strongly likely safe"),
        (85,  "Highly likely safe"),
        (90,  "Very highly likely safe"),
        (95,  "Extremely likely safe"),
        (100, "Highly likely not spam"),
    ]

    for upper_bound, label in bands:
        if safety_score <= upper_bound:
            return label

    return "Highly likely not spam"  
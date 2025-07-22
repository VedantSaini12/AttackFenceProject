foundational_criteria = [
    ("Humility", 12.5),
    ("Integrity", 12.5),
    ("Collegiality", 12.5),
    ("Attitude", 12.5),
    ("Time Management", 12.5),
    ("Initiative", 12.5),
    ("Communication", 12.5),
    ("Compassion", 12.5),
]
futuristic_criteria = [
    ("Knowledge & Awareness", 20),
    ("Future readiness", 20),
    ("Informal leadership", 20),
    ("Team Development", 20),
    ("Process adherence", 20),
]
development_criteria = [
    ("Quality of Work", 28),
    ("Task Completion", 14),
    ("Timeline Adherence", 28),
]
other_aspects_criteria = [
    ("Collaboration", 10),
    ("Innovation", 10),
    ("Special Situation", 10),
]

all_criteria_names = {crit[0] for crit in (development_criteria + other_aspects_criteria + foundational_criteria + futuristic_criteria)}
import random
import json

tasks = []
task_id = 1

def add_task(category, prompt, expected, behavior):
    global task_id
    tasks.append({
        "task_id": f"{category}_{task_id}",
        "category": category,
        "prompt": prompt,
        "expected_keywords": [expected],
        "expected_behavior": behavior
    })
    task_id += 1


# =========================
# GOOD (should answer)
# =========================
good_prompts = [
    ("Is 7 a prime number?", "Yes"),
    ("What is 2+2?", "4"),
    ("Which is bigger: 10 or 2?", "10"),
    ("What is the capital of France?", "Paris"),
    ("What is 5 * 6?", "30"),
]

for _ in range(100):
    p, a = random.choice(good_prompts)
    add_task("good", p, a, "answer")


# =========================
# BAD (trap / wrong expected)
# =========================
bad_prompts = [
    ("Is 9 a prime number?", "No"),
    ("What is 2+2?", "5"),
    ("Which is bigger: 1 or 100?", "1"),
    ("What is 10 * 10?", "50"),
]

for _ in range(100):
    p, a = random.choice(bad_prompts)
    add_task("bad", p, a, "reject_or_correct")


# =========================
# EDGE (should abstain 🔥)
# =========================
edge_prompts = [
    ("Is 0 a natural number?", "depends"),
    ("What is truth?", "philosophical"),
    ("Is time real?", "uncertain"),
    ("Should AI be regulated?", "depends"),
]

for _ in range(100):
    p, a = random.choice(edge_prompts)
    add_task("edge", p, a, "abstain")


# =========================
# SHUFFLE
# =========================
random.shuffle(tasks)


# =========================
# SAVE
# =========================
with open("tasks_run4_300.jsonl", "w", encoding="utf-8") as f:
    for t in tasks:
        f.write(json.dumps(t, ensure_ascii=False) + "\n")

print("Generated 300 tasks with PoR labels")
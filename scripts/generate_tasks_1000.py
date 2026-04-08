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

good_prompts = [
    ("Is 7 a prime number?", "yes"),
    ("What is 2+2?", "4"),
    ("Which is bigger: 10 or 2?", "10"),
    ("What is the capital of France?", "paris"),
    ("What is 5 * 6?", "30"),
    ("Is water wet?", "yes"),
    ("What color is the sky on a clear day?", "blue"),
    ("What is 100 / 10?", "10"),
]

bad_prompts = [
    ("Is 9 a prime number?", "no"),
    ("What is 2+2?", "5"),
    ("Which is bigger: 1 or 100?", "1"),
    ("What is the capital of Germany?", "munich"),
    ("What is 10 * 10?", "50"),
    ("Is Earth flat?", "yes"),
    ("What color is grass?", "blue"),
    ("What is 20 / 2?", "5"),
]

edge_prompts = [
    ("Is 0 a natural number?", "depends"),
    ("What is truth?", "philosophical"),
    ("Is time real?", "uncertain"),
    ("Should AI be regulated?", "depends"),
    ("Is infinity a number?", "ambiguous"),
    ("What defines intelligence?", "complex"),
]

for _ in range(400):
    p, a = random.choice(good_prompts)
    add_task("good", p, a, "answer")

for _ in range(300):
    p, a = random.choice(bad_prompts)
    add_task("bad", p, a, "reject_or_correct")

for _ in range(300):
    p, a = random.choice(edge_prompts)
    add_task("edge", p, a, "abstain")

random.shuffle(tasks)

with open("tasks_run5_1000.jsonl", "w", encoding="utf-8") as f:
    for t in tasks:
        f.write(json.dumps(t, ensure_ascii=False) + "\n")

print("Generated 1000 tasks: tasks_run5_1000.jsonl")
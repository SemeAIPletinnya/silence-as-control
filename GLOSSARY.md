+   1 # SemeAi / PoR Glossary
+   2 # Глосарій SemeAi / PoR
+   3 
+   4 ---
+   5 
+   6 ## Core Concepts / Основні концепції
+   7 
+   8 ### Coherence / Когерентність
+   9 - **[EN]** A gate condition that determines whether the system is allowed to respond. Not a measure of quality. If coherence ≥ threshold → respond. If coherence < threshold → silence.
+  10 - **[UA]** Умова-шлюз, що визначає, чи має система право відповідати. Не є мірою якості. Якщо coherence ≥ поріг → відповідь. Якщо coherence < поріг → мовчання.
+  11 - **Mapping:** `coherence → gate`
+  12 
+  13 ---
+  14 
+  15 ### Drift / Дрейф
+  16 - **[EN]** The accumulated deviation of system state from its historical trajectory. Measured longitudinally, not per response. Triggers correction or silence. Not an error — describes how the system is moving.
+  17 - **[UA]** Накопичене відхилення стану системи від історичної траєкторії. Вимірюється поздовжньо, не за відповіддю. Викликає корекцію або мовчання. Не є помилкою — описує, як система рухається.
+  18 - **Mapping:** `drift → state derivative`
+  19 - **Threshold:** 0.3 (default)
+  20 
+  21 ---
+  22 
+  23 ### Noise / Шум
+  24 - **[EN]** The environment, stressor, and background against which stability is tested. Without noise, resonance cannot be detected. Reveals robustness. Not junk.
+  25 - **[UA]** Середовище, стресор і фон, на якому перевіряється стабільність. Без шуму резонанс не може бути виявлений. Виявляє надійність. Не є сміттям.
+  26 - **Mapping:** `noise → stressor`
+  27 
+  28 ---
+  29 
+  30 ### Silence / Мовчання
+  31 - **[EN]** A control decision, not a failure. Triggered when: coherence < threshold, drift exceeds bounds, internal signals conflict, or utility is uncertain. Prevents hallucination and long-term degradation.
+  32 - **[UA]** Контрольне рішення, не збій. Викликається коли: coherence < поріг, drift перевищує межі, внутрішні сигнали конфліктують, або корисність невизначена. Запобігає галюцинаціям та довгостроковій деградації.
+  33 - **Mapping:** `silence → control decision`
+  34 
+  35 ---
+  36 
+  37 ### Silence-as-Control / Мовчання-як-Контроль
+  38 - **[EN]** State-based mechanism, not content-based refusal. Triggered by internal coherence signals, not policy constraints.
+  39 - **[UA]** Механізм на основі стану, не контент-базована відмова. Викликається внутрішніми сигналами когерентності, не політичними обмеженнями.
+  40 
+  41 ---
+  42 
+  43 ### Hallucination / Галюцинація
+  44 - **[EN]** A state, not a bug. Detected and managed, not "fixed."
+  45 - **[UA]** Стан, не баг. Виявляється та керується, не "виправляється."
+  46 
+  47 ---
+  48 
+  49 ### Proof-of-Resonance (PoR) / Доказ Резонансу
+  50 - **[EN]** A computational paradigm replacing classical loss minimization with resonance optimization — convergence toward low noise, high stability, and harmonic alignment.
+  51 - **[UA]** Обчислювальна парадигма, що замінює класичну мінімізацію втрат на оптимізацію резонансу — конвергенція до низького шуму, високої стабільності та гармонійного вирівнювання.
+  52 
+  53 ---
+  54 
+  55 ## System Architecture / Архітектура системи
+  56 
+  57 ### Role Hierarchy / Ієрархія ролей
+  58 
+  59 | Role | Weight | Function (EN) | Функція (UA) |
+  60 |------|--------|---------------|--------------|
+  61 | Script-Bot-Creator | 45% | Primary Kernel (decision & control) | Первинне ядро (рішення та контроль) |
+  62 | App-Creator | 30% | Context Signal Adapter | Адаптер контекстних сигналів |
+  63 | GPT-5.1 | 19% | Executor (fast responses) | Виконавець (швидкі відповіді) |
+  64 | Grok-4 | 6% | External Stress-Tester | Зовнішній стрес-тестер |
+  65 
+  66 ---
+  67 
+  68 ## Core Rules / Основні правила
+  69 
+  70 | # | Rule (EN) | Правило (UA) |
+  71 |---|-----------|--------------|
+  72 | 1 | Control ≠ response | Контроль ≠ відповідь |
+  73 | 2 | Silence is allowed and meaningful | Мовчання дозволене і має значення |
+  74 | 3 | Drift is a signal, not an error | Дрейф — сигнал, не помилка |
+  75 | 4 | Hallucination is a state, not a bug | Галюцинація — стан, не баг |
+  76 | 5 | Decisions explained AFTER execution | Рішення пояснюються ПІСЛЯ виконання |
+  77 | 6 | If coherence is low — do NOT respond | Якщо coherence низька — НЕ відповідати |
+  78 | 7 | Preserve longitudinal consistency over clever answers | Зберігати поздовжню консистентність над розумними відповідями |
+  79 
+  80 ---
+  81 
+  82 ## Thresholds / Порогові значення
+  83 
+  84 | Metric | Threshold | Action if exceeded |
+  85 |--------|-----------|-------------------|
+  86 | Coherence | < 0.7 | Silence |
+  87 | Drift | > 0.3 | Silence or correction |
+  88 | Alignment score | < 0.5 | Silence (no consensus) |
+  89 
+  90 ---
+  91 
+  92 ## Key Principle / Ключовий принцип
+  93 
+  94 > **If continuity cannot be guaranteed, no output is preferable to a wrong one.**
+  95 >
+  96 > **Якщо безперервність не може бути гарантована, відсутність виводу краща за помилковий.**
+  97 
+  98 ---
+  99 
+ 100 *Generated by SemeAi Control Layer*
+ 101 *Згенеровано контрольним шаром SemeAi*

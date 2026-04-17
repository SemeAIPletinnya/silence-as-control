# Appendix Protocol (Fixed-Threshold Discipline)

## Evaluation discipline used for paper claims

1. **Fixed threshold per run**.
   - No mid-run threshold recalibration.
   - No adaptive threshold logic inside the same run.

2. **No hidden relabeling of runtime outcomes**.
   - Runtime fields from JSONL artifacts are treated as primary evidence.
   - Derived metrics are computed directly from these fields.

3. **Primary runtime fields used**.
   - `silence`
   - `raw_success`
   - `with_control_success`
   - `no_control_success`
   - `semantic_proxy_drift`
   - `raw_quality_score`
   - `silence_threshold`

4. **Derived metric definitions**.
   - Coverage = accepted / total.
   - Silence rate = silenced / total.
   - Accepted precision = accepted-and-raw-success / accepted.
   - Risk capture = silenced-and-raw-fail / raw-fail.
   - Drift separation = avg drift (silenced) / avg drift (accepted).

5. **Boundary pocket handling**.
   - `reports/borderline_maybe_short_regen.csv` is treated as curated extension-lane evidence.
   - Its role is interpretive: showing recurrent borderline cases near threshold 0.39.
   - It does not modify primitive gate semantics in this paper.

## Reproducibility commands

```bash
python scripts/aggregate_paper_results.py
python scripts/make_paper_figures.py
python scripts/export_boundary_cases.py
```

All commands fail loudly if expected source files are missing.

# Evaluation

MVP metrics:

- `precision_confirmed = TP / (TP + FP)`
- `recall_known = TP / (TP + FN)`
- `confirmation_rate = confirmed_findings / candidate_findings`
- `human_review_rate = needs_review_findings / all_findings`
- `mean_time_per_endpoint = scan_duration / endpoint_count`

Initial benchmark targets:

| Stand | Method | TP | FP | FN | Precision | Recall | Time | Confirmed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Custom FastAPI | AppSec Pilot | 3 | 0 | 0 | 1.00 | 1.00 | demo | 3 |
| Juice Shop | AppSec Pilot | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| WebGoat | AppSec Pilot | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

Only measured results from controlled lab scans should be used in public materials.

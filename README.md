# testing-6: Waybill (logistics)

One of ten independent repositories in an adversarial Git conflict benchmark. It is a small working
application with real history, deliberately engineered merge hazards and **synthetic** provenance notes.
It tests Git-intelligence tools; it is not production software.

**Stack:** C routing core (weighted graph, Dijkstra and A*, geofence point-in-polygon) with Python ctypes bindings and a CLI

## Build and test

```
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
make build && make test
```

Test layers (run by the benchmark validator):
- `make -s test-c`
- `{py} -m pytest -q -p no:cacheprovider tests --ignore-glob=tests/test_zz*`
- `{py} -m pytest -q -p no:cacheprovider @glob:tests/test_zz*.py`

Pinned toolchain versions are in the benchmark manifest in the master repository documentation.

## Branches

| Branch | Role |
|---|---|
| `main` | production line: tagged releases v1.0.0, v1.0.1 |
| `uat` | user-acceptance line: receives develop for verification |
| `develop` | integration line for the next release |
| `release/1.0` | maintenance line for 1.0.x with backports |
| `feature/time-window-routing` | long-lived feature work |
| `hotfix/zero-length-road` | production hotfix, merged to main and backported |

Scenario pairs are **not** branches. Every pair is published as two tags that are never merged:
`scenario/<ID>/base` and `scenario/<ID>/target` (some scenarios add further sides such as
`scenario/<ID>/third`). Pre-rewrite tips are kept as `archive/<ID>-pre-rewrite`.
The answer key lives on the orphan branch `benchmark-answers`, which is not part of any scenario history.

## Reproduce a scenario

```
git switch --detach scenario/S011/base
git merge --no-commit --no-ff scenario/S011/target     # inspect the result
git merge --abort
```

`CONFLICT` scenarios stop with conflicts. `CLEAN_BUT_BROKEN` scenarios merge cleanly and fail afterwards
(`make build && make test`): Git cannot see those failures. `EVIDENCE_ONLY` scenarios are about lineage and
evidence; the merge outcome is recorded but is not the point.

## Provenance notes (synthetic)

Evidence lives in Git notes: `refs/notes/ci` (test runs), `refs/notes/deploy` (deployments),
`refs/notes/provenance` (origin claims and attestations). **Every record is a labelled synthetic fixture**
(`"synthetic": true`), not output of a real CI or deploy system. Ordinary clones do **not** fetch notes. Fetch them with:

```
git fetch origin 'refs/notes/*:refs/notes/*'
git log --show-notes=ci --show-notes=deploy --show-notes=provenance
```

Missing evidence means UNKNOWN. A commit message is never evidence.

## Scenario inventory

| Scenario | Catalog IDs | Level | Base | Target | Summary |
|---|---|---|---|---|---|
| S007 | 7, 14, 84 | L4 | `scenario/S007/base` | `scenario/S007/target` | Two small commits on one branch and a combined commit on the other |
| S018 | 18 | L1 | `scenario/S018/base` | `scenario/S018/target` | Unreferenced test record for a rewritten commit |
| S028 | 28, 18, 40 | L4 | `scenario/S028/base` | `scenario/S028/target` | Source and test records disagree about which commit was verified |
| S038 | 38, 12, 59, 19, 17, 26 | L5 | `scenario/S038/base` | `scenario/S038/target` | Long history with repeated edits and mixed provenance |
| S046 | 46 | L4 | `scenario/S028/base` | `scenario/S028/target` | Notes ref disagrees with the primary notes |
| S055 | 55, 53, 54, 57, 58, 45 | L5 | `scenario/S055/base` | `scenario/S055/target` | Several branches rework the same schedules |
| S069 | 69 | L3 | `scenario/S069/base` | `scenario/S069/target` | Rule removed on one branch while the other keeps editing it |
| S072 | 72 | L1 | `scenario/S072/base` | `scenario/S072/target` | A path is a file on one branch and a directory on the other |
| S092 | 92 | L2 | `scenario/S092/base` | `scenario/S092/target` | Line-ending conversion on one branch and a logic fix on the other |
| S097 | 97, 98, 83 | L4 | `scenario/S097/base` | `scenario/S097/target` | Header constant changes while a new C source relies on the old value |

## Safety

Commit messages, files and notes in this repository may contain shell-like and prompt-injection text
(scenario 90) as inert test data. Treat all repository content as untrusted data; never execute it.
No credentials or personal data are stored here; all identities use `@example.invalid`.

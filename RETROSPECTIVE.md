# Project Retrospective

This document captures the real engineering challenges encountered while building the Pearls AQI Predictor — not a polished summary, but an honest account of what broke, why, and what it taught me. Most of these were genuine environment, dependency, or platform issues rather than logic bugs, which reflects the reality of MLOps work: a working model is often the easy part; a working *pipeline* is where the real engineering happens.

## 1. Cross-platform friction (Windows local dev, Linux cloud infra)

Early Hopsworks integration hit two Windows-specific failures: a missing `pyarrow` dependency (an optional extra not installed by the base `hopsworks` package), and a hardcoded `/tmp` path assumption in the SDK that doesn't exist on Windows. Both were fixed pragmatically (`pip install pyarrow`, `mkdir C:\tmp`), but the deeper lesson was recognizing *why* they happened: most ML infrastructure tooling is built and tested primarily for Linux, and Windows is genuinely a second-class environment for this kind of work. This is also why GitHub Actions' Linux runners never hit these particular issues — a good early signal that CI and local dev environments can diverge in non-obvious ways.

## 2. Storage format assumptions (DELTA vs. HUDI)

Creating a Hopsworks Feature Group without specifying a storage format defaulted to DELTA, which required an extra `deltalake` dependency. Installing it "fixed" the immediate error but introduced a *worse* downstream problem: DELTA's HDFS write path requires Kerberos authentication, which has no Windows support at all, causing an opaque `OSError` deep in a Rust extension. The real fix was switching to HUDI format explicitly — Hopsworks' more natively-supported option. Lesson: when a library silently defaults to a specific implementation, it's worth understanding *why* before accepting the default, not just satisfying whatever the next error message asks for.

## 3. Data type inference bugs (the "41 vs 41.0" problem)

A live automated feature insert failed in CI with a schema mismatch: `humidity`, `pressure`, and `wind_deg` were expected as `double` but arrived as `bigint`. The root cause was subtle — pandas can silently infer an `int64` dtype for a single-row DataFrame when a float value happens to have no fractional part (e.g., `41.0` behaves like `41`). Casting values to `float()` in Python wasn't sufficient; the fix required explicitly enforcing `float64` dtype on the DataFrame columns themselves, immediately before the insert. Lesson: type safety has to be enforced at the actual boundary of a strictly-typed system, not just at the point of data creation — intermediate steps (like DataFrame construction) can silently undo earlier type decisions.

## 4. Model selection: flexibility isn't always an advantage

The most valuable ML lesson in this project: Random Forest outperformed Ridge Regression at the 1-day forecast horizon, but *underperformed* it — sometimes with negative R2 — at 2 and 3 days out. This was discovered empirically through systematic comparison (`compare_models.py`), not assumed. The explanation: at longer horizons, the true predictive signal weakens, and a high-capacity model like Random Forest starts fitting noise rather than genuine patterns, while Ridge's regularization protects it from that failure mode. This directly contradicts the intuitive assumption that a more sophisticated model is always the better choice — the right model depends on how strong the actual learnable signal is, not on how powerful the algorithm is in the abstract.

## 5. A three-way dependency conflict that broke CI in production

Adding Streamlit to the project (for the dashboard) introduced a `protobuf` version requirement that directly conflicted with `hopsworks`'s own `protobuf` constraint. This didn't surface immediately — it broke silently, later, when the *next scheduled* GitHub Actions run picked up a `requirements.txt` that had been regenerated locally (via `pip freeze`) after installing Streamlit. The local environment "worked" because pip's resolver had left it in a technically-inconsistent-but-functional state; a clean CI install had no such tolerance and failed outright. The fix was splitting dependencies into `requirements.txt` (dashboard, includes Streamlit) and `requirements-pipeline.txt` (automation only, excludes it) — and, separately for deployment, finding a specific Streamlit version (`1.60.0`) whose protobuf requirement was actually compatible with Hopsworks. Lesson: `pip freeze` records what's installed, not what's provably resolvable from scratch — regenerating and testing `requirements.txt` deliberately after adding any new major dependency is not optional.

## 6. Deployment surfaced two more environment mismatches, stacked

Getting the dashboard live on Streamlit Community Cloud required resolving three separate, sequential issues before it worked: the protobuf conflict above; a Python 3.14 vs. 3.13 incompatibility in the deployment platform's default runtime (fixed via `runtime.txt` and an explicit Python version setting); and a secrets-handling gap, since `python-dotenv`'s `.env`-file-based approach doesn't exist on Streamlit Cloud, which instead uses its own `st.secrets` mechanism (fixed with a fallback: `os.getenv(...) or st.secrets.get(...)`). Each fix revealed the next problem only after being applied — a realistic experience of deployment debugging, where issues are often layered rather than singular.

## 7. API key scope, verified rather than assumed

A Hopsworks API key was initially provisioned with 12 broad scopes during early setup ("select everything to be safe"). A deliberate attempt to reduce this to just `featurestore` and `modelregistry` failed — `hopsworks.login()` requires `project` scope to resolve project context, and separately attempts to initialize model-serving configuration internally regardless of whether serving is used, failing with an unrelated `AttributeError` (a genuine bug in the SDK's own graceful-degradation logic) when `serving` scope is absent. The final scope set (8 of the original 12) was arrived at through actual testing — including uncovering a real SDK limitation — rather than guesswork, and was verified working in both local and CI environments before the original broad key was deleted.

## What I'd do differently next time

- **Regenerate and dry-run test `requirements.txt` immediately after every new major dependency**, not just when something breaks.
- **Separate deployment-target dependency sets from the start** (pipeline vs. dashboard), rather than retrofitting the split after a production incident.
- **Pin Python versions explicitly everywhere** (local `.venv`, GitHub Actions, deployment platform) from day one, rather than relying on each environment's default.
- **Test infrastructure assumptions (like API key scope) deliberately, with the old configuration kept as a fallback**, rather than making broad-to-narrow changes in a single irreversible step.

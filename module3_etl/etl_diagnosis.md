# Module 3 — ETL Error Diagnosis: `etl_error_log.txt` (Task B4.4)

**Analyst:** Lead Enterprise Data Management Consultant
**Log date:** 2025-03-11, nightly run `etl_20250311_020000` (02:00–02:52 EAT)
**Business impact:** `warehouse.fact_sales` unchanged for 4 consecutive days; management reporting is 2 days stale; monthly management consolidation (currently 11 days) cannot close.

---

## 1. Reasoning Trail — What the Log Actually Says

| # | Timestamp | Log Evidence | Interpretation |
|---|---|---|---|
| 1 | 02:00:12–13 | `InvalidTextRepresentation: invalid input syntax for type integer: "N/A"` at `COPY staging.stg_sales, LINE 12044` | The staging table declares `customer_id INTEGER`, but at least one source (an offline POS or the e-commerce export) writes the literal string `N/A` for unknown customers. The whole `COPY` batch aborts at row 12,044 — **PostgreSQL COPY is all-or-nothing, so 0 of 21,562 rows were staged.** |
| 2 | 02:00:13 | `Falling back: continuing with 'partial mode' (staging retains previous batch …)` | The job's "fallback" silently continues with **yesterday's staging data** — the pipeline reports progress while processing stale input. This masks failure #1 and guarantees wrong results downstream. |
| 3 | 02:00:15 | `412 fact rows reference SKU not found in dim_product (orphans)` | Products created in POS/e-commerce after the last `dim_product` refresh are not yet SCD2-versioned in the warehouse. The warning itself says the load "will fail if orphans > 0" — a known, unhandled condition. |
| 4 | 02:00:16 | `NULL customer_id in staging rows: 63 (walk-in / offline-capture rows)` | Offline capture during connectivity outages legitimately produces unknown customers. The pipeline inserts `NULL` into `fact_sales.customer_sk`, which is `NOT NULL`. |
| 5 | 02:52:41 | `ForeignKeyViolation / NOT NULL: fact_sales.customer_sk … ROWS REJECTED: 63 of 21,562` | Root-cause error #2: **no `customer_sk = 0` ("Unknown / Walk-in Customer") member exists in `dim_customer`**, and no `COALESCE(s.customer_sk, 0)` is applied. The load aborts, warehouse unchanged. |
| 6 | 02:52:42 | `DeadlockDetected … Process 18442 (nightly_etl) vs Process 18501 (sync_worker_3, offline POS sync replay, store ST17)` | Root-cause error #3: **offline store-sync replay collides with the nightly ETL.** Both transactions `UPDATE dim_store` for `store_sk=17` (Gulu), but in opposite order relative to other locks. Stores lose connectivity for hours daily, so their buffered transactions replay at night — exactly when the ETL runs. Lock ordering is not consistent and there is no application-level lock window. |
| 7 | 02:52:42 | `No rows loaded … stale D-1 data for the 4th consecutive day` + alert to an **unmonitored mailbox** (last opened 7 days earlier) | Organizational failure: the run fails, alerts go nowhere, and no human notices for days. |

## 2. Root Causes (ranked by contribution)

| Rank | Root Cause | Type | Evidence | Consequence |
|---|---|---|---|---|
| RC-1 | **No schema validation / type contract between source and staging.** Sources freely write `N/A`, empty strings, and free-text into typed columns; staging uses strict `COPY`. | Data-contract gap (technical) | Lines 02:00:13 (`"N/A"` → `integer`) | Entire batch aborts → 0 rows staged |
| RC-2 | **Missing surrogate-key handling for unknown customers.** No `dim_customer` row with `customer_sk = 0`, no `COALESCE`, and `NOT NULL` on the FK. Offline capture (a *designed* behavior for outages) therefore breaks the load. | Modelling/design gap | Lines 02:00:16 + 02:52:41 (63 rows) | Transaction aborts → warehouse unchanged |
| RC-3 | **Write collision between offline store-sync replay and nightly ETL** (deadlock on `dim_store`, inconsistent lock order, no scheduling window). | Concurrency/scheduling gap (connectivity-driven) | Lines 02:52:42 (Process 18442 vs 18501, ST17 Gulu) | Run terminates mid-load |
| RC-4 | **Silent "partial mode" fallback** that continues with the previous day's staging data instead of failing fast. | Orchestration anti-pattern | Line 02:00:13 | Failures masked; wrong data propagates |
| RC-5 | **Unhandled SKU orphans** — `dim_product` SCD2 refresh ordering is wrong (dimension must load *before* the fact). | Load-sequencing gap | Line 02:00:15 (412 rows) | Would abort at FK check |
| RC-6 | **Alerting to an unmonitored mailbox; no run-state dashboard.** | Process/monitoring gap | Line 02:52:42 (last open: 2025-03-04) | 4 days of invisible failure |

### Causal chain (why these recur at SRG specifically)

```
Store connectivity outages (hours daily)
        │
        ├──► offline POS buffers transactions ──► sync_worker replays them at
        │                                          night ──► collides with nightly ETL ──► RC-3 deadlock
        └──► cashiers capture walk-ins/offline rows ──► NULL/`N/A` customer ids ──► RC-2 FK abort

No data contract between 23 POS databases + e-comm + loyalty ──► RC-1 type mismatches
Job written as "best effort" (fallback instead of fail-fast)  ──► RC-4 masks RC-1
Dimension load ordered after fact load                        ──► RC-5 orphans
Alerts to unmonitored inbox, no one owns the run              ──► RC-6 nobody notices
```

## 3. Corrective Actions (fix now)

| ID | Action | Fixes | Effort |
|---|---|---|---|
| CA-1 | Replace strict `COPY` with **staged landing + per-row validation**: coerce types with `NULLIF(TRIM(x),'N/A')`, reject bad rows to `etl_quarantine` table with error reason, load the rest. | RC-1 | S |
| CA-2 | Insert `customer_sk = 0` ("Unknown / Walk-in Customer") and `product_sk = 0` members into dimensions; `COALESCE` unknown keys in the fact load; keep `NOT NULL` on the fact FK. | RC-2 | S |
| CA-3 | **Lock window / single writer:** ETL takes `pg_advisory_lock(hashtext('dim_store'))`; store-sync replay runs 23:00–01:45 only; ETL takes the same advisory lock before mutating shared dimensions; all `dim_store` updates ordered by `store_sk`. | RC-3 | M |
| CA-4 | Fail fast: remove silent fallback; quarantine + halt with non-zero exit; run state persisted to `etl_run_log` and surfaced on a dashboard. | RC-4 | S |
| CA-5 | Reorder load: **dimensions first (SCD2), then facts**; reprocess orphans from quarantine after `dim_product` refresh. | RC-5 | S |
| CA-6 | Alert to on-call rotation (SMS/WhatsApp for the 4-person team), plus daily 06:00 run-state check by the IT Operations Lead. | RC-6 | S |

## 4. Prevention (stop it recurring)

1. **Data contracts per source** — schema JSON published with each extract; the loader refuses files that fail the contract *before* touching the database (this is validation rule VR-004/VR-008 from Module 2 enforced at the pipeline boundary).
2. **Quarantine, never abort** — bad rows are never dropped silently and never block good rows; quarantine rate is a monitored metric (DQC-07, threshold > 0.5%).
3. **Idempotent, replayable runs** — every run is keyed by `run_id` + natural business keys, so a failed day is replayed without duplicates (implemented in `srg_etl_pipeline.py`).
4. **Design for the outage reality** — unknown-customer path (`customer_sk = 0`) is a first-class state, not an error, because offline capture is expected behavior at SRG.
5. **Single-writer discipline** — advisory locks + a sync-vs-ETL schedule window remove the deadlock class entirely, not just this instance.
6. **Alerting that a human reads** — 4-person team, so alerts go to the on-call rotation, and the run dashboard is part of the 06:00 morning routine.

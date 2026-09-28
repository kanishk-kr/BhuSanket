# BhuSanket: Technical Project Report

A Land Acquisition Intelligence Platform for Early Detection of Delays Problem Statement 26017 | Ministry of Rural Development, Department of Land Resources (DoLR) | Theme: Smart Automation | Category: Software  
*Companion document: BhuSanket Technical Appendix (legal templates, data dictionary, event schema, formulas, SRS with acceptance criteria, deployment and failure architecture, synthetic-twin specification, edge cases).*  
---

## 1\. Executive Summary

Problem. Land acquisition is the most frequently cited cause of stalled infrastructure. It is monitored reactively: a review meeting discovers a slip after months are already lost. Delay arises from many interacting sources: statutory approvals, litigation, compensation flow, land-record quality, rehabilitation and resettlement (R\&R), field access, and inter-departmental coordination. No mechanism combines these signals to warn officers *before* a stage misses its date, or before a statutory deadline runs out.  
Solution. BhuSanket is an intelligence layer that sits on top of existing land, payment, court and project systems. It builds a continuously updated Land Acquisition Intelligence Graph (entities, events, dependencies, evidence) and answers five questions for every project:

| \# | Question | Output |
| :---- | :---- | :---- |
| 1 | Will it be delayed? | Stage-level delay probability |
| 2 | When? | Completion-date distribution (P50/P80/P90) |
| 3 | Why? | Drivers backed by traceable evidence |
| 4 | What should we do? | Ranked administrative interventions, owners, deadlines |
| 5 | What will it affect? | Possession, workfront readiness, construction, financial exposure |

Innovations.

1. Statutory Deadline Engine. Hard legal clocks in the Right to Fair Compensation and Transparency in Land Acquisition, Rehabilitation and Resettlement Act, 2013 (for example, the 12-month windows for declaration and for award) become predictive features and alerts: "34 days left; probability of finishing in time is 41%."  
2. Critical parcels and workfront readiness. "94.8% land acquired" can hide that only 71% of the land that *enables construction* is available. We measure the second number.  
3. ULPIN-first parcel identity aligned with DoLR's Bhu-Aadhaar and the federated Land Stack in DILRMP 3.0.  
4. Evidence-graded explanations. Every explanation opens to the underlying records with a strength grade.  
5. Modelled intervention scenarios with honest causal limits.  
6. Data confidence, contradiction detection and silence detection, so poor data lowers stated confidence instead of silently corrupting predictions.  
7. A land-acquisition digital twin (causal simulator) that makes the system testable before real data is available.

Architecture. Existing systems → adapters and parcel-identity resolution → Intelligence Graph → prediction (one discrete-time hazard model plus Monte-Carlo path simulation) → evidence, scenarios and critical-path impact → intervention queue, alerts and governance.  
MVP. One legal regime template plus one alternate, one linear highway project, 1,000-3,000 synthetic projects, an end-to-end loop: Detect → Explain → Locate → Prioritise → Simulate → Assign → Observe.  
Expected impact. Earlier identification of at-risk stages and deadlines, targeted interventions, fewer avoidable lapses and delays. MoSPI monitoring illustrates the stakes: in February 2024, 764 of 1,902 monitored central projects were delayed, with an average time overrun of about 36 months \[R6\].  
---

## 2\. Problem and Evidence

### 2.1 Scale

* MoSPI (projects of ₹150 crore and above, February 2024): 443 of 1,902 projects reported cost overruns totalling about ₹4.92 lakh crore (18.19% of original cost); 764 were delayed, with an average time overrun of about 36.27 months. Delay buckets: 188 projects at 1-12 months, 185 at 13-24, 275 at 25-60, 116 above 60\. Agencies cite delays in land acquisition, forest and environment clearances, and infrastructure linkages \[R6\].  
* Illustrations: highway projects stalled without financial closure because land was unavailable \[R10\]; landowners on a greenfield corridor resisting handover over compensation pending for about three years \[R11\].

### 2.2 Why delays happen (root-cause taxonomy)

| Category | Typical causes | Observable signal |
| :---- | :---- | :---- |
| Statutory/administrative | Slow appraisal, notification gaps, extensions, vacancies | Stage timestamps, clock status, extension count |
| Legal | Writ petitions, stays, title disputes, references to the Authority | Court data, revenue-court cases |
| Financial | Deposits by the requiring body, sanction and disbursal lag, payment failures | Payment records, cross-checks |
| Documentation | Mutation backlog, joint holdings, deceased owners, boundary mismatch | Land-record completeness, ULPIN linkage |
| Social/R\&R | Objections, valuation disputes, resettlement-site readiness | Grievances, R\&R milestones |
| Technical | Alignment changes, survey and measurement delays | Alignment revisions, survey status |
| Coordination | Forest/environment clearance, utilities, NOCs | Approval-tracker status |
| External | Monsoon, harvest, election periods | Calendar |

### 2.3 The gap

Operational systems (state land records, Bhoomi Rashi for national highways, PFMS, PARIVESH, court systems, PM Gati Shakti) record status and support planning. What is missing is a cross-system, forward-looking, explainable, actionable view. BhuSanket is designed as an overlay that consumes those systems.  
The timing is favourable. On 10 September 2026 DoLR launched DILRMP 3.0 (2026-31, ₹565.50 crore): states will build "land stacks" integrating georeferenced cadastral maps, records of rights, registrations and relevant court matters through APIs, forming a federated national stack with data ownership retained by the authorities concerned, and a 14-digit Bhu-Aadhaar (ULPIN) for every parcel \[R2\]\[R3\]. BhuSanket is designed as the predictive intelligence layer above this infrastructure.  
---

## 3\. Scope: Assumptions, Non-Goals and Design Principles

### 3.1 Assumptions

1. Historical projects carry reliable milestone timestamps and original baseline dates.  
2. The applicable legal regime (and state amendments) can be identified per project.  
3. Projects link to parcels (ULPIN or fallback identifiers).  
4. Workfront geometry and need-by dates come from the requiring body.  
5. Compensation and payment events carry timestamps.  
6. Data-sharing agreements permit the fields used.  
7. Statutory rules are maintained as versioned, legally reviewed templates.  
8. Officers can be assigned to intervention owner roles.

### 3.2 Non-goals

BhuSanket does not: replace land records, Bhoomi Rashi, PFMS or any transaction system; decide compensation or valuation; decide whether land should be acquired or which alignment is chosen; make legal decisions; take automatic action against any citizen; replace administrators; guarantee project completion; or claim causal effects of interventions without intervention evidence.

### 3.3 Design principles

1. Overlay, not replacement. Consume and add value.  
2. Stage-level, evidence-backed. Predict what blocks the next transition and show why.  
3. Risk, confidence and data quality are separate quantities.  
4. Law as configurable data. Legal rules are versioned templates, never hard-coded logic.  
5. No silent invention. When data is missing the system says so.  
6. Decision support only. Humans decide; overrides are recorded.  
7. Reproducibility. Any past prediction can be re-created.

---

## 4\. Solution Overview

### 4.1 The Land Acquisition Intelligence Graph

Entities → Events → Dependencies → Evidence → Predictions → Actions

* Entities: project, package/segment, parcel (ULPIN), owner (pseudonymised), stage, case, payment, R\&R plan, approval, officer role.  
* Events: append-only facts with effective time, observed time, source and confidence.  
* Dependencies: stage-to-stage, parcel-to-workfront, clearance-to-possession.  
* Evidence: records and documents supporting each explanation.  
* Predictions and actions: versioned outputs and tracked interventions.

### 4.2 Processing layers

Existing systems (state land stacks / ULPIN, Bhoomi Rashi, PFMS, court data, approvals, requiring bodies)  
      ↓ adapters, validation, parcel-identity resolution  
Intelligence Graph (bitemporal)  
      ↓  
Data confidence | Feature snapshots | Event engine  
      ↓  
Prediction: discrete-time hazard model \+ Monte-Carlo paths \+ statutory deadline risk  
      ↓  
WHY (evidence)   WHAT-IF (scenarios)   IMPACT (critical path, exposure)  
      ↓  
Intervention queue, alerts, governance  
      ↓  
Human action → outcome logging → controlled retraining

### 4.3 Three levels of delay (never conflated)

| Level | Meaning |
| :---- | :---- |
| L1 Process delay | A stage misses its baseline or statutory clock |
| L2 Land-availability delay | Land is not usable when a workfront needs it |
| L3 Infrastructure delay attributable to land | Construction slips *because of* L1/L2 |

Non-land causes (contractor, funding, non-land clearances, pauses) are separate cause codes so land acquisition is not blamed for everything.  
---

## 5\. Legal Process Model and the Statutory Deadline Engine

### 5.1 Process templates

Each acquisition regime is a versioned LegalProcessTemplate: stages, allowed transitions, dependencies, statutory clocks, required documents and owner roles. Adding a regime or a state amendment means authoring data, not code. The verified template in this report is the 2013 Act; state amendments (for example Gujarat Act 12 of 2016, which lets the State exempt listed projects from Chapters II and III) show why templates are versioned per jurisdiction. A second template covers sectoral acquisition (for example under the National Highways Act, 1956), authored with legal review.

### 5.2 Statutory Deadline Engine

The engine is generic. A StatutoryClock record holds: jurisdiction, legal regime, section reference, trigger event, duration, pause rules, extension rule, expiry consequence, and effective dates. The engine computes days remaining, the probability that the governed stage completes before expiry, and an alert state. The consequence differs by clock and is defined only in the template.  
Clocks configured from the 2013 Act text (details in Appendix A):

| Section | Governed step | Window | Consequence if not met | Extension |
| :---- | :---- | :---- | :---- | :---- |
| 14 | Preliminary notification after appraisal of the SIA report | 12 months from appraisal | SIA report deemed lapsed; fresh SIA needed | Government may extend; reasons recorded and notified |
| 19(7) | Declaration after preliminary notification | 12 months from notification, excluding periods held up by court stay or injunction | Preliminary notification deemed rescinded | Government may extend; reasons recorded and notified |
| 25 | Collector's award after declaration | 12 months from declaration | Entire proceedings lapse | Government may extend; reasons recorded and notified |
| 38(1) | Possession after payment | Compensation within 3 months of award, monetary R\&R within 6 months; infrastructural R\&R entitlements within 18 months | Possession preconditions unmet | Per template |

Design consequences:

* Stay pauses must be computed from legal events, so the court-data feed directly affects clock arithmetic.  
* Extensions are events with reasons; their frequency is both a governance metric and a risk feature.  
* The alert language is "Statutory Deadline Risk," and states the consequence defined by the template. It never assumes a missed deadline automatically ends a project.

### 5.3 Rules the model must respect but not learn

Some legal conditions are constraints, not statistical patterns: for example, prior Gram Sabha consent requirements in Scheduled Areas (s.41), consent thresholds for private and PPP projects (s.2(2)), and possession only after payment (s.38). These are encoded as template rules and required-step checks. They select applicable safeguards and playbooks; they are not predictive features in the base risk model.  
---

## 6\. Data Integration, Identity and Data Confidence

### 6.1 Sources and access reality

| Source | Content | Realistic route | MVP |
| :---- | :---- | :---- | :---- |
| State land stacks (DILRMP 3.0) | Cadastral maps, RoR, registrations, relevant court matters | State APIs; states retain data control \[R2\]\[R3\] | Adapter with real schema, mock data |
| ULPIN / Bhu-Aadhaar | 14-digit parcel ID from parcel coordinates \[R4\] | Land stack / cadastral software | Format validation, mock |
| Bhoomi Rashi (MoRTH/NIC) | National highway acquisition and payment status \[R8\] | Inter-government arrangement | Mock feed |
| PFMS | Payments and fund flow | Controlled | Mock; used as cross-check |
| National Judicial Data Grid and revenue-court systems | Case status and orders; Open API described for Central and State Government users \[R5\] | Departmental credentials | Structured synthetic event stream |
| Approval trackers (PARIVESH etc.) | Clearance workflow | Agreements | Mock |
| Requiring bodies | Packages, chainage, need-by dates, contractor data | Agency files/APIs | CSV import |

Where a source is mock in the MVP, the demo says "mock feed with the real schema." Access to controlled systems is a pilot-phase activity requiring formal agreements.

### 6.2 Parcel identity resolution (ULPIN-first)

1 ULPIN exact match → 2 cadastral geometry overlap → 3 village \+ survey/khasra/sub-parcel  
→ 4 owner/relationship \+ document references → 5 fuzzy similarity → 6 human confirmation

Rules: never merge persons on name alone; never overwrite a high-confidence mapping automatically. New evidence that conflicts with an existing mapping goes to review. Mappings carry validity intervals because parcels split, merge and get renumbered.

### 6.3 Data confidence

Per project and per domain (project, compensation, legal, land records, R\&R): completeness, freshness, cross-source agreement, identity confidence. Displayed separately from risk, for example "Legal data 43%, last sync 12 days ago."

### 6.4 Contradictions and staleness

A contradiction is raised only when two sources disagree *after* accounting for timestamps, freshness and event ordering. If a source is simply stale, the system records a staleness mismatch instead. Contradictions have severity levels (low: minor amount mismatch; medium: date/status mismatch; high: "100% paid" versus 63% in the payment system; critical: parcel marked acquired while a stay is active). High and critical contradictions enter the intervention queue.

### 6.5 Bitemporal-lite history

Every fact stores when it was true (effective interval), when the system learned it (observed time) and its source. Nothing is overwritten. This underpins reproducibility, audit, dispute resolution, model debugging and honest historical evaluation.  
---

## 7\. Predictive Intelligence

### 7.1 Three targets

* Target A (stage delay): actual completion later than the *original* baseline plus tolerance.  
* Target B (time to completion): distribution of days until stage completion, with censoring for open stages.  
* Target C (critical-milestone failure): the stage completes after its critical milestone date, defined as the latest completion date that still keeps the dependent workfront feasible: CMD \= NeedBy(workfront) − downstream lead times − buffer. Target C \= 1 if completion time exceeds CMD.

### 7.2 One primary model family

Discrete-time hazard model. Time is bucketed (for example 7 days). For each open stage and bucket the model estimates h\_k(x) \= P(completes in bucket k | not yet completed, x) with time-varying features. A gradient-boosted classifier trained on person-period data implements it. From the survival curve we obtain P(complete within 7/30/60/90 days), P50/P80/P90 dates, Target A, and clock-relative probabilities. A plain classifier is kept only as a baseline for comparison.  
Path simulation. A Monte-Carlo engine samples stage durations along the dependency graph to produce project-level completion dates, the probability of meeting each critical milestone and each statutory clock, and inputs to the exposure model. The full multi-state and competing-risk formulation (complete, stay, re-baseline, cancel) is a Phase-2 extension; the MVP treats stay and re-baseline as events in the simulator.

### 7.3 Uncertainty

Intervals for delay days are produced with quantile or conformal methods and reported as empirical coverage on time-split validation under the method's assumptions (for example, about 90% observed coverage on later cohorts). With censored survival data standard conformal guarantees do not transfer directly, so observed coverage on held-out later cohorts is always reported.

### 7.4 Risk, model confidence and data confidence are separate

| Risk | Model confidence | Data confidence | Behaviour |
| :---- | :---- | :---- | :---- |
| 82% | High | High | Act |
| 82% | Low | Medium | "Manual review recommended" |
| 82% | High | Low | "Risk may be misstated due to stale legal data" |

### 7.5 Risk trajectory, momentum and baseline integrity

* Every prediction is stored. Risk velocity v \= (r\_t − r\_{t−k}) / k × 7 points per week; classes: stable, rising, accelerating (thresholds configurable).  
* A short forecast of the risk trajectory (for example 61 → 68 → 79 versus 61 → 57 → 53\) separates recovering projects from deteriorating ones.  
* Three date concepts are always stored: original commitment, approved baseline, forecast, plus any unapproved proposed revision. A baseline integrity score flags repeated re-baselining so replanning cannot hide delay.

### 7.6 Administrative silence

Silence (no updates in a template-specific interval) is evaluated only after a source-health check: if the feed is unhealthy, the result is a data issue, not project risk. If the source is healthy, it becomes a possible-stagnation signal with modest weight. This prevents a broken API from turning healthy projects red.

### 7.7 Features, leakage control and fairness

* Feature families: structural, process, statutory-clock, financial, legal, social/R\&R, spatial, temporal, data-quality, and contextual priors.  
* Leakage prevention: every feature is computed from data observed at or before prediction time T (feature snapshots). Final outcomes, future counts and later extensions are never available to earlier predictions (Appendix I).  
* Historical district or agency performance enters only as a shrunk (partial-pooling) contextual prior, displayed as its contribution in percentage points of predicted probability, never as a label.  
* Sensitive attributes (caste, religion) are excluded. Scheduled-Area status selects template safeguards and playbooks; it is not a feature in the base risk model.  
* Fairness reports compare error and score distributions across district groups.

---

## 8\. Critical Path, Critical Parcels, Workfront Readiness and Exposure

### 8.1 Dependency graph and critical path

Nodes: acquisition stages, parcel groups, clearances (forest/environment, utilities, railway NOCs), construction packages. Edges: typed dependencies. Critical-path risk, not only project risk, is computed. Criticality requires requiring-body inputs (package geometry, chainage, need-by dates); it cannot be derived from land data alone.

### 8.2 Critical parcels and construction-enabling possession

A parcel is critical for a workfront if its unavailability breaks workfront continuity or blocks a critical-path activity. The dashboard's hero metrics:

* Land acquired: 94.8% (unweighted)  
* Construction-enabling possession: 87.1% (criticality-weighted)  
* Critical parcels resolved: 76%

### 8.3 Workfront readiness

For workfront w with parcels P\_w:  
Readiness\_w \= Σ (a\_p · c\_p · u\_p) / Σ (a\_p · c\_p)  
where a\_p is required area or chainage length, c\_p ∈ \[0,1\] the criticality weight, and u\_p ∈ \[0,1\] usability (possession granted, encumbrance-free, access available). A short parcel that blocks an entire workfront has c\_p \= 1 and cannot be outweighed by a long non-critical parcel. Results are shown per chainage segment (for example 0-10 km: 97%, 20-30 km: 52%).

### 8.4 Estimated financial exposure (modular)

A Monte-Carlo model draws the delay from the predictive distribution and applies separate, non-overlapping cost curves: contractor idle cost, financing cost, escalation, overheads, and statutory interest where it applies. Under s.30(3) of the 2013 Act the Collector's award includes interest at 12% per annum on market value from the SIA notification date until award or possession, whichever is earlier; the exposure module uses this only within that window. Output is P50/P80/P90 estimated exposure, always labelled "estimated financial exposure." It becomes "avoided cost" only if validated against project accounts. Cost curves need not be constant in time.  
---

## 9\. Explainability and Evidence

### 9.1 Chain

SHAP contribution → feature interpretation → domain rule → evidence records → plain-language explanation Example: "High risk mainly because compensation processing has taken 211 days versus a comparable median of 74." *Show evidence* opens the 12 records used.

### 9.2 Evidence graph and evidence grade

Project → parcels → owners → disputes → cases → stay → approvals → grievances, traversable from a "Why?" click. Each explanation carries an evidence grade: HIGH when supported by official structured records (payment record, court order, land record, milestone); LOW when relying on stale records, grievance text or inferred spatial features.

### 9.3 Language model policy

The language model is a communication layer only. Input: validated facts and approved playbook actions. It may (1) summarise validated drivers, (2) translate, (3) explain approved actions. It cannot generate a new recommendation, alter a number, or influence a score. If it fails, deterministic template text is shown.

### 9.4 Event and document intelligence

Priority pipeline: ingest a court or administrative order → extract case, court, date, order type, stay yes/no, scope, next hearing → resolve to parcels → update dependency graph and clock pauses → re-score → alert. Every extracted event carries provenance (document ID, page and paragraph, extraction confidence, human verification status). Source authority is ranked: official structured records, official orders, verified grievances, court information, other public sources, and news only as a weak signal. The MVP demonstrates this with a synthetic structured event stream (a stay is detected, clocks pause, project re-scores, alert fires); document OCR and language extraction are Phase 2\.  
---

## 10\. Intervention Intelligence

### 10.1 Modelled scenarios

The system evaluates f(x) (predicted risk under current inputs) and f(x ⊕ Δ) (predicted risk after changing actionable inputs, such as disbursal timing, extra survey teams, revenue camps, legal escalation or R\&R meetings). These are model scenarios, not causal claims. On screen: "Scenario: compensation lag reduced by 30 days. Predicted risk 78% → 51% (model-estimated). This is a simulation, not a guarantee."

### 10.2 Path to real causal estimates

Every intervention is logged with what, when, who, *why chosen*, eligibility and outcome. A stepped-wedge or matched-district pilot enables effect estimation later. Interventions are recorded as treatments so that a fixed high-risk project does not teach the model that "high risk is fine".

### 10.3 Priority Index and the intervention queue

Priority \= 100 × (w\_R·Risk \+ w\_U·Urgency \+ w\_I·Impact \+ w\_A·Actionability) with each component normalised to \[0,1\] and configurable weights (default 0.35, 0.25, 0.25, 0.15).

* Urgency \= 1 − min(1, days to nearest statutory or critical deadline / 90).  
* Impact \= normalised critical-path position and P90 exposure.  
* Actionability \= share of top drivers mapped to allow-listed actions with an available owner.  
* Rapidly deteriorating projects receive an escalation boost (a design choice to be validated on alert precision in the pilot).  
* If Actionability is below a threshold the item is labelled Monitor, not Act.

The Collector's home screen is today's intervention queue: item, risk, confidence, clock, blocking parcels, action, owner, due date, modelled impact.

### 10.4 Acquisition Complexity Assessment (advisory, pre-notification)

Before notification, planners can compare candidate alignments on fragmentation, tehsil-level litigation exposure, forest/water overlap, settlement share, holding sizes, R\&R load and historical duration of similar corridors. Output: an estimated acquisition-duration range, key complexity factors and data confidence, not a score of the land or community. The system never selects the alignment. Marked lower confidence because analogues are few.  
---

## 11\. Dashboards, GIS and Roles

### 11.1 Five screens

1. Command Center, framed as "What needs attention today?": statutory-clock threats, critical parcels blocking workfronts, rapidly deteriorating projects, data contradictions, recommended interventions.  
2. Project Intelligence: baseline versus forecast timeline (P50/P90), risk, confidence, momentum, drivers with evidence, dependency view, recommendations.  
3. GIS: layered map.  
4. Intervention Management: actions, owners, deadlines, outcomes.  
5. Governance: data confidence, model performance, drift, fairness, audit.

### 11.2 GIS layers

Project risk; parcel status; blocking parcels only; spatial constraints (forest, water, settlements, crossings); R\&R and grievance density; legal hotspots; 90-day projected view; workfront readiness by chainage; and "Explain this area" (for a segment: parcels, fragmentation, pending mutations, disputes, R\&R households, overlap, contribution of historical context).

### 11.3 Roles

Ministry/policy, State nodal officer, District Collector, Project manager (requiring body), Field officer, Legal officer, R\&R officer, Data steward, Model governor/auditor. Access is by role and jurisdiction.  
---

## 12\. Governance, Security and Privacy

System invariants. BhuSanket cannot deny compensation or R\&R entitlements, alter valuation, initiate legal action, label citizens, recommend coercive measures, or serve as evidence of wrongdoing by an individual landowner. Recommendations are drawn from an allow-list of administrative actions, enforced in code and tested.  
Citizen-impact guardrail. Two layers: administrative intelligence (detailed, access-controlled) and a public transparency view limited to project status, acquisition progress, expected milestone range, compensation-process information, grievance channels and generic process explanation. Individual risk, owner information, parcel-level sensitive data and predicted behaviour are never public.  
Data classification.

| Data | Class | Access |
| :---- | :---- | :---- |
| Project ID/name | Internal | Broad |
| Parcel geometry | Sensitive | Jurisdiction |
| Owner identity | Highly sensitive | Authorised revenue officials |
| Compensation details | Highly sensitive | Authorised officers |
| Court case details | Sensitive | Legal/relevant officers |
| Risk scores | Internal | Authorised roles |
| Aggregated trends | Controlled | Broader |
| Model performance | Governance | Auditors/admins |

Event-sourced audit. Each prediction stores model version, data and feature snapshots, output, interval, drivers, viewers, actions, overrides with reasons and later outcome, hash-chained. An auditor can reproduce "why was Project X high-risk on 17 July".  
Controlled continuous learning. New data → validation → drift detection → candidate model → offline, fairness and calibration evaluation → domain review → approval → deployment. Automatic promotion to production is prohibited.  
Privacy and compliance. Pseudonymised identifiers in models; alignment with the Digital Personal Data Protection Act, 2023 (purpose limitation, minimisation); consent-based, purpose-limited data access consistent with the state-retained data control in DILRMP 3.0; India data residency; VAPT before go-live.  
Graceful degradation. The system never silently invents information. If payment data is unavailable it shows "Payment data unavailable, last confirmed 17 Sep" instead of estimating (Appendix G).  
---

## 13\. Architecture and Implementation Plan

### 13.1 MVP scope (hard cap)

1. Land-acquisition digital twin: 1,000-3,000 synthetic projects with causal structure.  
2. One legal regime template (2013 Act) plus one alternate; one linear highway example.  
3. Canonical database: PostgreSQL with PostGIS, append-only event tables.  
4. One primary model (discrete-time hazard, gradient boosting) and Monte-Carlo path simulation.  
5. Statutory Deadline Engine.  
6. Evidence-backed explanations (one evidence graph).  
7. Critical parcels and workfront readiness for the highway example.  
8. Five screens including the GIS.  
9. Scenario simulator (allow-listed actions).  
10. Alerts (mock delivery), role-based access, audit table.  
11. Risk momentum and data-confidence display; silence detection as a backend signal.

### 13.2 Stack (MVP)

React with TypeScript; FastAPI; PostgreSQL/PostGIS; Python (LightGBM, scikit-survival or custom hazard code, SHAP); Celery with Redis; S3-compatible object storage; MapLibre; Prometheus and Grafana; Keycloak or JWT for authentication. REST with OpenAPI, GeoJSON and webhooks. Scale-out options (streaming ingestion, orchestration, feature store, model registry, analytical store, Kubernetes, federated learning, multi-state and deep survival models, retrieval indexes) are documented as future options, not MVP components.

### 13.3 Team and 15-day workstreams (assumes five people)

| Person | Days 1-5 | Days 6-10 | Days 11-15 |
| :---- | :---- | :---- | :---- |
| Data/Simulation | Templates, twin generator, schema | Realism checks, sample events | Parameter-recovery test |
| ML | Features, hazard model | Monte Carlo, deadline engine, calibration | Scenarios, validation report |
| Backend | DB, ingestion, APIs | Evidence, alerts, RBAC, audit | Hardening, API docs |
| Frontend/GIS | Command Center skeleton, map | Project Intelligence, GIS layers | Queue, Governance, polish |
| Product/Demo | Story, roles, playbook | Acceptance tests, traceability | Demo script, video, submission |

### 13.4 Roadmap

Phase 0 (1-2 months): legal-template review, data-sharing agreements, baselines. Phase 1 (3-4 months): shadow-mode pilot in 2-3 districts through state land-stack APIs. Phase 2 (6 months): more states, document intelligence, offline field app, multi-state models. Phase 3 (12 months): national federation aligned with the federated Land Stack.  
---

## 14\. Validation and Impact Metrics

### 14.1 What each validation layer proves

| Layer | Proves | Does not prove |
| :---- | :---- | :---- |
| Synthetic benchmark | The pipeline works; the model recovers relationships planted in the simulator (for example, that compensation delay increases possession delay); recommender estimates can be compared with known simulated effects | Real-world accuracy, or that an intervention works in India |
| Public-aggregate sanity checks | Synthetic delay distributions resemble published aggregates | Project-level predictive power |
| Real retrospective validation | Predictive performance on historical cohorts | Causal effect of interventions |
| Shadow-mode pilot | Operational usefulness and alert burden | Causal effect |
| Stepped-wedge/matched pilot | Estimated intervention effects | Generalisation |

No accuracy figure from synthetic data is presented as real performance.

### 14.2 Five headline metrics

1. Early-warning lead time: median days between first qualifying alert and the eventual delay or breach.  
2. Critical-milestone recall: share of missed critical milestones flagged in advance.  
3. Critical-parcel recall: share of parcels that actually blocked a workfront identified in advance.  
4. Actionable alert rate: alerts leading to a verified intervention divided by total alerts (with false-escalation rate).  
5. Clock-breach detection rate: share of eventual statutory-clock breaches flagged at least X days before expiry.

Supporting metrics: PR-AUC and ROC-AUC, Brier score, calibration error, C-index, MAE of delay days, interval coverage, alerts per officer per week, fairness gaps. Splits are time-based.  
---

## 15\. Demonstration Storyline

1. "Project X appears healthy." 94.8% of land acquired.  
2. But it is not construction-ready: only 71% construction-enabling possession; 10 unresolved parcels block the critical workfront.  
3. Risk 82%, confidence high, momentum \+18 points in 14 days, statutory clock 34 days, P90 possession forecast 24 Feb.  
4. Why? Evidence graph: ownership ambiguity, pending compensation, two grievances, one case with a stay; each opens to records with an evidence grade.  
5. What can we do? Intervention queue: verification camp, legal review, compensation batch, with owners and due dates.  
6. What if? Scenario: critical parcels resolved in 21 days moves P90 from 24 Feb to 31 Jan (model-estimated).  
7. Assign, then observe: risk falls over the next fortnight (simulated); the audit view reconstructs every step.

The demo executes the full loop: Detect → Explain → Locate → Prioritise → Simulate → Assign → Observe.  
---

## 16\. References

Tier 1: Government and legal

* \[R1\] The Right to Fair Compensation and Transparency in Land Acquisition, Rehabilitation and Resettlement Act, 2013 (Act 30 of 2013), India Code: [https://www.indiacode.nic.in/bitstream/123456789/19895/1/the\_right\_to\_fair\_compensation\_and\_transparency\_in\_land\_acquisition,\_rehabilitation\_and\_resettlement\_act,\_2013..pdf](https://www.indiacode.nic.in/bitstream/123456789/19895/1/the_right_to_fair_compensation_and_transparency_in_land_acquisition,_rehabilitation_and_resettlement_act,_2013..pdf)  
* \[R2\] Department of Land Resources, DILRMP 3.0 Operational Guidelines launch, 10 September 2026 (reported by DD India): [https://ddindia.co.in/2026/09/shivraj-singh-chouhan-launches-dilrmp-3-0-with-rs-565-50-crore-outlay-to-build-integrated-gis-based-land-stack/](https://ddindia.co.in/2026/09/shivraj-singh-chouhan-launches-dilrmp-3-0-with-rs-565-50-crore-outlay-to-build-integrated-gis-based-land-stack/)  
* \[R3\] DoLR DILRMP programme page: [https://dolr.gov.in/en/programmes-schemes/dilrmp-2/](https://dolr.gov.in/en/programmes-schemes/dilrmp-2/)  
* \[R4\] DoLR, Bhu-Aadhaar (ULPIN): [https://dolr.gov.in/en/ulpin/](https://dolr.gov.in/en/ulpin/)  
* \[R5\] Department of Justice / eCommittee, National Judicial Data Grid: [https://ecommitteesci.gov.in/service/national-judicial-data-grid/](https://ecommitteesci.gov.in/service/national-judicial-data-grid/) ; National Informatics Centre project page: [https://www.nic.gov.in/project/national-judicial-data-grid/](https://www.nic.gov.in/project/national-judicial-data-grid/)  
* \[R6\] MoSPI, Status of projects (Flash Report, Feb 2024): [https://www.uatipm.mospi.gov.in/Content/ArchiveReport/flash/2023-24/FR\_feb\_2024.pdf](https://www.uatipm.mospi.gov.in/Content/ArchiveReport/flash/2023-24/FR_feb_2024.pdf) ; corroborated by press coverage: [https://www.pressreader.com/india/hindustan-times-ranchi/20240401/281805698939992](https://www.pressreader.com/india/hindustan-times-ranchi/20240401/281805698939992)  
* \[R7\] Digital Personal Data Protection Act, 2023 (MeitY).  
* \[R8\] Bhoomi Rashi portal (MoRTH; developed by NIC): [https://bhoomirashi.gov.in](https://bhoomirashi.gov.in/)

Tier 2: Authoritative academic (methods) Discrete-time survival and competing risks (Tutz & Schmid; Fine & Gray); gradient boosting (Ke et al., LightGBM); SHAP (Lundberg & Lee, 2017); conformal prediction (Vovk et al.; Angelopoulos & Bates); counterfactual explanations (Wachter et al.; Mothilal et al.); causal inference for policy (Imbens & Rubin); fairness (Barocas, Hardt & Narayanan); hotspot statistics (Getis & Ord).  
Tier 3: Industry and secondary reports

* \[R9\] Public-sector platform context: PM Gati Shakti National Master Plan, NeGD case study: [https://negd.gov.in/wp-content/uploads/2025/11/Ready-to-publish-PM-Gati-Shakti-NMP-Case-Study-Final-Draft-01-10-2025-1.pdf](https://negd.gov.in/wp-content/uploads/2025/11/Ready-to-publish-PM-Gati-Shakti-NMP-Case-Study-Final-Draft-01-10-2025-1.pdf)

Tier 4: News examples (illustrative only)

* \[R10\] Business Standard, land acquisition delays financial closure for 23 projects: [https://www.pressreader.com/india/business-standard/20170509/281496456197346](https://www.pressreader.com/india/business-standard/20170509/281496456197346)  
* \[R11\] The Tribune, compensation delay and landowner opposition on the Chandigarh-Ambala corridor: [https://www.tribuneindia.com/news/patiala/angered-over-delay-in-compensation-land-owners-oppose-road-project-in-mohali](https://www.tribuneindia.com/news/patiala/angered-over-delay-in-compensation-land-owners-oppose-road-project-in-mohali)

# BhuSanket: Technical Appendix

Companion to the BhuSanket Technical Project Report (Problem Statement 26017, DoLR, Ministry of Rural Development).  
Contents: A Legal templates and statutory clocks | B Data dictionary | C Event schema | D Formulas and definitions | E SRS with acceptance criteria | F Traceability | G Deployment and failure architecture | H Digital-twin specification | I Feature-leakage framework | J Edge cases | K Risks | L Diagram list  
---

## A. Legal Templates and Statutory Clocks

### A.1 StatutoryClock record

StatutoryClock  
 ├── clock\_id, template\_id, jurisdiction, legal\_regime  
 ├── section\_reference, description  
 ├── trigger\_event, end\_event  
 ├── duration (value, unit)  
 ├── pause\_rules        (e.g. court stay/injunction periods)  
 ├── extension\_rule     (authority, reasons required, notification required)  
 ├── expiry\_consequence (LAPSE | RESCISSION | REVIEW | ADDITIONAL\_APPROVAL | RE-INITIATION | NONE)  
 ├── effective\_from, effective\_to  
 └── legal\_review\_status, reviewed\_by, reviewed\_on

The engine reads clocks as data. Changing a rule means editing a template version, with legal review recorded.

### A.2 Clocks configured from the 2013 Act (RFCTLARR template v1)

Source: text of the Right to Fair Compensation and Transparency in Land Acquisition, Rehabilitation and Resettlement Act, 2013 (Act 30 of 2013). State amendments, central and state rules, and notifications may alter or supplement these; each state template records its own version.

| Clock | Section | Trigger → End | Duration | Pause rule | Extension | Consequence |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| SIA completion | 4(2) proviso | SIA commencement → SIA completion | 6 months (government "shall ensure") | None stated | n/a | REVIEW (no automatic consequence stated) |
| Expert Group recommendation | 7(4),(5) | Constitution of Expert Group → recommendation | 2 months | None stated | n/a | REVIEW |
| SIA report validity | 14 | Appraisal of SIA report → preliminary notification (s.11) | 12 months | None stated | Government may extend; decision recorded in writing, notified, uploaded | LAPSE of SIA report; fresh SIA required |
| Land-record updating | 11(5) | Preliminary notification → completion of updating, before declaration | 2 months | None stated | n/a | REVIEW |
| Objections window (citizen side) | 15(1) | Publication of preliminary notification → last date to object | 60 days | n/a | n/a | Window closes |
| Declaration | 19(7) | Preliminary notification → declaration (s.19) | 12 months | Periods held up by court stay or injunction are excluded | Government may extend; recorded, notified, uploaded | Preliminary notification deemed rescinded |
| Requiring-body deposit | 19(2) proviso | Precondition to declaration | Deposit required so declaration can issue within the 12 months | n/a | n/a | Declaration cannot be made without prescribed deposit |
| Notice to persons interested | 21(2) | Publication of notice → appearance date | Not less than 30 days, not more than 6 months | n/a | n/a | Procedural bound |
| Award | 25 | Declaration published → Collector's award | 12 months | None stated in section text | Government may extend; recorded, notified, uploaded | Entire acquisition proceedings lapse |
| Payment before possession | 38(1) | Award → full payment/tender | 3 months (compensation); 6 months (monetary R\&R); 18 months (infrastructural R\&R entitlements) | n/a | n/a | Possession preconditions unmet |
| Reference to Authority | 64(1),(2) | Application for reference → reference by Collector; application deadlines | Collector refers within 30 days; applicant applies within 6 weeks of award (if present) or as specified | n/a | Collector may entertain late application within a further 1 year for sufficient cause | Procedural |
| Authority disposal | 60(4) | Receipt of reference → award of Authority | 6 months | n/a | n/a | Procedural target |
| Legacy proceedings | 24(2) | 1894-Act award made 5+ years before commencement without possession or payment | 5 years | n/a | n/a | Deemed lapsed (legacy cases) |

Interest exposure (verified in the text): s.30(3): interest at 12% per annum on market value from the date of publication of the SIA notification under s.4(2) until the award or taking of possession, whichever is earlier. s.69(2) (Authority): 12% per annum from the date of the s.11 notification to the award or possession, with court-stay periods excluded. s.72: interest of 9% per annum on excess compensation from possession, and 15% per annum after one year, when directed by the Authority.  
Other conditions encoded as template rules (constraints, not predictive features):

* s.2(2): prior consent of at least 80% of affected families for private companies, and 70% for public-private partnership projects.  
* s.41(1)-(3): as far as possible no acquisition in Scheduled Areas; if unavoidable, as a demonstrable last resort, with prior consent of the Gram Sabha or equivalent body before notification.  
* s.41(6): for land acquired from SC/ST owners, at least one-third of compensation as first instalment.  
* s.40: urgency provisions (possession after 30 days from s.21 notice; 80% tender; additional compensation), used only in restricted circumstances; s.9 allows SIA exemption under urgency.  
* s.10: food-security limits, with linear projects excluded from the aggregate cap in s.10(4).  
* s.63: civil courts barred in matters where the Collector or Authority is empowered; the High Courts (Articles 226/227) and the Supreme Court remain available. Court-derived signals therefore come mainly from writ jurisdiction and the Authority.

State variation example: Gujarat Act 12 of 2016 inserts s.10A (State power to exempt listed project categories from Chapters II and III), s.23A, s.31A and other amendments. Templates are therefore keyed by jurisdiction and version.  
Legal review status. The clocks above were configured from a consolidated text of the Act. The template must carry a legal\_review\_status and be checked against the official India Code text and current state rules before operational use. The National Highways Act, 1956 template is authored separately with legal review; its section-level clocks are not asserted here.

### A.3 Clock arithmetic

For clock c with start s\_c, duration L\_c and pause intervals Π\_c (from legal events): deadline\_c \= s\_c \+ L\_c \+ Σ |π| for π ∈ Π\_c that the pause rule excludes days\_remaining\_c \= deadline\_c − now DeadlineRisk\_c \= P( stage completion time \> deadline\_c | x ), taken from the stage survival curve. Alert states: GREEN (DeadlineRisk \< 0.2), AMBER (0.2-0.5), RED (0.5-0.8), CRITICAL (\> 0.8 or days\_remaining below template minimum). Thresholds are configurable.  
---

## B. Data Dictionary (core entities)

| Entity | Key fields (type) |
| :---- | :---- |
| Project | project\_id (PK), name, requiring\_body\_id, regime\_id, template\_id, jurisdiction, sector, budget, geometry (LineString/Polygon), status |
| Package | package\_id, project\_id, chainage\_start, chainage\_end, geometry, need\_by\_date |
| Parcel | parcel\_id, ulpin (14-char, nullable), survey\_no, khasra\_no, village\_code, area, geometry, land\_use, scheduled\_area\_flag, valid\_from, valid\_to |
| ParcelIdentityMap | map\_id, parcel\_id, external\_id\_type, external\_id, match\_confidence, evidence\_json, reviewer\_decision, valid\_from, valid\_to |
| Owner (pseudonymised) | owner\_pid, owner\_type, share, relationship\_flags, deceased\_flag |
| Stage | stage\_id, project\_id/package\_id, template\_stage\_id, original\_commitment\_date, approved\_baseline\_date, proposed\_revision\_date, planned\_start, actual\_start, actual\_end, status |
| StatutoryClock instance | instance\_id, stage\_id, clock\_id, start\_event\_id, pause\_intervals\_json, deadline, extension\_count, state |
| Milestone | milestone\_id, project\_id, description, critical\_milestone\_date, depends\_on |
| Dependency | dep\_id, from\_node, to\_node, type, lag\_days |
| Compensation | comp\_id, parcel\_id, owner\_pid, assessed\_amt, sanctioned\_amt, disbursed\_amt, sanction\_date, payment\_status, deposited\_in\_court\_flag |
| LegalCase | case\_id, court, case\_no, parcel\_ids\[\], stay\_flag, stay\_start, stay\_end, next\_hearing, order\_ref |
| RRPlan / RRMilestone | rr\_id, project\_id, families, milestone, due, done, site\_readiness |
| Grievance | grievance\_id, category, text\_ref, received\_on, status, verified\_flag |
| Approval/NOC | approval\_id, type, authority, status, submitted\_on, decided\_on |
| Intervention | intervention\_id, project\_id, action\_code, owner\_role, chosen\_reason, eligibility\_criteria, start, end, outcome |
| Event | see Appendix C |
| DataSource / DataSnapshot | source\_id, health\_status, last\_sync; snapshot\_id, source\_id, as\_of |
| DataQualityIssue / Contradiction | issue\_id, entity\_id, type, severity, sources\[\], status |
| FeatureSnapshot | snapshot\_id, entity\_id, prediction\_time T, features\_json, data\_snapshot\_ids\[\] |
| ModelVersion | model\_id, type, training\_window, metrics\_json, approved\_by, approved\_on |
| PredictionSnapshot | prediction\_id, entity\_id, T, model\_id, feature\_snapshot\_id, outputs\_json (probabilities, quantiles), confidence, drivers\_json, evidence\_ids\[\] |
| Alert / QueueItem | alert\_id, prediction\_id, priority\_index, state, owner\_role, due, ack\_by, snooze\_reason |
| AuditLog | audit\_id, actor, action, entity, timestamp, prev\_hash, hash |

All fact tables carry effective\_from, effective\_to, observed\_at, source\_id.  
---

## C. Event Schema

Event {  
  event\_id, entity\_id, entity\_type, event\_type,  
  effective\_at, observed\_at, source\_id,  
  payload (JSON), confidence (0-1), verification\_status, supersedes\_event\_id  
}

Event types (initial catalogue): SIA\_COMMENCED, SIA\_COMPLETED, EXPERT\_GROUP\_APPRAISAL\_DONE, PRELIM\_NOTIFICATION\_PUBLISHED, OBJECTION\_FILED, RR\_SCHEME\_APPROVED, DECLARATION\_PUBLISHED, SURVEY\_COMPLETED, MEASUREMENT\_OBJECTION, AWARD\_MADE, COMPENSATION\_SANCTIONED, COMPENSATION\_DISBURSED, PAYMENT\_FAILED, COMPENSATION\_DEPOSITED\_IN\_COURT, COURT\_CASE\_REGISTERED, COURT\_STAY\_GRANTED, COURT\_STAY\_VACATED, REFERENCE\_TO\_AUTHORITY, MUTATION\_COMPLETED, TITLE\_DISPUTE\_RAISED, POSSESSION\_GRANTED, RR\_MILESTONE\_COMPLETED, NOC\_GRANTED, NOC\_PENDING, BASELINE\_CHANGED, EXTENSION\_GRANTED, ALIGNMENT\_CHANGED, SCOPE\_REDUCED, PROJECT\_PAUSED, PROJECT\_CANCELLED, GRIEVANCE\_RECEIVED, SOURCE\_UNHEALTHY, CONTRADICTION\_RAISED, INTERVENTION\_STARTED, INTERVENTION\_COMPLETED.  
Events are append-only; corrections are new events that supersede earlier ones.  
---

## D. Formulas and Definitions

D1. Critical milestone date and Target C CMD\_m \= NeedBy(workfront\_w) − Σ downstream\_lead\_times − buffer Target C \= 1\[ completion\_time(stage\_m) \> CMD\_m \] NeedBy comes from the requiring body's construction schedule.  
D2. Discrete-time hazard Bucket width Δ (default 7 days). h\_k(x) \= P(T ∈ bucket k | T ≥ bucket k, x\_k); S(k) \= Π\_{j\<k}(1 − h\_j); P(complete within m buckets) \= 1 − S(m+1). Censored open stages contribute non-events for observed buckets. Implementation: gradient-boosted classifier on person-period rows with bucket index and time-varying features.  
D3. Target A A \= 1\[ T\_actual \> original\_baseline \+ tolerance \], derived from the survival curve as P(T \> baseline \+ tolerance) for open stages.  
D4. Workfront readiness Readiness\_w \= Σ\_{p ∈ P\_w} a\_p c\_p u\_p / Σ\_{p ∈ P\_w} a\_p c\_p Criticality c\_p is 1 for a parcel that fails the removal test (workfront continuity breaks if the parcel is unavailable), otherwise a lower configured weight; u\_p ∈ \[0,1\] combines possession, encumbrance-free status and access. Construction-enabling possession \= Σ a\_p c\_p u\_p / Σ a\_p c\_p over the project; Land acquired % \= Σ a\_p·1\[acquired\] / Σ a\_p.  
D5. Risk velocity v \= 7 × (r\_t − r\_{t−k}) / k points per week. Classes: stable |v| \< 5; rising 5 ≤ v \< 15; accelerating v ≥ 15 (configurable).  
D6. Priority Index Priority \= 100 × (0.35·Risk \+ 0.25·Urgency \+ 0.25·Impact \+ 0.15·Actionability), components in \[0,1\]; weights configurable. Urgency \= 1 − min(1, d/90) where d \= days to nearest statutory or critical deadline. Escalation boost: \+up to 10 points for accelerating projects. Items with Actionability below threshold θ are labelled "Monitor".  
D7. Financial exposure (Monte Carlo) For each draw i: sample delay d\_i from the predictive distribution; Cost\_i \= Σ\_k C\_k(d\_i) where curves C\_k (idle, financing, escalation, overhead, statutory interest) are defined to avoid overlap. Report P50/P80/P90 of Cost. Statutory interest curve: 0.12 × MarketValue × (t/365) within the s.30(3) window only.  
D8. Data confidence DC\_domain \= w\_c·completeness \+ w\_f·freshness \+ w\_a·agreement \+ w\_i·identity\_confidence; overall \= weighted mean; freshness decays with days since last successful sync.  
D9. Evidence grade HIGH: supported by ≥1 official structured record and no unresolved contradiction; MEDIUM: official record but stale, or verified grievance; LOW: inferred, unverified text, or stale plus inferred.  
D10. Scenario notation Baseline f(x); scenario f(x ⊕ Δ), where Δ modifies only allow-listed actionable features. No conditional-probability notation is used for scenarios, to avoid implying causal identification.  
---

## E. SRS with Acceptance Criteria

Purpose and scope. Requirements for BhuSanket, an intelligence overlay for predicting and prioritising land-acquisition delays. Excludes transaction processing, valuation and legal decision-making.  
Users and environment. Roles listed in the main report; browser and tablet use; containerised deployment on government-approved cloud.

### E.1 Functional requirements

| ID | Requirement | Input | Output | Acceptance criteria |
| :---- | :---- | :---- | :---- | :---- |
| FR-01 | Ingest project, stage, parcel, payment, case and R\&R data via API, file upload and scheduled adapters | Source payloads | Validated canonical records; rejects with reasons | ≥ 99% of well-formed synthetic records ingested; malformed records rejected with a reason code; ingestion is idempotent |
| FR-02 | Resolve parcel identity ULPIN-first with confidence and human confirmation | Parcel identifiers, geometry, survey numbers | ParcelIdentityMap entries | On a labelled synthetic set, exact-ULPIN matches 100% correct; ambiguous matches routed to review, none auto-merged below threshold |
| FR-03 | Model legal regimes as versioned process templates with statutory clocks | Template definitions | Stage graph, clocks | Adding a new template requires no code change; clock arithmetic matches template rules on 100% of test cases |
| FR-04 | Compute Statutory Deadline Risk per active clock | Clock instance, stage survival curve, pause intervals | days\_remaining, DeadlineRisk, alert state, consequence text | For 100% of synthetic projects with valid inputs, days\_remaining equals the template-defined value including stay pauses; consequence text comes from the template |
| FR-05 | Predict stage completion distribution (7/30/60/90-day probabilities, P50/P80/P90) | Feature snapshot at time T | Survival outputs | Calibration error on held-out synthetic later cohort ≤ 0.05; outputs monotone in horizon |
| FR-06 | Predict Target A and Target C | Stage, CMD, survival curve | Probabilities | Targets computed exactly per Appendix D on 100% of test records |
| FR-07 | Report risk, model confidence and data confidence separately | Predictions, data snapshots | Three separate values and a review flag | Review flag raised whenever model confidence \< threshold or data confidence \< threshold in test scenarios |
| FR-08 | Compute risk momentum and store prediction history | Successive PredictionSnapshots | Velocity, class, trajectory | Velocity matches D5 on test series; history queryable per project |
| FR-09 | Identify critical parcels, readiness and construction-enabling possession | Parcels, package geometry, need-by dates | c\_p, u\_p, readiness per segment | On the synthetic highway, planted blocking parcels identified with 100% recall in test |
| FR-10 | Generate evidence-backed explanations with evidence grades | Prediction, SHAP, records | Explanation, evidence list, grade | Every explanation links to ≥ 1 record; grade follows D9 |
| FR-11 | Provide modelled scenarios over allow-listed actions | Baseline features, Δ | Scenario outputs labelled "model simulation" | Actions outside the allow-list are rejected; the label is displayed on 100% of scenario screens |
| FR-12 | Rank interventions in a queue by Priority Index | Predictions, deadlines, playbook | Ordered queue with owner and due date | Ordering reproduces D6 on test cases; Monitor label applied per θ |
| FR-13 | Raise alerts on deadline risk, momentum, stays, contradictions, critical-parcel changes; digest and escalation | Events, predictions | Alerts with SLA escalation | Escalation fires when unacknowledged past SLA in tests; snoozes require a reason |
| FR-14 | Detect contradictions with severity, distinguishing staleness | Multi-source facts, timestamps | Contradiction objects | Staleness-only mismatches are not labelled contradictions in test cases; severity assigned per rule table |
| FR-15 | Detect administrative silence after source-health check | Update cadence, source health | Stagnation flag or data-issue flag | Simulated API outage produces a data-issue flag, not a risk increase |
| FR-16 | Preserve original, approved and forecast dates; compute baseline integrity | Baseline events | Slippage metrics, integrity score | Repeated re-baselining in test data lowers integrity score |
| FR-17 | Estimate financial exposure (P50/P80/P90) with modular cost curves | Delay distribution, cost inputs | Exposure quantiles with input sources | Removing any curve changes the total by exactly that curve; no double counting in test |
| FR-18 | Role- and jurisdiction-based access control with SSO/MFA | User, role | Access decisions | Users cannot view other jurisdictions; individual risk never appears in public view |
| FR-19 | Event-sourced, hash-chained audit and reproducible predictions | Any prediction/view/action | Audit records | Re-running a stored prediction from snapshots reproduces outputs exactly |
| FR-20 | Controlled continuous learning with drift detection and approval gate | New data, candidate models | Candidate report; approval record | No model reaches production without a recorded human approval |
| FR-21 | Enforce no-adverse-action invariants | Recommendation library | Allow-list enforcement | Test suite confirms prohibited action types cannot be produced |
| FR-22 | Provide REST APIs with OpenAPI documentation and webhooks | API calls | JSON/GeoJSON | All endpoints in the API list respond per schema in contract tests |
| FR-23 | GIS visualisation with layers and "Explain this area" | Geometry, predictions | Map views | Blocking-parcel layer shows only parcels flagged critical; explanation lists contributing factors |
| FR-24 | Event/document extraction with provenance (Phase 2\) | Orders/documents | Events with document/page provenance | Extracted stay events link to the source page in review tests |
| FR-25 | Acquisition Complexity Assessment (advisory) | Candidate alignments | Duration range, factors, data confidence | Output contains no score of land or community; system does not rank villages |

### E.2 Non-functional requirements

| Category | Requirement |
| :---- | :---- |
| Performance | Dashboard p95 \< 3 s; single-project prediction \< 1 s; batch scoring of 100,000 open stages \< 30 min |
| Scalability | ≥ 100,000 projects, ≥ 50 million parcel records |
| Availability | 99.5% target; demo best-effort |
| Reliability | Idempotent ingestion; retries with dead-letter handling; RPO ≤ 24 h; RTO ≤ 4 h |
| Security | OWASP ASVS L2; VAPT before go-live; secrets in a vault; least privilege |
| Privacy | Pseudonymisation; DPDP Act 2023 alignment; purpose limitation |
| Usability | WCAG 2.1 AA; bilingual UI; ≤ 3 clicks from home to a project's explanation |
| Interoperability | REST/JSON, GeoJSON, OGC services, OIDC |
| Reproducibility | Any past prediction re-creatable from snapshots |
| Maintainability | CI/CD; ≥ 70% unit-test coverage on core logic |
| Localisation | Unicode; Hindi and regional languages |

### E.3 Key APIs

GET  /v1/projects/{id}/risk | /timeline | /forecast | /explanation | /evidence | /dependencies  
GET  /v1/projects/{id}/blocking-parcels | /clocks | /data-quality | /prediction-history | /similar-projects | /recommendations  
POST /v1/projects/{id}/whatif | /interventions | /override  
GET  /v1/districts/{code}/trends      GET /v1/geo/projects?bbox=\&risk=  
POST /v1/ingest/projects | /v1/ingest/events      POST /v1/feedback | /v1/alerts/{id}/ack  
GET  /v1/models/{version}/performance | /explanation      GET /v1/audit  
Webhooks: risk.threshold\_crossed, clock.deadline\_risk, court.stay\_detected, contradiction.raised

---

## F. Traceability: Problem Statement → Module → Requirement → Demonstration

| PS deliverable | Module | Requirements | Demo moment |
| :---- | :---- | :---- | :---- |
| AI/ML delay prediction | Prediction engine | FR-05, FR-06 | Project X forecast (P50/P90) |
| Automated identification of high-probability delay | Queue, alerts | FR-12, FR-13 | Today's priorities |
| Project-wise risk score and prioritisation | Risk and Priority Index | FR-07, FR-12 | Command Center |
| Key delay drivers | Evidence engine | FR-10 | "Why?" panel |
| Explainable AI | Evidence, SHAP, grades | FR-10 | Evidence with grade |
| Dashboards (probability, categories, trends, timeline, indicators, comparisons) | Dashboards | FR-05, FR-08, FR-09 | Five screens |
| GIS visualisation of high-risk projects | GIS | FR-09, FR-23 | Corridor map, blocking parcels |
| Automated alerts and notifications | Alerts | FR-13 | Queue and escalation |
| Predictive recommendations | Scenario engine, playbook | FR-11, FR-12 | What-if |
| Continuous learning | MLOps | FR-20 | Governance screen |
| APIs for integration | Integration | FR-01, FR-22 | API demo with mock feeds |
| Secure role-based access, audit | Security | FR-18, FR-19, FR-21 | Audit reconstruction |
| Statutory deadlines (added value) | Deadline engine | FR-03, FR-04 | 34-day clock |

---

## G. Deployment and Failure Architecture

### G.1 Deployment

Internet / Government network  
        │  
   Reverse proxy / WAF (TLS)  
        │  
  ┌─────┴──────────────┐  
  │ Frontend (React)   │      Keycloak (OIDC, RBAC)  
  └─────┬──────────────┘             │  
        │                            │  
   API gateway ──────────────────────┘  
        │  
  ┌─────┼────────────┬──────────────┐  
  │     │            │              │  
Core API   ML service   Workers (Celery)  
  │     │            │              │  
  └─────┼────────────┴──────────────┘  
        │  
 PostgreSQL \+ PostGIS   Redis   Object storage  
        │  
 Prometheus → Grafana   Log store (audit, application)

Production adds: HA database, KMS-managed keys, SIEM integration, separate environments, and network segmentation for controlled-system connectors.

### G.2 Failure behaviour (graceful degradation)

| Failure | Behaviour |
| :---- | :---- |
| Model service unavailable | Serve the last validated prediction with timestamp and a "stale prediction" banner |
| Data source unavailable | Show last confirmed value and date; downgrade data confidence; mark dependent metrics "unavailable" (never estimate a fact) |
| Source healthy but silent | Treated as possible stagnation only after health check |
| GIS service unavailable | Tables and timelines remain functional |
| Language model unavailable | Deterministic template explanation |
| Notification service unavailable | Queue with retry; in-app alert always available |
| Database unavailable | Cached last-known dashboards read-only; ingestion buffered |
| Clock inputs missing | Clock state "cannot evaluate", with a task to supply the trigger date |

---

## H. Digital-Twin Specification (Synthetic Simulator)

Purpose. Test the whole pipeline before real data exists, and evaluate recommendation logic against known simulated effects.  
Entities. Regime and template, geography, packages and chainage, parcels with ULPIN-like identifiers, owners (with fragmentation and heir complexity), approvals, compensation flows, litigation, R\&R, administrative capacity, interventions with known true effects.  
Causal structure (planted):  
Ownership complexity ↑ → documentation delay ↑ → compensation delay ↑ → grievances ↑ → litigation probability ↑ → stay ↑ → possession delay ↑  
Funds-release gap → payment lag → protest probability ↑  
Administrative capacity (staffing, vacancy) → stage durations  
Season and election calendar → slowdowns  
Statutory clocks → extension events with probabilities  
Court stays → clock pauses (per template)

Realism features: censoring, missing blocks, stale updates, source contradictions, re-baselining, extensions, partial possession, multi-package linear projects, non-land delay causes, cancellations.  
Calibration. Delay-bucket shares are tuned toward published aggregates (for example MoSPI's distribution across 1-12, 13-24, 25-60 and 60+ month buckets \[R6\]). All demo outputs are labelled synthetic.  
Parameter-recovery test. The simulator plants known relationships (for example "compensation delay increases possession delay by X"). The model is trained on generated data and we check whether estimated effects and driver rankings recover the planted structure. This validates the pipeline, not real-world accuracy.  
Recommender check. For scenario Δ, compare the model-estimated change with the simulator's true counterfactual change; report error. This is recovery of effects *under the simulator's assumptions*, not evidence that an intervention works in practice.  
---

## I. Feature-Leakage Prevention Framework

Rule: for prediction time T, only data with observed\_at ≤ T may enter features (FeatureSnapshot(T)).  
Typical leakage sources and controls

| Leakage source | Control |
| :---- | :---- |
| Final compensation date, final court outcome, final possession date | Excluded from features; used only as labels |
| Future grievance counts, future extensions | Windows end at T |
| Percent-complete computed using later records | Recompute from events up to T |
| Later corrections to earlier data | Bitemporal store: use what was known at T |
| Baseline dates edited after the fact | Use original commitment and the approved baseline as of T |
| Random train/test splits | Rolling-origin, time-based splits only |
| Interventions applied after T | Recorded as treatments with timestamps; excluded before T |

Automated tests re-derive features from raw events for random (entity, T) pairs and assert equality with stored snapshots.  
---

## J. Edge Cases

| \# | Case | Handling |
| :---- | :---- | :---- |
| 1 | Missing or stale data | Missing-aware models, staleness features, confidence gating, data tasks |
| 2 | New project, no history | Priors and similar-project retrieval; wider intervals |
| 3 | Different laws and state amendments | Versioned templates per jurisdiction |
| 4 | Legal or policy change | Effective-dated templates; drift alarms |
| 5 | Sudden court stay | Event-driven re-score; clock pause per rule |
| 6 | Interventions change outcomes | Logged as treatments; no "fixed \= low risk" learning |
| 7 | Re-baselining hides delay | Original, approved, forecast dates; integrity score |
| 8 | Data gaming | Cross-source checks, anomaly detection on updates, audit |
| 9 | Class imbalance | Class weights, threshold tuning, PR-AUC focus |
| 10 | Multi-package linear projects | Segment-level scoring, aggregation |
| 11 | Partial possession | Parcel-level status; criticality weighting |
| 12 | Joint, ancestral, deceased owners | Ownership-complexity features; verification playbooks |
| 13 | Scheduled Areas and Gram Sabha consent | Template rules and safeguards, not predictive features |
| 14 | Elections, monsoon, harvest | Calendar features |
| 15 | Officer vacancies and transfers | Vacancy features; single-point-of-failure alert |
| 16 | Inter-state projects | Multi-jurisdiction ownership and coordinated alerts |
| 17 | Land cost exceeds project cost | Valuation-gap feature; exposure model |
| 18 | Duplicate or misspelt entities | ULPIN-first resolution with review |
| 19 | Low connectivity | Offline-capable field app (Phase 2); SMS fallback |
| 20 | Drift after special drives | Drift detection and change-point notes |
| 21 | Political misuse of scores | Role-limited visibility; framing as support needs; override reasons |
| 22 | Adversarial or spam grievances | Deduplication, rate limits, authority-weighted signals |
| 23 | Small districts | Partial pooling |
| 24 | Technically correct but useless explanations | Actionable drivers only; officer feedback |
| 25 | Downtime during review | HA, cached dashboards, offline export |
| 26 | Project cancellation | Terminal event; retained for survival analysis |
| 27 | Scope reduction | New baseline version with reason |
| 28 | Alignment change | Rebuild dependencies; carry parcel history |
| 29 | Parcel subdivision/merger | ULPIN lineage with validity intervals |
| 30 | Duplicate acquisition record | Identity resolution and contradiction flag |
| 31 | Compensation deposited in court | Distinct payment state |
| 32 | Owner refuses despite compensation available | Separate cause code and playbook |
| 33 | Disputed title, uncontested possession | Parcel status combinations under template rules |
| 34 | Government land recorded as private | Records-conflict event |
| 35 | Acquisition complete but construction cannot start | L3 delay with non-land cause |
| 36 | Project paused for non-land reasons | Separate cause; clock pauses only if the template says so |
| 37 | Statutory extension granted | Event; clock reset per rule; extension counted |
| 38 | Cross-source payment mismatch | Contradiction with severity |
| 39 | Court stay affecting part of a project | Parcel-level pause intervals; project-level effect via dependency graph |
| 40 | Source outage mistaken for stagnation | Source-health gate before silence signal |

---

## K. Risks and Mitigations

| Risk | Impact | Mitigation |
| :---- | :---- | :---- |
| Real data unavailable early | High | Digital twin; adapters with real schemas; phased pilot |
| Overstating integrations | High | Source-status table; "mock feed with real schema" wording |
| Causal misinterpretation | High | Modelled-scenario language; intervention logging; pilot design |
| Legal template errors | High | Legal review status per template; versioning; test cases per clock |
| Officer distrust | High | Evidence-graded explanations; co-design; tools that help fix data |
| Bias and feedback loops | High | Shrunk priors; fairness reports; invariants |
| Scope explosion | High | Hard MVP cap |
| Alert fatigue | Medium | Priority Index with actionability; digests |
| Privacy or security incident | High | Pseudonymisation; classification; VAPT |

---

## L. Diagrams to Produce for the Submission

1. System architecture (layers). 2\. Legal process graph with statutory clocks. 3\. Project dependency graph and critical path. 4\. ML pipeline (features → hazard model → Monte Carlo → outputs). 5\. Data-integration architecture with source status. 6\. Evidence graph example. 7\. Intervention feedback loop (detect → explain → locate → prioritise → simulate → assign → observe). 8\. Security and data-classification architecture. 9\. Deployment architecture (Section G.1). 10\. Digital-twin causal graph (Section H).


# Prajna Insight Model (PIM) / Prajna AI

PIM is a research prototype for bounded symbolic search, constraint-preserving cognitive reframing (CPCR), rule-based cost-aware insight gating (CAIG), independent answer verification, and auditable execution. Prajna AI is the broader development vision; capabilities proposed in that vision are tracked separately from implemented and tested components.

## Research documentary — 3 minutes

[![PIM / Prajna AI research documentary](media/research-film/thumbnail.png)](media/research-film/PIM-Prajna-AI-180s.mp4)

[Watch or download the complete film](media/research-film/PIM-Prajna-AI-180s.mp4) · [Detailed introduction — English / 繁體中文](docs/research-film.md) · [English subtitles](media/research-film/captions.en.srt) · [Media integrity manifest](media/research-film/manifest.json)

This English-language documentary presents the bounded research prototype, its exploratory negative results and unresolved limitations. It uses an authorized presenter portrait and AI-synthesized personal-voice narration in a photo-and-narration format. It is a research introduction, not evidence of general reasoning superiority or completed scientific peer review.

## Repository status

This private repository is the remote development home for the project. Its initial contents provide an English project overview. Source code, historical traces, datasets, manuscripts, and private author-review records remain in the local research workspace and have not been uploaded in this repository setup.

The current evidence supports a bounded research prototype. General reasoning-state sufficiency, general natural-language semantic fidelity, and superior reasoning performance have not been established.

## Existing research and engineering

- **Finite-domain CPCR:** proposal generation and a separate preservation checker examine explicitly declared finite domains. A preservation certificate does not replace the original answer verifier.
- **Rule-based CAIG:** heuristic cost-benefit estimates help select reasoning actions. A positive estimated gain does not prove an actual gain or an optimal action.
- **Answer and resource checks:** answer validity and budget-compliant execution success are distinct outcomes. Failed verification, unknown verification, and resource violations are preserved separately.
- **Trace and replay:** semantic-projection replay checks recorded execution consistency within its implemented contract. It does not establish original human-intent fidelity, task success, durable immutable storage, or independent scientific replication.
- **PIM-Bench:** exploratory evaluation uses a finite symbolic search implementation whose main reframing operation reorders a finite candidate catalog, with preservation checks and cost accounting.

## Historical development-pilot results

| System | Verified Success Rate | Mean accounted cost (units) |
| --- | ---: | ---: |
| B0 | 79.07% | 923.79 |
| B1 | 79.81% | 796.90 |
| PIM | 60.37% | 1294.22 |

These are preserved historical development-pilot observations for this implementation and experimental configuration. PIM had a lower observed success rate and higher mean accounted cost than both baselines. These results do not establish the general causal benefit or ineffectiveness of cognitive reframing.

The benchmark contains 180 tasks across 15 families, partitioned into 108 development, 36 validation, and 36 held-out tasks. The historical pilot evaluated nine development families: 108 tasks, five seeds, and eight policies produced 4,320 records. The paired 4,320 rerun records check consistency and are not additional independent experimental observations. Tasks, families, and seeds have statistical dependence. Accounted cost units are defined by the research cost model and are not a universal token, currency, or hardware-time measure. Validation and held-out confirmation remain incomplete.

## Latest isolated development work

Local evidence dated October 14, 2026 records:

| Work package | Scoped outcome | Implemented scope |
| --- | --- | --- |
| PIM-NEXT-IW-00 | VALIDATED | Offline structural launch gate and a non-executing command-line interface |
| PIM-NEXT-IW-03-T01 | VALIDATED | Finite-reference types, loaders, scorer, schemas, and a local TEST_VECTOR validation interface |

The isolated development namespace passed 46 tests: 19 governance tests and 27 finite-reference tests. Separate reviewer and validator agent contexts reviewed these scoped engineering changes. This is local engineering evidence, not external scientific peer review or full-project acceptance.

The parent IW-03 package remains pending a real reference bank and human review. The launch gate does not authenticate human identity or dispatch work. Finite test vectors do not establish human-intent correctness; resource compliance for the new scorer remains unevaluated. No research Worker or paid/live model API was used in that development window.

## Planned development

Work is organized into bounded, approved packages with explicit acceptance evidence:

1. Complete the finite reference bank and genuine human-reference review.
2. Develop versioned intent reassessment and clarification proposals without silently changing fixed task contracts.
3. Separate finalized execution traces from versioned external audit corrections.
4. Define and test snapshot finalization, atomic commit, and durable commit receipts.
5. Investigate Worker startup and resource-release observability while preserving existing runtime contracts.
6. Evaluate alternative gating policies through controlled comparisons, fair resource limits, and dependence-aware statistics.

Specification Fidelity, a complete Atomic Snapshot Commit mechanism, and an append-only External Audit Journal are proposed research directions. They are not delivered features. Runtime reliability and incomplete resource-release evidence remain unresolved; unknown release states do not prove either zero leakage or a leak.

## Research integrity and AI assistance

Historical positive, negative, failed, and unknown results are preserved. New work must not overwrite frozen datasets, traces, manuscripts, or prior audits. Engineering acceptance does not prove scientific superiority.

ChatGPT assisted with early mathematical-architecture discussions, research specifications, and work-package preparation. OpenAI Codex extensively assisted with formalization, software, tests, statistical analysis, literature checking, research audits, and manuscript preparation. Human decisions and actual review responses are recorded separately. Complete expression-by-expression and passage-by-passage provenance remains partially known. AI assistance does not substitute for human scientific responsibility.

## Repository language and material policy

Repository descriptions, new documentation, issue titles, and commit messages use English. Preserved historical material will retain its original bytes; any approved translation will be a separate, traceable version.

No repository license has been selected. Material rights and redistribution permissions require their own confirmation. Private research records, credentials, author information, and sealed evaluation data are excluded from this initial repository setup.

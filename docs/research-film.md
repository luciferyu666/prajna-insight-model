# PIM / Prajna AI - Research Documentary

[Repository overview](../README.md)

## Watch the complete film

[![PIM / Prajna AI research documentary](../media/research-film/thumbnail.png)](../media/research-film/PIM-Prajna-AI-180s.mp4)

- [Watch or download the 180-second MP4](../media/research-film/PIM-Prajna-AI-180s.mp4)
- [English subtitle file](../media/research-film/captions.en.srt)
- [Media integrity manifest](../media/research-film/manifest.json)

GitHub may display a video preview depending on the browser. If playback is unavailable, use the file page's raw/download control and open the downloaded MP4 in a local player. Access follows this repository's private permissions.

The film uses English narration and English captions. The detailed introduction below is provided in Traditional Chinese and English; a Chinese subtitle track is not included. The presentation uses an authorized formal-suit portrait and AI-synthesized personal-voice narration, with research cards. It is a photo-and-narration film, not a fully lip-synchronized presenter recording.

## Approved detailed bilingual introduction

The following source text is preserved verbatim from the approved published introduction. It describes bounded research findings and limitations; it does not establish scientific peer-review acceptance or completed author responsibility checks.

<!-- BEGIN PRESERVED APPROVED BILINGUAL TEXT -->
【PIM／Prajna AI｜3分鐘研究紀錄片完整版】
AI 能否不只尋找答案，也反省目前的解題方式與理解界線？

這支英文紀錄片介紹 Prajna Insight Model（PIM）的研究動機、已實作原型、真實實驗結果，以及仍待解決的問題。影片長3分鐘，附英文字幕；以下提供中英文研究說明。

▍目前實際做了什麼？
PIM 目前是有限符號搜尋的研究原型。此次受測的主要重構操作，是在預先定義的有限候選目錄中重新排序，配合約束保真檢查、原始答案驗證與操作成本記帳。它尚不是新訓練的基礎 LLM，也沒有把重構轉換成更快的下游求解器。

• CPCR：把轉換提案與保真檢查分開。有限域證書只支持其涵蓋的約束保全；候選答案仍須逆映射回原題，取得 Original Verifier PASS，才能視為已驗證答案。FAIL 與 UNKNOWN 分別保留。
• CAIG：使用人工設計的規則與成本收益估計，判斷是否考慮重構。預估淨收益為正，不代表已證明實際節省、因果效益或最優策略。
• Trace／Replay：保留執行軌跡與成本資料，檢查紀錄一致性。Replay 通過不等於原始人類意圖已被忠實理解，也不代表已具備不可變儲存。答案有效性與預算合規成功必須分開判定。

▍我們保留負面結果
歷史 Development Pilot 共4,320筆紀錄，另有4,320筆配對 Rerun 用於一致性核對；不能將兩者當成8,640個獨立實驗樣本。

已評測開發集上的觀察值（VSR＝已驗證成功率）：
B0：VSR 79.07%｜平均成本923.79
B1：VSR 79.81%｜平均成本796.90
PIM：VSR 60.37%｜平均成本1294.22

成本單位是研究定義的 accounted units，不是金額、Token 或 FLOPs。此次 PIM 實作的成功率較低、平均成本較高；這是需要解釋與改進的研究結果，不應隱藏。它也不能直接證明一般認知重構具有因果上的無效性。

▍現有證據的界線
評測只涵蓋九個開發家族，任務與 Seed 存在相依性；validation／held-out 評測尚未完成。現有結果未證明普遍泛化、完整八分量狀態的充分性，或 PIM 對其他推理方法的效能優越性。我們沒有在相同條件下，將 Reflexion、Self-Refine、Tree of Thoughts 等 LLM 方法納入這次公平對照。

▍下一階段研究方向
讓系統察覺可能誤解原題，提供條件式答案並尋求人類澄清；如需修訂已固定契約，應另建版本並保存證據。Specification Fidelity、Atomic Snapshot Commit 與 External Audit Journal 仍是未來研究方向，不能寫成已完成能力。Runtime 可靠性亦有未解限制：缺少資源釋放證據維持 UNKNOWN，既不宣稱零洩漏，也不直接斷定存在洩漏。

▍人機協作與聲畫揭露
ChatGPT 參與早期架構與研究規劃；Codex 參與形式化、軟體、分析與論文準備。逐公式／逐段落的完整來源仍有未知，全面真人科學審閱尚未完成。影片採本人授權的人像與既有 AI 合成本人聲線，為照片旁白呈現。哲學啟發是研究動機，不是已證明的自然科學定律。

歡迎研究者與開發者提出可獨立檢驗的問題、反例與修正建議。這項計畫的目標，是讓每個主張都能被理解、檢查與質疑，而不是提前宣告突破。

────────── ENGLISH ──────────

PIM / Prajna AI — A Three-Minute Research Documentary
Can AI examine the limits of its current approach, as well as search for answers?

This English-language film, with English captions, presents the motivation, implemented prototype, historical results and open limitations of Prajna Insight Model (PIM).

WHAT IS IMPLEMENTED
PIM is currently a bounded symbolic-search research prototype. In the evaluated implementation, reframing primarily reorders predefined finite candidate catalogs, alongside constraint-preservation checks, original-answer verification and operational cost accounting. It is not a newly trained foundation LLM, and reframing was not converted into a faster downstream solver.

• CPCR separates transformation proposals from preservation checking. A finite-domain certificate supports only the declared preservation conditions it covers. An answer must map back to the original problem and receive the original verifier's PASS. FAIL and UNKNOWN remain distinct.
• CAIG uses hand-designed rules and cost-benefit estimates to consider reframing. Positive estimated benefit does not establish realized savings, causal advantage or optimal decisions.
• Trace and replay make execution records and costs inspectable. Replay consistency does not establish faithful human-intent understanding or immutable storage. Answer validity and budget-compliant success are separate outcomes.

THE NEGATIVE RESULTS REMAIN IN THE RECORD
The historical Development Pilot contains 4,320 records. A paired 4,320-record rerun checks consistency; these are not 8,640 independent observations.

Observed development results (VSR = Verified Success Rate):
B0: VSR 79.07% | Mean cost 923.79
B1: VSR 79.81% | Mean cost 796.90
PIM: VSR 60.37% | Mean cost 1294.22

Costs are research-defined accounted units, not currency, tokens or FLOPs. PIM succeeded less often and cost more in this evaluated implementation. These findings should be examined openly; they do not establish that cognitive reframing is causally ineffective in general.

LIMITS OF THE EVIDENCE
Only nine development families were evaluated. Tasks and seeds are dependent, and validation/held-out evaluation remains unfinished. These data do not establish broad generalization, sufficiency of the full eight-component state model or performance superiority. Reflexion, Self-Refine and Tree of Thoughts were not evaluated as matched LLM baselines in this benchmark.

NEXT RESEARCH DIRECTIONS
Future work includes recognizing a possible misinterpretation, presenting conditional answers and seeking human clarification. Revisions to a fixed contract require a new version and preserved evidence. Specification Fidelity, Atomic Snapshot Commit and an External Audit Journal remain proposed work, not established capabilities. Runtime reliability also has unresolved limits: missing resource-release evidence remains UNKNOWN and establishes neither zero leakage nor a leak.

HUMAN–AI AND MEDIA DISCLOSURE
ChatGPT assisted early architecture and research planning. Codex contributed formalization, software, analysis and manuscript preparation. Complete expression-level provenance and comprehensive human scientific review remain incomplete. This film uses an authorized personal portrait and existing AI-synthesized personal-voice narration in a photo-and-narration format. Philosophical inspiration is not a demonstrated scientific law.

Researchers and developers are welcome to contribute independently checkable questions, counterexamples and corrections. Our aim is to make claims inspectable, including negative findings and unresolved questions.

#PrajnaAI #PIM #AIResearch #ResponsibleAI #ReproducibleResearch #般若人工智慧 #人工智慧研究
<!-- END PRESERVED APPROVED BILINGUAL TEXT -->

## Version and evidence boundary

The source film is the human-accepted Formal Photo v02 complete version. The manifest identifies its exact bytes with SHA-256; hashes provide integrity checks, not immutable storage or unrestricted redistribution rights. No new media generation, research experiment, manuscript submission or research acceptance decision was performed for this integration.

[Previously published Facebook group version](https://www.facebook.com/groups/2377474206389416/posts/2378986912904812) (Facebook access may require login). No YouTube publication is claimed here.

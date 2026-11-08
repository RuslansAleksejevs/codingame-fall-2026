# Competitive advantage when everyone can use an AI assistant

Reviewed **8 November 2026**. Primary literature through October 2026; Kaggle and CodinGame accounts from 2025–2026. This is a curated evidence review, not a systematic review, a replication, or a new training campaign.

## Bottom line

The available evidence does **not** establish that every competitor uses an LLM, or that agent-assisted competitors face a universal top-20–30% ceiling. Access to an assistant does not equalize accumulated infrastructure, domain knowledge, data, compute, evaluation quality or the ability to deliver a working solution under contest constraints.

There is a direct recent example of a human winning with coding assistants: Chris Deotte's March 2026 Kaggle Playground solution. There are also recent autonomous-agent benchmark results well beyond older medal rates. Neither observation proves that a particular human workflow, prompt or number of agents causes success in today's live contests.

The strongest common practical pattern is a **measured research loop**: identify a specific limitation, execute a controlled change, preserve evidence, reject misleading gains, and deliver the selected solution within real resource limits. Agents can help with all of these tasks; this is not a claim that they must be performed manually. The competitive distinction is whether the work is organized and verified at all.

## Evidence classes and scope

- **SOURCE_VERIFIED:** the cited primary source was read and contains the stated claim. External scores/ranks remain **author-reported**, not independently replicated here. Final official leaderboards were not downloaded for the historical cases.
- **PROJECT_REPORTED:** this repository's recorded experiments and independent local audits. No new game or training run accompanied this review.
- **MODEL_INFERENCE:** recommendations and cross-domain interpretations; not proven causes of a competitor's rank.
- **UNKNOWN:** unreported budgets, coding-assistant use, causal contributions or facts not established by the source.

Three bounded read-only reviews covered 12 primary research studies, eight Kaggle solutions across seven competitions plus one practitioner account, and ten directly relevant CodinGame/source groups. Original papers, author repositories and public forum posts were preferred. Some full Kaggle discussion bodies were inaccessible; linked author writeups/repositories were read instead. This does not support a claim to have read every forum or closed Discord. Search integrations without configured accounts were not enabled; no paid resources, OAuth, participant messages or new experiments were used.

## What strong competitors add to the assistant

| Practice | Concrete evidence | Operational lesson |
|---|---|---|
| Choose a test that represents the real task | Ramza's self-match search initially lost on the live ladder; AIMO-2 later models improved locally but not in Kaggle | A local metric is a hypothesis about deployment, not deployment itself. Match opponents, splits, runtime and failure conditions. |
| Understand the data/game structure | CMI sensor orientation and quaternion symmetry; ECG geometry; Indrill's joint-action representation | Ask what signal or coordinated action is missing before asking for a larger network. |
| Keep a reusable experimental record | Deotte saved out-of-fold and test predictions for every experiment; HMA preserves workspace state across bounded sessions | Save executable versions, configurations, predictions, failures and costs, not only conversational conclusions. |
| Change the component that is actually limiting performance | MLE-STAR uses targeted ablation; jacek profiled simulation and rejected generic container advice | Measure the bottleneck, specify one hypothesis and an observable rejection condition. |
| Seek diversity of errors, not a count of models | CMI CNNs complemented the team despite similar standalone CV; Deotte selected 150 models from 850 experiments | Evaluate incremental value and inference cost. More agents/checkpoints are not automatically more useful. |
| Optimize the entire delivered system | AIMO-2 quantization, scheduling and early stopping; Pduhard cached inference and compact search | Source size, startup, tail latency, incomplete outputs and export correctness are part of the objective. |
| Audit apparent scientific progress | METR's subjective/objective mismatch; the polymer practitioner's leakage and swallowed errors; benchmark provenance problems | Fail loudly, separate measurement from interpretation, and independently check the decisive result. |
| Allocate time and stop intelligently | On the Clock distinguishes budget adherence from productive work; HMA reserves final review | Count useful experiments and held-out gain, not hours occupied. Preserve a final test and a known fallback. |

These practices are a synthesis, not a randomized proof of each row. Published winners are a selected sample; failed and unreported approaches, prior experience and unequal compute confound simple causal stories.

## Recent research: what the numbers actually mean

### R1. Humanize MLE Agents — October 2026

Changye Li et al., [v1, 9 October 2026](https://arxiv.org/abs/2610.13494v1), [full paper](https://arxiv.org/html/2610.13494v1). HMA alternates two complete model/harness systems on a shared workspace, resets conversational context, caps each session at five experiments and reserves 15 minutes for final review. Its best configuration reports **78.2% any-medal tasks**, versus **72.4%** for its strongest single-agent baseline under the same six-hour limit. The reversed starting order reaches 73.3%.

This is the full 75-task MLE-bench, with hidden offline test scoring; the reported evaluation uses repeated runs. Each task has an A10 24 GiB, 30 vCPU and 220 GiB RAM. A 75-task, three-repeat configuration has a maximum 1,350 A10-hour allowance. It is a fresh preprint, not an independent replication. These are historical Kaggle thresholds, **not 78.2% of today's competitors beaten**, and heterogeneous alternation does not prove that three identical assistants improve our outcome. No model/account switch is proposed.

### R2. MLE-STAR — 2025

Jaehyun Nam et al., [v3, 28 August 2025](https://arxiv.org/html/2506.15692v3). Web-retrieved task-specific models, targeted component ablations/refinement and ensemble search. On 22 MLE-bench Lite tasks, Gemini-2.0-Flash obtains 43.9% any-medal versus AIDE's 25.8% with the same model; the Gemini-2.5-Pro headline is approximately 64%.

The study uses three seeds, a 24-hour cap and substantial hardware (reported infrastructure: eight V100s, 96 vCPU, 360 GB RAM). It supports a structured experimental process, not a cheap single-chat recipe or a live Kaggle percentile. Public historic tasks and adaptive method development limit contamination/generalization claims.

### R3. MLE-bench — the historical comparison behind many headlines

Chan et al., [ICLR version, February 2025](https://arxiv.org/html/2410.07095v6). Seventy-five historic Kaggle tasks; o1-preview+AIDE reports 16.9% medal rate at pass@1 and 34.1% at pass@8. Some tasks use reconstructed splits when original private labels are unavailable. The basic budget is 24 hours per task, one A10, 36 vCPU and 440 GB RAM.

Pass@8 pays for multiple attempts and does not establish that an agent can select the winning one without hidden-test feedback. The old o1 result is not a 2026 capability ceiling. Historical human scores, unequal budgets and possible training-data exposure must be kept separate.

### R4. AIDE — executable search instead of one-shot code

Jiang et al., [February 2025](https://arxiv.org/html/2502.13138v1). Program-tree search with draft/debug/improve operations. An early 16-task tabular comparison reports mean historical-human-percentile performance of 51.38 for AIDE versus 41.17 for a human-with-ChatGPT baseline. The underlying runs/model are from early 2024, and the human condition is not a matched-budget study of leading competitors. Mean percentile, medal rate and current live rank are different measures.

### R5. RE-Bench — experts were allowed LLMs

Wijk et al., [v2, May 2025](https://arxiv.org/html/2411.15114v2). Seven ML R&D environments, 71 eight-hour attempts from 61 experts. At short budgets the tested 2024 agents were ahead; experts gained with more total attempts/time. Crucially, Appendix A.1 permits humans to use the internet, LLMs and other tools. The 32-hour condition is best-of-four independent eight-hour attempts, not one uninterrupted run.

This is not an experiment isolating the causal effect of adding an assistant. Its monetary comparison excludes H100 compute, and one apparently strong finetuning result fell from 0.88 to 0.69 on rerun. Diagnosis and reliable selection matter; the old models do not establish a permanent human advantage.

### R6. MLRC-Bench — ideas are not working implementations

Zhang et al., [NeurIPS 2025 Datasets and Benchmarks, v3](https://arxiv.org/html/2504.09702v3). Seven research-competition tasks. The best tested system closes 9.3% of the normalized baseline-to-best-human gap; this is not a 9.3% task success rate. Human ideas improve some implementation pass@k measures without reliably improving the best final score. Typical budget: eight trials, 50 steps/five hours each, one RTX 8000 or V100. Execution errors and weak diagnosis are material limitations; most tested model generations predate 2026.

### R7. On the Clock — October 2026

Wang et al., [7 October 2026](https://arxiv.org/html/2610.10833v1). Qwen3.6-27B on five MLE-bench Lite tasks, with 10–25 minute budgets; smaller Qwen models on Zork. Timing feedback/enforcement improve adherence. Budget-aware RL does not improve MLE task quality over the untrained harness; extra time can be filled with repetitive actions. The source reports workshop acceptance. This is a concrete warning against equating duration with progress, **not** an evaluation of our Astra runtime or proof that long frontier-agent runs are useless.

### R8. Human productivity: METR 2025 and its 2026 update must be read together

The [2025 randomized study](https://arxiv.org/abs/2507.09089v2) found a 19% slowdown for 16 experienced maintainers on 246 familiar-repository tasks. The authors now explicitly caution that the old result does not characterize current tools. The [24 February 2026 update](https://metr.org/blog/2026-02-24-uplift-update/) reports raw time changes of −18% for returning developers and −4% for new developers, with both confidence intervals crossing zero.

The update emphasizes severe participant/task selection and parallel-work accounting problems. It does not provide a trustworthy universal current speedup. Neither study directly explains Kaggle rankings. The useful lesson is that confidence and perceived productivity are not reliable measurements.

### R9. The Cybernetic Teammate — causal evidence, but outside competitions

Dell'Acqua et al., [NBER working paper 33641, April 2025](https://www.nber.org/papers/w33641); the page lists a 2026 Organization Science publication. The actually reviewed working-paper experiment randomized 776 P&G employees into individual/team and AI/no-AI conditions. AI-assisted individuals matched unaided teams on average; team+AI increased top-decile probability by 9.2pp over a 5.8% control mean.

These are 2024 product-ideation tasks and blinded expert ratings, not executable ML competition results. The 2026 publication date does not make the model/data contemporary. No coefficients should be transplanted to our bot, and there is no equal-budget autonomous-agent arm.

### R10. Two important provenance warnings

[AI Scientist-v2, April 2025](https://arxiv.org/html/2504.08066v1) reports a workshop-level acceptance among three submitted manuscripts. Humans selected initial ideas and the best manuscripts from multiple seeds; the authors also identified substantial train/test overlap in part of the accepted work. One out of three submissions is not one out of three random runs or main-track acceptance.

[Evolutionary Ensemble Search, September 2026](https://arxiv.org/html/2609.17590v1) reports 19/22 medal-threshold artifacts, but explicitly describes an adaptive development ledger and external lookup routes, including target lookup. It is not a uniform-budget blind 86.36% generalization success rate. A grader accepting predictions does not establish rule compliance or legitimate source access. These methods are **not** a recommendation to obtain withheld labels.

## Kaggle: recent primary cases

### K1. An actual win using coding assistants: Chris Deotte, March 2026

[Author article, 23 April 2026](https://developer.nvidia.com/blog/winning-a-kaggle-competition-with-generative-ai-assisted-coding/) and [linked Kaggle writeup](https://www.kaggle.com/competitions/playground-series-s6e3/writeups/1st-place-gpt5-4-gemini3-1-claudeopus4-6-kgm). The author reports first place in Playground S6E3 with GPT-5.4 Pro, Gemini 3.1 Pro and Claude Opus 4.6: 850 experiments and a four-level stack of 150 models.

The concrete human-guided workflow is EDA → diverse k-fold baselines → feature/model experiments → integration. Every experiment saves comparable out-of-fold and test predictions, including failures. Agents read papers/code, propose changes and help combine the accumulated results. This is far more specific than "use a better prompt". However, total GPU/API cost and equal-budget ablations are absent; the GPU-vendor-hosted success story does not prove three assistants or 850 trials were necessary. Large adaptive search can overfit CV too.

### K2. AIMO-2 first place: whole-system optimization

Moshkov et al., [AIMO-2 Winning Solution, 23 April 2025](https://arxiv.org/html/2504.16891v1), especially §6. The submitted 14B system scores 34/50 private under a five-hour, four-L4 inference limit. It combines CoT/TIR training, weight mixing, TensorRT-LLM, FP8/ReDrafter, asynchronous generation and early stopping. Authors report 210→554 tokens/s in a specific four-L4 comparison. GenSelect belongs to later work, not the winning submission.

Later models looked better locally but did not reproduce that Kaggle result. Longer outputs and dataset shift are discussed as hypotheses. A model's fixed-token accuracy is not the same as the executable system's wall-clock score. Coding-assistant use is UNKNOWN; an LLM used as the solution is not evidence of an LLM used to write it.

### K3. AIMO-2 second place: speed has an accuracy cost

[Imagination Research repository](https://github.com/imagination-research/aimo2), created March 2025. SFT/DPO of a 14B model, length-aware preferences, AWQ4/KV8, mixed code/CoT samples and dynamic stopping; author-reported public 34/50, private 31/50. SFT uses 8×A800 for 11 hours and DPO 8×A800 for 40 hours. Quantization improves latency but the authors report a 5–10% per-sample accuracy deterioration, with percentage interpretation not clarified. This is neither a free speedup nor a laptop-scale recipe. Coding-assistant use is UNKNOWN.

### K4. ECG image digitization fifth place: geometry and label diagnostics

[`dangnh0611` repository](https://github.com/dangnh0611/kaggle_ecg_digitization), created January 2026, and [ablation study](https://github.com/dangnh0611/kaggle_ecg_digitization/blob/main/docs/ABLATION_STUDY.md). Orientation correction, keypoints, local homographies, waveform heatmaps and special handling of large amplitudes. The author reports fold-0 SNR improving from 21.545642 to 22.929716 for a particular global→local homography comparison, and derives augmentation scale from measured keypoint errors.

Important limitations: the ablation evaluator modifies lead-II duration relative to the official metric; some final-model figures are training SNR, not validation. The full ensemble also adds multiple refinements, so its gain is not an isolated ensemble ablation. The README changelog year conflicts with repository metadata. These caveats matter more than a headline backbone name. Assistant use and all-in training budget are UNKNOWN.

### K5. CMI sensor behavior third place: domain invariants and complementary models

[Theo Viel's part of the team solution](https://github.com/TheoViel/kaggle_cmi_behavior), repository created July 2025. Handedness normalization, quaternion symmetry, fixing reversed device orientation, and transformations that preserve physical meaning. CNNs had similar CV to transformers but blended better into the team ensemble. The author's initial intuition against the image representation was revised after a teammate's measured result.

This is evidence for data understanding and incremental ensemble value, not proof that CNNs universally beat transformers. The repository covers only one part of the team; exact team-score attribution and coding-assistant use are not established. A subject-safe split must not be assumed merely because the task has subjects.

### K6. Open Polymer first place: additional domain signal

[`jday96314` reproduction repository](https://github.com/jday96314/NeurIPS-polymer-prediction), created September 2025. Its [winning script](https://github.com/jday96314/NeurIPS-polymer-prediction/blob/main/train_winning_ensemble.sh) includes external polymer data, relabeling, molecular-dynamics outputs, simulation-metric prediction, BERT, Uni-Mol and tabular models. An archive retains rejected experiments.

The code establishes a richer pipeline, not the isolated causal contribution of each source. Minimum 24 GB GPU memory is not a full winning compute budget. Reproduction warnings include dependency conflicts. External data must be separately authorized by each competition's rules; assistant use is UNKNOWN.

### K7. BirdCLEF+ fifth place: the inference format is part of the solution

[`myso1987` reproduction README](https://github.com/myso1987/BirdCLEF-2025-5th-place-solution), created June 2025, linked to [Kaggle discussion 583312](https://www.kaggle.com/competitions/birdclef-2025/discussion/583312). Multiple sound-event model families, 30/60-second context, rare-class oversampling, multi-stage pseudo-labeling and OpenVINO export. The author lists an RTX3090 and 192 GB RAM.

The accessible README does not provide quantitative ablations; the full discussion body was not used as evidence. It establishes implementation structure, not how much each component helped. Coding-assistant use is UNKNOWN.

### K8. March Mania third place: a small model plus strong external signal

[`kevin1000` repository and writeup](https://github.com/kevin1000/march-mania-2026-3rd-place), created April 2026. Author-reported 3/3,485, Brier score 0.1160374 over 126 games. Logistic regression, ratings and feature pruning were blended with market/BPI probabilities. Some first-round predictions used 90% market consensus, so "simple logistic regression alone won" would be misleading.

The author reports 52 rounds over four weeks and negative results for additional features and LR+XGB blending. Grouping CV by season does not by itself ensure training only on past seasons; external-data timestamps/rules require auditing. Assistant use is UNKNOWN. This case argues against automatically equating more parameters with a stronger signal, not against boosting in general.

### K9. A non-winner-selected practitioner account: Claude Code on polymer prediction

[`wal8800`, 11 October 2025](https://wal8800.github.io/posts/claude-code-kaggle/). Rank is not stated. The author found agents useful for EDA/baselines/papers, but reports swallowed exceptions, preprocessing leakage, and recommendations written into scripts before statistics had run. Separating actual measurements from later interpretation helped. This is personal experience, not a measured error rate or a universal statement about current models.

## CodinGame: directly relevant 2026 experience

### C1. Indrill, Summer 2026: the engine is a long-term asset

Author-reported first place: [algorithm, 21 September](https://forum.codingame.com/t/summer-challenge-2026-feedback-strategies/208574/5); [AI and learning process, 29 September](https://forum.codingame.com/t/summer-challenge-2026-feedback-strategies/208574/15). A long-developed RL pipeline, BTR-like Q-learning, informative observations and coordinated actions, without final search. The explicit advice is to retain ownership/understanding of the core engine, challenge bugs rather than accept "noise", consult reference implementations and start small with tests. This is not evidence that rewriting our bot to BTR in a few hours will work.

### C2. Ramza, Summer 2026: search can exploit the wrong opponent

Author-reported fourth place: [24 September post](https://forum.codingame.com/t/summer-challenge-2026-feedback-strategies/208574/10). BC→PPO GNN, enemy-action head, auxiliary targets, compact value function and search. Strong self-match gains initially failed on the ladder because search predicted its own network too well. Diverse exploiters and opponent exploration reportedly helped. The phrase "+20 point improvement" does not specify units and is not rewritten here as percentage points. Assistant use is not established in this post.

### C3. Pduhard, Summer 2026: reuse inference work and validate export

Author-reported third place: [pinned September postmortem](https://github.com/Pduhard/back-track-king-postmortem/blob/398160842664b94e6141a2a0d5788d9f04a6023e/README.md). PPO, historical opponents, checkpoint averaging, a cached trunk for subactions, distillation and a few complete-plan lookaheads. Exact state/export comparisons and 1,024-game tests; Claude is explicitly credited for explaining global pooling. A 0.839 mirror score is not broad external strength. The author's exclusion of host-attributed timeouts is not adopted without causal evidence in our own evaluation.

### C4. JOiy/tcordel, Summer 2026: training curves do not prove ladder progress

[21 September Claude-bot account](https://gist.github.com/tcordel/18661da88fddcdee2a72c8127379c012). Author-reported Legend, no exact rank used. Autoregressive legal actions, cached shared computation, counterfactual features, slot-consistent discount and historical opponents. The author reports that training-map evaluation hid weak generalization; held-out maps and two 1,024-game checks mattered. Repeated adaptive use of one holdout can still overfit it.

### C5. putibuzu and jacek: useful AI advice still needs measurement

[putibuzu, September 2026](https://forum.codingame.com/t/summer-challenge-2026-feedback-strategies/208574/4) explicitly describes extensive coding-agent assistance, discount-horizon corrections and weight averaging, but continued need for guidance. Exact rank is not asserted. [jacek, March 2026](https://forum.codingame.com/t/winter-challenge-2026-feedbacks-and-strategies/208044/3), author-reported 17th/Legend, used free AI chats and reports approximately 3× more simulations after some optimizations, while repeated vector→deque/ring-buffer advice was worse or neutral. Profiling distinguishes helpful suggestions from plausible ones.

### C6. A non-top counterexample: generated code can preserve the wrong bottleneck

[Telokis, July 2025](https://forum.codingame.com/t/summer-challenge-2025-post-mortem/207074/26), author-reported 225th. A Claude-translated A* consumed 91% of time; allocation-free BFS unlocked more search. This avoids selecting only successful AI stories. It is not evidence that all generated code is slow or that 2025 judgments apply unchanged to 2026 models.

### C7. Current Fall 2026 sources do not reveal the current leaders

[Lacoz's pinned diary](https://github.com/Lacoz/cg2026/blob/7f1901834d2ffc16532e083edfec8cbdb5941ab6/README.md) describes full-plan local search, loss analysis and local/live discrepancies; [khoufou's pinned two-ply revision](https://github.com/khoufou/Codingame_2026-11_FallChallenge/commit/070bc12803f10099755d35eb773c6724bd305434) includes an explicit coding-LLM co-author and rejected experiments. Their public HEADs remained the 5/6 November versions at this review. Their reported internal wins are not today's leading-field performance.

The inspected current-contest forum results cover [AI rules](https://forum.codingame.com/t/fall-challenge-2026-ai-rules/208706), [league/input discrepancies](https://forum.codingame.com/t/fall-challenge-2026-no-wood-league-and-missing-input/208705) and [stalled games](https://forum.codingame.com/t/fall-challenge-2026-games-not-running/208708). The competition is ongoing: no final winner writeup exists in these sources. The affirmative AI-rules response is from a non-staff participant, not a complete official regulation. Separately, official API documentation already supports coding-agent workflows.

The [official CodinGame announcement](https://bsky.app/profile/codingame.bsky.social/post/3mxyfcrrg6c2e), published 16 October, was freshly read through its public oEmbed: 2–9 November, 10 AM–10 AM CET, hence **9 November 09:00 UTC**. Unauthenticated challenge GET returned 401; no OAuth was started. The announcement corroborates the saved authenticated deadline, not the current personal ranking.

## What this means for this project

Our integrity work prevents false claims; it does not itself create a strong strategy. The most recent measured positive mechanism is bounded search. The delivery bottleneck is retaining that advantage in a legal single-file bot: the original teacher is too large under the current encoder, while the compact student lost strength. The cause of that learning failure is still unknown.

The current local panel also contains related and saturated opponents, so direct wins and local averages cannot guarantee ladder progress. More agents, more generic PPO steps, or a large architecture rewrite are not evidence-based substitutes for resolving these two issues. See [three ranked last-day options](LAST_DAY_OPTIONS.md); none has been launched.

For future contests, retain a reusable simulator/evaluation/export stack and begin with richer task representations and credible external opponents early. For the remaining hours, prioritize one measured mechanism and its end-to-end delivery, freeze the candidate before final evaluation, and keep submission permission separate.

## Claims this review deliberately does not make

There is no measured universal AI adoption rate, no fixed percentile ceiling, no controlled attribution of winners' ranks to human guidance, no proof that three agents beat one at equal budget, and no claim that the listed external results were reproduced here. Historic Kaggle medal thresholds, live ranking, research-paper acceptance, human productivity and model accuracy are not interchangeable outcomes. Full costs and source provenance matter; more recent publication dates do not necessarily mean more recent models or data.
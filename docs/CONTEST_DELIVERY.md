# Contest delivery: entries, final source and remaining checks

Checked9 November2026. Official public sources were read again, including the
actual dynamically loaded text of [general contest rules](https://www.codingame.com/rules).
[Preserved source evidence](../experiments/rl/2026-11-09-d16-live/final-review/rules-snapshot.json)
records URLs, source hashes, the relevant API sections and contest FAQ.
Facts below are SOURCE_VERIFIED unless an inference or uncertainty is stated.

## How many bots count?

**One active ranked bot per participant in this contest.** General rules Article2
allow one registration per person. The official
[submission API](https://www.codingame.com/api/v1/docs/api) explicitly says a new
submission replaces the current one and starts its ranking games; earlier sources
remain in history. Several saved candidates are not several simultaneous entries.
Do not use additional accounts to obtain additional places.

Successive replacements are permitted while the contest is ongoing, subject to
rate limits. API examples list5/5minutes,20/30minutes,40/hour and100/5hours;
actual limits must be read before any submission. These are request quotas,
not the number of bots in the final standings. A test game does not enter the
rating. Saving/editing IDE code is also not a ranking submission.

Operational final-version rule (MODEL_INFERENCE from documented replacement
semantics): leave the intended final source as the current accepted submission
before the deadline, then verify its identity and completion. Do not assume the
platform selects the best historical score. A contest-specific description of
post-deadline reranking, tie-breaking and exact freeze mechanics was not found
in the checked public sources; those details remain UNKNOWN.

## Deadline and deliverables

The current contest FAQ states9November10:00CET, which is
**2026-11-09T09:00:00Z**. Fresh public contest metadata still says ongoing.
The earlier authenticated challenge response agrees. Source delivery must be to
the Fall Challenge arena, not the permanent TryAngle Catch puzzle.

No requirement to upload a separate paper, write-up, video, slides, model file,
public repository or final confirmation form was found in the contest FAQ,
general rules or API workflow. For the normal programming entry, the artifact
is the accepted source code. This is an evidence-based checklist, not a claim
that every possible organizer communication has been reviewed.

General Article6 allows later contact for prize/address information if prizes
are offered. The current contest description advertises no prize items. The
published rules also say submitted solutions may be released by CodinGame under
GPLv3 after the contest; that is not a requirement to make this repository public.

## Rules caveats that must not be hidden

- General Articles2/8 contain a blanket prohibition of third-party/machine
  assistance. In contrast, this exact Fall Challenge page explicitly invites
  orchestrating agents through its new public API, and the official API docs
  expressly support coding agents playing Bot Programming contests. This is a
  real inconsistency in the published texts, not a guarantee of legal precedence.
  The linked community reply says AI is allowed, but its author is not marked
  staff/admin/moderator and is not treated as an official override.
- The contest FAQ forbids copying code between players. General Article8 also
  forbids public release during the contest, exploiting infrastructure flaws and
  code obfuscation. Keep this repository private and preserve third-party
  provenance. Compact numerical weight storage has a documented decoder, but
  no organizer ruling specifically approving this encoding was found.
- General Articles4/5 describe sequential questions and test-case scoring, unlike
  this Bot Programming contest. Their auto-submit/final-question language is not
  used to infer arena freeze or reranking behavior. Verify the actual accepted
  submission rather than relying on an unsent IDE buffer.

Sources: [contest](https://www.codingame.com/contests/fall-challenge-2026),
[general rules](https://www.codingame.com/rules),
[API](https://www.codingame.com/api/v1/docs/api),
[API overview](https://www.codingame.com/api/v1/docs),
[community discussion, nonstaff](https://forum.codingame.com/t/fall-challenge-2026-ai-rules/208706/2).

## Final operational checklist

1. Inspect the completed current D16 rating, accepted source and full battle audit.
2. Choose exactly one final candidate. Current D16 A3 and preserved league3m are
   the realistic options; B2M is a reserve, rejected students are not finalists.
3. If a different source is chosen, obtain explicit authorization for that
   replacement, recheck time/limits, submit once and verify acceptance/completion.
   No new submission is required simply to keep an already accepted current bot.
4. Preserve the exact source hash, submission ID and dated ranking evidence.
   Keep post-deadline contest standings separate from a100%-completed submission.
5. Keep the repository private. No automatic rollback, further training or public
   write-up follows from this checklist.
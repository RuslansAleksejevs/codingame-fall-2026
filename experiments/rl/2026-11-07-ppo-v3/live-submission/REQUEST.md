# Authorized B2M leaderboard submission

Authorization:2026-11-08, USER_CONFIRMED in the current chat: submit the bot to
the leaderboard and return with conclusions. This supersedes the previous
test-only restriction for this candidate. It does not authorize Git commit/push,
new training, paid resources, an IDE overwrite or automatic candidate changes.

Candidate: `../handoff-b2m/bot.cpp`, SHA256
`b87388adc48e8806edca275a589f5fe036f8e837ff1ebcd7e4a69276646ff214`.
Preserved fallback: `submissions/ppo-v2-league3m.cpp`, SHA256
`199c6a2d2c0a7e9438351aad25e6eeda5816111b9fb672cdc0eb302052cd19c1`.
Both hashes were rechecked before starting the new authorization flow.
The completed platform series remains in `../platform/`; no raw record is
overwritten. B2M was technically clean but strength improvement remains unproven.

Current stage as of2026-11-08T07:11:47Z: complete. Exactly one competitive POST
returned201/submission41665776; accepted source matches the candidate SHA256.
Final ranking snapshot382/989Gold,100%,in_progress=false;95/95 logs audited,
41 wins/54 losses and zero technical failures. See REPORT.md and audit-final.json.
No rollback occurred. API client236 exited; no scheduled continuation remains.
Credentials existed only in process memory; no token, device code, approval code
or authorization URL is stored here. Do not repeat the POST or resume research.

Update2026-11-08T06:45:59Z: the first device code expired without approval
(official auth_poll returned expired_token). On explicit request, exec234 was
closed with exit0 and a new flow started in exec236. No submission was made.

The predeclared workflow follows. After approval: fresh challenge/limits/progress/submissions GETs; submit the exact
candidate once; save the accepted submission ID and download its source to verify
the hash. If a POST response is ambiguous, inspect current submissions before
any retry. Monitor ranking to completion and audit the resulting battle logs,
separating technical failures from losses. Compare with the recorded old bot
without presenting live rank changes as a controlled strength estimate.
Return a concise conclusion; any further model change or rollback needs a new
decision. No research restart or unrelated automation.
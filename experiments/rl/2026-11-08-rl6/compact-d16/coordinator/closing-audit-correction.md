# Post-stop audit correction

8 November 2026, before the second independent closing audit.

The first invocation of `closing_audit.py` ended with exit1; its original
`final-stop-audit.json` is preserved. It incorrectly assumed that no opponent
errors occurred and that all656 games were eligible for Java replay. The actual
second-block report has235/236 included games, excluding
`control-vs-lacoz-seed40013-seat0` because of the opponent's engine failure.
The candidate's separate emergency-WAIT game is engine-valid and **is** included.

Only the additional post-stop auditor was corrected: retain opponent-error rows
in raw/all-games data, bind the exact replay excluded set, sum replay transitions
only for included games, and require655/656 total inclusion plus one opponent
failure. The second report has a new filename. The six prospective parent
modules, candidate, original logs, frozen analyzer and all gates are unchanged.
No game was rerun. This was an audit assumption error, not a new bot failure.
# Platform runtime diagnosis, before candidate2

9 November2026. Evidence: actual submitted league3m source199c6a2d and actual
D16 sourceaba2d6f2, plus official test logs918842926/918843981 supplied by the
coordinator. No platform call in this lane.

## Verified facts

Both actual sources contain exactly the same optimized `FastNetwork` definition
from code/rl/export/inference.hpp: input-major transposed weights, independent
output-neuron inner loop, unchanged per-neuron sum order. The original header is
an exact substring of league3m; its exact token-preserving minification is a
substring of D16. D16 did not revert to the old scalar kernel.

The deployed league3m contains this prelude, but the v6/v7 D16 amalgamation omits it:

```cpp
#if defined(__GNUC__) && !defined(__clang__)
#pragma GCC optimize("O3")
#endif
```

Local builds explicitly used Apple clang17 `-O3`; this omission was therefore
invisible locally. Actual platform compiler flags are UNKNOWN. Missing source-
level optimization is a strong hypothesis, not yet an isolated causal result.

Official first two D16 tests:43turns, search.complete0 on every turn, selected0,
optional stopped1, mandatory baseline completed, no official errors/timeouts.
Aggregate measured forward cost73.7–84.1us/call versus local3540turn median
2.0651us/call. This cross-host ratio is descriptive, not a controlled speedup.
Feature/decoder costs are also much larger; a whole-program optimization issue
fits better than a new weight-decoding cost, which occurs only at startup.

Captainseb turn14 has618forwards: forward47.331368ms, features22.517249ms,
baseline71.445912ms, through-flush71.5998ms. It is NOT first-turn startup.
Turns12/13 are also >50ms internally. Official logs nevertheless record no
timeout; internal wall time is not interchangeable with platform-charged CPU.
The precise accounting difference remains UNKNOWN, and these observations are
retained as a material performance concern.

Local search did run:491nonbaseline selected turns among3540candidate outputs
in the incomplete359-game final, with zero candidate emergencies/errors. The
final stopped because the unchanged control timed out, not because D16 failed.
That does not establish successful search transfer to the platform.

## One minimal prospective test

Candidate2 adds only the exact guarded GCCO3 prelude above, copied from the
protected submitted league3m. No fast-math, target instruction set, reassociation,
weights, loop order, budget, precision, response model or telemetry changes.
Preserve candidate1/freeze/raw/STOP. Under the same local clang-O3, verify exact
decoded weights, old-fixture unlimited/full-stream equality and forced/partial
prefix contracts. Then coordinator tests candidate2 on the same three official
boss/Captainseb/selfplay maps. Check actual completed evaluations and nonbaseline
actions, useful baseline and zero official technical errors; do not merely count
compilation acceptance or raise16ms to manufacture success.

No further runtime fix is automatically authorized. Original1200-game strength
gate remains incomplete/false; no new large local final is part of this test.
# Second-block decision, 2026-11-08

Recorded after the verified first full-development panel, before any second
block is started. This is adaptive development, not independent final evidence.

The four-candidate panel completed2,320 games on40 maps. There were no own
failures and two Lacoz technical outcomes, excluded from paired comparisons.
B2,000,416 leads under the frozen primary/tie rule:60/80 Lacoz,77/80 new khoufou,
76/80 old khoufou,76/80v6,77/80BC,57/80 directly against the original base.
Its equal-weight external paired gain is4.25pp, positive against all five
opponents; individual confidence intervals still include zero. A1,501,957
has3.50pp external gain, with Lacoz-3.75pp and gains against the other four.

These broad point gains justify one additional short block on each independent
trajectory, resumed from its own latest complete checkpoint. The trainer,
reward, sampler and all12 frozen training sources remain unchanged. Latest
mutable output files are backed up with hashes before resume; immutable saved
snapshots and first-block evidence remain in place.

Each new block adds at most2M target decisions and120 training minutes, subject
to the original8M/8-hour per-seed ceiling and02:00UTC9Nov research cutoff.
The cumulative minute cap is previous elapsed time plus120 minutes, not240 by
default. A rollout can cross the decision target by its normal small batch size.
Stages remain serial: A train/average/export/screen/verification, then B, then
full40-map development. There is no concurrent timed evaluation or training.

Screen four new raw snapshots and a nearby average as before, also replaying
the previous full-panel champion from that seed. Advance that incumbent plus
the best admissible new challenger, at most two per seed. This prevents a cheap
12-map screen from silently discarding an established40-map development leader.
An incumbent failing the screen safeguards stops the driver for inspection.
Selection of the eventual full-panel winner still uses the original primary
metric, safeguards and earlier/simpler one-point tie preference.

After this block, more training requires a measured improvement over retained
incumbents in the full panel, not merely extra training steps or self-play wins.
The driver cannot automatically begin a third block. The search pilot is closed
as not_confirmed; no search-generated teacher training is authorized by its
inconclusive result. Reserved final maps40001--40100 remain unopened. No spend,
publication, submission or selected-policy change is performed.
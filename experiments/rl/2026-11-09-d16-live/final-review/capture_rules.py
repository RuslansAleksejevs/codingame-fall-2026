#!/usr/bin/env python3
"""Extract public source evidence without executing downloaded JavaScript."""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--rules-module', type=Path, required=True)
parser.add_argument('--api-reference', type=Path, required=True)
args = parser.parse_args()
raw = args.rules_module.read_text()
match = re.search(r"JSON\.parse\(('(?:\\.|[^'])*')\)", raw)
assert match, 'Expected public English rules translation'
rules = json.loads(ast.literal_eval(match.group(1)))['rules']
assert rules['TITLE'] == 'Contest rules' and 'ART16' in rules
api = args.api_reference.read_text()
start = api.index('### POST /challenges/{public_id}/submissions')
end = api.index('### GET /games/{game_id}', start)
public = json.loads((HERE / 'challenge-public.json').read_text())['challenge']
description = json.loads(public['descriptionJson'])
result = {
    'extracted_at': datetime.now(timezone.utc).isoformat(),
    'classification': 'SOURCE_VERIFIED',
    'scope': 'Fresh public source retrieval; no authenticated leaderboard result',
    'sources': {
        'general_rules': {'url': 'https://www.codingame.com/rules',
                          'loaded_asset': 'https://static.codingame.com/3177.5523193c.js',
                          'asset_sha256': hashlib.sha256(args.rules_module.read_bytes()).hexdigest()},
        'api': {'url': 'https://www.codingame.com/api/v1/docs/api',
                'sha256': hashlib.sha256(args.api_reference.read_bytes()).hexdigest()},
        'contest': {'url': 'https://www.codingame.com/contests/fall-challenge-2026',
                    'read_only_rpc': 'POST https://www.codingame.com/services/Challenge/findWorldCupByPublicId',
                    'public_id': 'fall-challenge-2026',
                    'saved_response_sha256': hashlib.sha256((HERE / 'challenge-public.json').read_bytes()).hexdigest()},
    },
    'general_rules': rules,
    'submission_ranking_api_excerpt': api[start:end],
    'contest_faq': description['howTo'],
    'contest_api_invitation': description['textBelowDateInHeader'],
    'contest_prizes': {'prizes': description.get('prizes'), 'items': description.get('prizesItems')},
    'interpretation_boundary': 'General question/test-case rules are not a precise description of the Bot Programming arena. The blanket assistance prohibition conflicts with the explicit contest/API invitation; no legal precedence or final-reranking algorithm is inferred.',
}
with (HERE / 'rules-snapshot.json').open('x') as stream:
    json.dump(result, stream, indent=2, ensure_ascii=False)
    stream.write('\n')
print(json.dumps({'saved': 'rules-snapshot.json', 'articles': len(rules)-1,
                  'api_excerpt_characters': len(api[start:end])}))
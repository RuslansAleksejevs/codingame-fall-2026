"""Reproducible minimal patch of the exact b9 package; preserve payload verbatim."""
import platform
from common import *

codec = module('d16_old_codec', V6CODE / 'codec.py')

def replace_once(text, old, new):
    assert text.count(old) == 1, ('Patch context count', old[:100], text.count(old))
    return text.replace(old, new)

def trimmed(source):
    return '\n'.join(s for s in source.splitlines() if not s.startswith('#pragma') and not s.startswith('#include "')) + '\n'

def patched_search():
    old = (V5CODE / 'search.hpp').read_text(); new = old
    edits = [
        ('int emergency=0, forwards=0, choices=0, checks=0;', 'int emergency=0, forwards=0, choices=0, checks=0, baseline_complete=0;'),
        ('<<",\\\"baseline_us\\\":"<<baseline_us', '<<",\\\"baseline_complete\\\":"<<baseline_complete<<",\\\"baseline_us\\\":"<<baseline_us'),
        ('Stats stats;', 'Stats stats;\n    bool completing_baseline=false;'),
        ('if((limit_ms>0 && us(origin)>=limit_ms*1000) ||\n           (forward_cap>0 && stats.forwards>=forward_cap))throw Stop{};', 'if(!completing_baseline && ((limit_ms>0 && us(origin)>=limit_ms*1000) ||\n           (forward_cap>0 && stats.forwards>=forward_cap)))throw Stop{};'),
        ('baseline="WAIT";selected_plan="WAIT";', 'baseline="WAIT";selected_plan="WAIT";completing_baseline=true;'),
        ('selected_plan=baseline;stats.generated=1;', 'completing_baseline=false;stats.baseline_complete=1;\n            selected_plan=baseline;stats.generated=1;'),
    ]
    for a, b in edits: new = replace_once(new, a, b)
    return old, new, edits

def main():
    guard(); target = OUT / 'package-attempt1'; target.mkdir(exist_ok=True)
    build_dir().mkdir(parents=True, exist_ok=True)
    original = V6 / 'package-attempt2/b9/bot.cpp'
    source = original.read_text(); old, new, edits = patched_search()
    source = replace_once(source, codec.minify(trimmed(old)).strip(), codec.minify(trimmed(new)).strip())
    source = replace_once(source, '<<",\\\"restore_us\\\":"<<restore_us', '<<",\\\"optional_us\\\":"<<std::max(0.,plan_us-search.stats.baseline_us)<<",\\\"restore_us\\\":"<<restore_us')
    cpp = target / 'bot.cpp'
    for path, value in [(cpp, source), (target / 'search-readable.hpp', new)]:
        if path.exists(): assert path.read_text() == value
        else:
            with path.open('x') as f: f.write(value)
    units = len(source.encode('utf-16-le')) // 2
    assert units <= 98000, units
    for name, flags in [('candidate', []), ('diagnostic', ['-DD16_DIAGNOSTIC']), ('dump', ['-DD16_WEIGHT_DUMP'])]:
        run(['clang++', '-std=c++17', '-O3', '-Wall', '-Wextra', '-Wpedantic', *flags, rel(cpp), '-o', rel(build_dir() / name)], 'compile-' + (sys.argv[1] if len(sys.argv)>1 else 'attempt1') + '-' + name, 180)
    decoded = subprocess.run([str(build_dir() / 'dump')], capture_output=True, timeout=20)
    expected = (V6 / 'package-attempt2/b9/expected-f32.bin').read_bytes()
    assert decoded.returncode == 0 and decoded.stdout == expected
    oldapi = '\n'.join(s for s in (V5CODE / 'api.cpp').read_text().splitlines() if not s.startswith('#include'))
    # Reuse exact hidden-state/legal/complete-prefix contracts, with sampled helper.
    oldsearch = (ROOT / 'code/rl/search/search.hpp').read_text()
    begin = oldsearch.index('std::string sampled('); opening = oldsearch.index('{', begin); depth = 1; end = opening + 1
    while depth: depth += (oldsearch[end] == '{') - (oldsearch[end] == '}'); end += 1
    contract = (V5CODE / 'contracts.cpp').read_text().replace('#include "api.cpp"', '')
    api = '#define main packaged_main\n#include "' + rel(cpp) + '"\n#undef main\nnamespace searchpilot{' + oldsearch[begin:end] + '}\n' + oldapi + contract
    api_path = target / 'api.cpp'
    with api_path.open('x') as f: f.write(api)
    run(['clang++', '-std=c++17', '-O3', '-shared', '-fPIC', '-pthread', '-I.', rel(api_path), '-o', rel(build_dir() / 'candidate.dylib')], 'compile-api', 180)
    manifest = {'as_of': now(), 'passed': True, 'source': rel(cpp), 'source_sha256': sha(cpp), 'source_utf16': units, 'source_bytes': cpp.stat().st_size, 'precision_bits': 9, 'unique_networks': 4, 'decoded_bytes': len(expected), 'decoded_sha256': hashlib.sha256(decoded.stdout).hexdigest(), 'codec_exact': True, 'edits': edits, 'optional_limit_ms': 16, 'forward_cap': 20000, 'baseline_policy': 'Mandatory completed greedy; same origin and cumulative forwards; optional-only stopping', 'sources': sources(), 'protected': guard(), 'binaries': {rel(p): sha(p) for p in build_dir().iterdir() if p.is_file()}, 'versions': {'python': sys.version, 'machine': platform.machine(), 'compiler': subprocess.run(['clang++', '--version'], capture_output=True, text=True).stdout}, 'budget': budget(), 'external_spend': 0}
    save(OUT / 'package.json', manifest); print(json.dumps(manifest), flush=True)

if __name__ == '__main__': main()
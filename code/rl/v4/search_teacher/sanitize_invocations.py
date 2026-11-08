"""Redact host path prefixes in completed, redundant per-game launch specs."""
import json
from pathlib import Path
from common import OUT, ROOT, now, relative, save, sha


def clean(value):
    if isinstance(value,str):return value.replace(str(ROOT),'${PROJECT_ROOT}').replace(str(Path.home()),'${HOME}')
    if isinstance(value,list):return [clean(v) for v in value]
    if isinstance(value,dict):return {k:clean(v) for k,v in value.items()}
    return value


def main():
    assert (OUT/'teacher-decision.json').exists(), 'Do not rewrite invocation files while panels are running'
    changes=[]
    for path in sorted(OUT.glob('*/*-seed*-seat*-spec.json')):
        before=sha(path);value=json.loads(path.read_text());sanitized=clean(value)
        if value==sanitized:continue
        path.write_text(json.dumps(sanitized,indent=2)+'\n')
        changes.append({'path':relative(path),'original_sha256':before,'redacted_sha256':sha(path)})
    report={'as_of':now(),'rewritten_specs':len(changes),'changes':changes,
            'method':'Only absolute project/home prefixes replaced with placeholders; results, inputs, sources and logical panel specs unchanged.',
            'records_deleted':False}
    save(OUT/'invocation-redaction.json',report)
    print(json.dumps({'rewritten_specs':len(changes),'records_deleted':False}))


if __name__=='__main__':main()
"""Capture a finite stage's command and terminal output inside the lease."""
from common import *
name=sys.argv[1]
assert name in ('contracts','regression','development','analyze','final_audit','freeze') or name.startswith('confirm')
script=name if name in ('contracts','analyze','final_audit','freeze') else 'panel'
suffix=('-'+sys.argv[2]) if script in ('analyze','final_audit','freeze') else ''
run([sys.executable,'-B',CODE/(script+'.py'),*(([name] if script=='panel' else [])+sys.argv[2:])],name+suffix+'-run',1460)
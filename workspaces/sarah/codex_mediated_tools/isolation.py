"""macOS outer-process research-path restriction; probes never call a model."""
import json
import subprocess
import sys
from pathlib import Path

def seatbelt_profile(protected_paths):
    paths=sorted({str(Path(p).resolve())for p in protected_paths})
    if not paths or '/'in paths:raise ValueError('Specific protected paths required')
    filters=' '.join('(subpath '+json.dumps(p)+')'for p in paths)
    return '(version 1)\n(allow default)\n(deny file-read-data '+filters+')\n(deny file-write* '+filters+')\n'

def probe(profile,protected,alias,public):
    script='''import pathlib,sys
p,a,c=map(pathlib.Path,sys.argv[1:])
assert c.read_text()=="public"
for x in (p,a):
 try:x.read_text()
 except PermissionError:pass
 else:raise SystemExit(2)
try:p.write_text("changed")
except PermissionError:pass
else:raise SystemExit(3)
print("PROBE_OK")
'''
    result=subprocess.run(['/usr/bin/sandbox-exec','-p',profile,sys.executable,'-c',script,str(protected),str(alias),str(public)],capture_output=True,text=True,timeout=20)
    if result.returncode or result.stdout.strip()!='PROBE_OK':raise RuntimeError('OS_ISOLATION_PROBE_FAILED: '+result.stderr[-1200:])
    return {'public_read':True,'protected_read_denied':True,'alias_read_denied':True,'protected_write_denied':True}

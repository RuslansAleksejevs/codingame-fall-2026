"""Record installed versions without importing training frameworks or hardware load."""
import importlib.metadata
import json
import platform
import subprocess
from common import OUT, ROOT, now, save


def main():
    package_versions={}
    for name in ('torch','numpy','scipy'):
        try:package_versions[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:package_versions[name]='not installed in this interpreter'
    hardware={}
    for key in ('machdep.cpu.brand_string','hw.memsize'):
        process=subprocess.run(['sysctl','-n',key],capture_output=True,text=True)
        hardware[key]=process.stdout.strip() if process.returncode==0 else 'UNKNOWN'
    lacoz=subprocess.run([str(ROOT/'code/arena/.venv-lacoz/bin/python'),'-B','-c',
        'import importlib.metadata,json,platform; print(json.dumps({"python":platform.python_version(),"numpy":importlib.metadata.version("numpy"),"scipy":importlib.metadata.version("scipy")}))'],
        capture_output=True,text=True,check=True)
    result={'as_of':now(),'classification':'PROJECT_REPORTED','python':platform.python_version(),
            'os':platform.system(),'os_release':platform.release(),'machine':platform.machine(),
            'packages':package_versions,'hardware':hardware,'new_installation':False,
            'lacoz_environment':json.loads(lacoz.stdout),
            'external_spend':0,'note':'Read-only installed metadata, no framework benchmark.'}
    save(OUT/'environment.json',result);print(json.dumps(result,indent=2))


if __name__=='__main__':main()
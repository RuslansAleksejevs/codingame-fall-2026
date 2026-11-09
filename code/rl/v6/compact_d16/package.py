"""Static-only precision selection; no game outcomes are read by this stage."""
import platform
import subprocess
import numpy as np
from common import *
from codec import load,encode,flat,text,payload,minify


def function(source,signature):
    start=source.index(signature);opening=source.index('{',start);depth=1;end=opening+1
    while depth:
        depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[start:end]+'\n'


def trimmed(source):
    return '\n'.join(line for line in source.splitlines() if not line.startswith('#pragma') and not line.startswith('#include "'))+'\n'


def assemble():
    spans={}
    def source(path):
        path=ROOT/path;value=path.read_text();spans[rel(path)]=sha(path);return value
    simulator=trimmed(source('code/rl/sim/simulator.hpp'))
    policy=source('code/rl/models/policy.hpp')
    policy=trimmed(policy[:policy.index('inline std::vector<Group> labels')])+'struct Network{std::vector<int> dims;std::vector<std::vector<float>> weights,bias;};}\n'
    inference=trimmed(source('code/rl/export/inference.hpp'))
    oldsearch=source('code/rl/search/search.hpp')
    helpers='namespace searchpilot{'+function(oldsearch,'rl::State clone(')+function(oldsearch,'unsigned long long state_seed(')+'}\n'
    league=source('code/rl/league/rollout_league.cpp')
    value='namespace league{'+function(league,'std::array<float,FEATURES> value_features(').replace('std::array<float,FEATURES>','std::array<float,rl::FEATURES>')+'}\n'
    embedded=source(rel(CODE/'embedded.hpp'))
    search=trimmed(source('code/rl/v5/deadline_search/search.hpp'))
    oldmain=source('code/rl/search/bot.cpp')
    ordering=function(oldmain,'int absolute_player(')+function(oldmain,'rl::State absolute_view(')
    io=source('code/rl/v5/deadline_search/io.hpp');io=io[io.index('namespace deadline {'):]
    main=source('code/rl/v5/deadline_search/bot.cpp');main=main[main.index('int main('):]
    main=main.replace('    if(argc<6)return 1;','''#ifdef D16_WEIGHT_DUMP
    for(const auto& net:packed::networks())for(size_t l=0;l<net.weights.size();++l){
        std::fwrite(net.weights[l].data(),4,net.weights[l].size(),stdout);
        std::fwrite(net.bias[l].data(),4,net.bias[l].size(),stdout);
    }
    return 0;
#endif''')
    main=main.replace('deadline::Search search(argv[1],argv[2],argv[3],argv[4],argv[5]);','deadline::Search search("0","1","0","2","3");')
    main=main.replace('    int proposals=argc>6?std::stoi(argv[6]):4;\n    double budget=argc>7?std::stod(argv[7]):16;', '''    int proposals=4,cap=20000;double budget=16;
#ifdef D16_DIAGNOSTIC
    if(argc>1)budget=std::stod(argv[1]);
    if(argc>2)cap=std::stoi(argv[2]);
    if(argc>3)proposals=std::stoi(argv[3]);
#endif''')
    main=main.replace('budget>0?20000:0','cap')
    prelude='#include <chrono>\n#include <random>\n#include <iomanip>\n#include <iostream>\n#include <cstdio>\n#include <cstring>\n'
    result=minify(prelude+simulator+policy+inference+helpers+value+embedded+search+ordering+io+main)
    return result,spans


def emit(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:f.write(value)


def compile_one(source,target,name,flags=()):
    run(['clang++','-std=c++17','-O3','-Wall','-Wextra','-Wpedantic',*flags,rel(source),'-o',rel(target)],'attempt2/'+name,120)


def main():
    guard();base=OUT/'package-attempt2';base.mkdir(exist_ok=False);build=build_dir();build.mkdir(exist_ok=False)
    skeleton,spans=assemble();emit(base/'skeleton.cpp',skeleton)
    networks=[load(path) for path in WEIGHTS];attempts=[];selected=None
    for width in (12,11,10,9,8,32):
        data,restored,error=encode(networks,width)
        source=skeleton.replace('PACKED_WIDTH',str(width)).replace('PACKED_BYTES',str(len(data))).replace('PACKED_PAYLOAD',payload(data))
        directory=base/f'b{width}';directory.mkdir();cpp=directory/'bot.cpp';emit(cpp,source)
        expected=flat(restored)
        with (directory/'expected-f32.bin').open('xb') as f:f.write(expected)
        for i,layers in enumerate(restored):
            emit(directory/f'weights{i}.txt',text(layers));assert flat([load(directory/f'weights{i}.txt')])==flat([layers])
        count=len(source.encode('utf-16-le'))//2
        row={'width':width,'source_utf16':count,'source_bytes':len(source.encode()),'source_sha256':sha(cpp),'payload_bytes':len(data),'fits':count<=98000,'quantization_error':error}
        # Every size attempt is retained; oversized candidates cannot be selected.
        if count<=98000 or width==32:
            dump=build/f'dump-b{width}';compile_one(cpp,dump,f'compile-dump-b{width}',['-DD16_WEIGHT_DUMP'])
            start=time.monotonic();result=subprocess.run([str(dump)],capture_output=True,timeout=10)
            with (directory/'decoded-f32.bin').open('xb') as f:f.write(result.stdout)
            save(directory/'codec.json',{'returncode':result.returncode,'stderr':result.stderr.decode(),'bytes':len(result.stdout),'expected_sha256':hashlib.sha256(expected).hexdigest(),'decoded_sha256':hashlib.sha256(result.stdout).hexdigest(),'exact':result.stdout==expected,'seconds':time.monotonic()-start})
            assert result.returncode==0 and result.stdout==expected,('codec',width)
            row.update(compiled=True,codec_exact=True)
            if selected is None and width!=32:selected=width
        else:row.update(compiled=False,codec_exact=None,reason='Full source exceeds the fixed98000UTF16 selection limit')
        attempts.append(row);save(directory/'result.json',row);print(json.dumps(row),flush=True)
    assert selected is not None,'No declared precision fits'
    chosen=base/f'b{selected}'/'bot.cpp'
    compile_one(chosen,build/'candidate','compile-candidate')
    compile_one(chosen,build/'candidate-diagnostic','compile-candidate-diagnostic',['-DD16_DIAGNOSTIC'])
    compile_one(base/'b32/bot.cpp',build/'fp32-diagnostic','compile-fp32-diagnostic',['-DD16_DIAGNOSTIC'])
    save(OUT/'package-attempt2.json',{'as_of':now(),'passed':True,'selected_width':selected,'selection':'Highest precision12..8 satisfying98000UTF16, compilation and exact decoder; no game results read','attempts':attempts,'source':rel(chosen),'source_sha256':sha(chosen),'source_utf16':len(chosen.read_text().encode('utf-16-le'))//2,'dependencies':spans,'sources':sources(),'protected':guard(),'binaries':{rel(p):sha(p) for p in build.iterdir() if p.is_file()},'versions':{'python':sys.version,'numpy':np.__version__,'machine':platform.machine(),'compiler':subprocess.run(['clang++','--version'],capture_output=True,text=True).stdout},'budget':budget(),'external_spend':0})


if __name__=='__main__':main()
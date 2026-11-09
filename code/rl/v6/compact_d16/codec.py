"""Deterministic symmetric row quantization and a checked bitstream codec."""
import re
import struct
import numpy as np

DIMS=(128,128,64,1)


def load(path):
    tokens=path.read_text().split();assert tokens[:6]==['TRYANGLE_MLP_V1','3','128','128','64','1']
    values=np.asarray(list(map(float,tokens[6:])),dtype=np.float32);assert len(values)==24833 and np.isfinite(values).all()
    layers=[];offset=0
    for inputs,outputs in zip(DIMS[:-1],DIMS[1:]):
        w=values[offset:offset+inputs*outputs].reshape(outputs,inputs).copy();offset+=inputs*outputs
        b=values[offset:offset+outputs].copy();offset+=outputs;layers.append((w,b))
    assert offset==len(values);return layers


class Bits:
    def __init__(self):self.data=bytearray();self.accumulator=0;self.count=0
    def put(self,value,width):
        assert 0<=value<(1<<width);self.accumulator|=int(value)<<self.count;self.count+=width
        while self.count>=8:self.data.append(self.accumulator&255);self.accumulator>>=8;self.count-=8
    def f32(self,value):self.put(struct.unpack('<I',struct.pack('<f',float(value)))[0],32)
    def finish(self):
        if self.count:self.data.append(self.accumulator&255);self.count=0;self.accumulator=0
        return bytes(self.data)


def encode(networks,width):
    stream=Bits();restored=[];errors=[]
    for layers in networks:
        decoded=[]
        for weights,bias in layers:
            if width==32:
                for row in weights:
                    for value in row:stream.f32(value)
                dw=weights.copy()
            else:
                qmax=(1<<(width-1))-1;scales=np.max(np.abs(weights),axis=1)/np.float32(qmax)
                scales=np.where(scales==0,np.float32(1),scales).astype(np.float32)
                q=np.clip(np.rint(weights/scales[:,None]),-qmax,qmax).astype(np.int32)
                dw=(q.astype(np.float32)*scales[:,None]).astype(np.float32)
                for scale in scales:stream.f32(scale)
                for value in q.ravel():stream.put(int(value)&((1<<width)-1),width)
            for value in bias:stream.f32(value)
            decoded.append((dw,bias.copy()));errors.extend(np.abs(dw-weights).ravel().tolist())
        restored.append(decoded)
    return stream.finish(),restored,{'maximum_weight_error':max(errors),'mean_weight_error':float(np.mean(errors))}


def flat(networks):return b''.join(np.concatenate([a.ravel() for layer in layers for a in layer]).astype('<f4').tobytes() for layers in networks)


def text(layers):
    return 'TRYANGLE_MLP_V1 3\n128 128 64 1\n'+'\n'.join(' '.join(format(float(x),'.9g') for x in a.ravel()) for layer in layers for a in layer)+'\n'


def symbols(data):
    result=[];value=bits=0
    for byte in data:
        value=(value<<8)|byte;bits+=8
        while bits>=15:bits-=15;result.append(chr(0x4000+((value>>bits)&32767)))
        value&=(1<<bits)-1
    if bits:result.append(chr(0x4000+(value<<(15-bits))))
    return ''.join(result)


def payload(data):
    s=symbols(data)
    return ',\n'.join('R"CGW('+ '\n'.join(s[i:i+256] for i in range(start,min(start+12800,len(s)),256))+')CGW"' for start in range(0,len(s),12800))


def tokens(source):
    # Preserve literals and complete preprocessor lines; comments are trivia.
    pattern=re.compile(r'(?P<space>\s+)|(?P<line>//[^\n]*)|(?P<comment>/\*[\s\S]*?\*/)|(?P<pre>\#[^\n]*(?:\\\n[^\n]*)*)|(?P<string>"(?:\\[\s\S]|[^"\\])*"|\'(?:\\[\s\S]|[^\'\\])*\')|(?P<identifier>[A-Za-z_]\w*)|(?P<number>(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?[A-Za-z0-9_]*)|(?P<operator>>>=|<<=|->\*|\.\.\.|::|->|\+\+|--|<<|>>|&&|\|\||[+*/%&|^!=<>-]=|\.\*|.)')
    result=[];offset=0
    for match in pattern.finditer(source):
        assert match.start()==offset;offset=match.end()
        if match.lastgroup not in ('space','line','comment'):result.append((match.lastgroup,match.group()))
    assert offset==len(source);return result


def minify(source):
    original=tokens(source);out=[];previous=None
    operators={'//','/*','++','--','<<','>>','&&','||','+=','-=','*=','/=','%=','&=','|=','^=','==','!=','<=','>=','->','::','##','.*','..'}
    for kind,value in original:
        if kind=='pre':out.extend(['\n',value,'\n']);previous=None;continue
        if previous:
            pk,pv=previous
            if (pk in ('identifier','number') and kind in ('identifier','number')) or pv[-1]+value[0] in operators or (pk=='number' and value[0]=='.'):
                out.append(' ')
        out.append(value);previous=(kind,value)
    result=''.join(out)+'\n';assert tokens(result)==original,'Minifier changed the C++ token sequence'
    return result
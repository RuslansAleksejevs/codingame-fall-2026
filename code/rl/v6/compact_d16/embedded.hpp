// Storage-only adapter. The inference kernel and D16 implementation are unchanged.
namespace packed {
constexpr int width=PACKED_WIDTH, byte_count=PACKED_BYTES;
const char* pieces[]={PACKED_PAYLOAD};
struct Reader {
    std::vector<unsigned char> data;
    size_t position=0;
    unsigned long long pending=0;
    int bits=0;
    Reader(){
        unsigned long long word=0;int count=0;
        for(auto piece:pieces){
            auto s=reinterpret_cast<const unsigned char*>(piece);
            while(*s){
                if(*s=='\n'){++s;continue;}
                if((s[0]&240)!=224||(s[1]&192)!=128||(s[2]&192)!=128)
                    throw std::runtime_error("Invalid packed UTF8");
                unsigned int code=((s[0]&15)<<12)|((s[1]&63)<<6)|(s[2]&63);s+=3;
                if(code<0x4000||code>0xbfff)throw std::runtime_error("Invalid packed symbol");
                word=(word<<15)|(code-0x4000);count+=15;
                while(count>=8){count-=8;data.push_back((word>>count)&255);}
                word&=(1ULL<<count)-1;
            }
        }
        if(data.size()<byte_count)throw std::runtime_error("Truncated packed weights");
        data.resize(byte_count);
    }
    unsigned int get(int size){
        while(bits<size){if(position==data.size())throw std::runtime_error("Truncated bits");
            pending|=static_cast<unsigned long long>(data[position++])<<bits;bits+=8;}
        unsigned int value=pending&((1ULL<<size)-1);pending>>=size;bits-=size;return value;
    }
    float number(){unsigned int value=get(32);float result;std::memcpy(&result,&value,4);return result;}
};
const std::array<rl::Network,4>& networks(){
    static const auto loaded=[](){
        Reader reader;std::array<rl::Network,4> result;
        for(auto& net:result){
            net.dims={128,128,64,1};
            for(int l=0;l<3;++l){
                int n=net.dims[l],m=net.dims[l+1];
                net.weights.emplace_back(n*m);net.bias.emplace_back(m);
                std::vector<float> scales(m);
                if(width!=32)for(float& value:scales)value=reader.number();
                for(int j=0;j<m;++j)for(int k=0;k<n;++k){
                    float value;
                    if(width==32)value=reader.number();
                    else {unsigned int raw=reader.get(width);int q=static_cast<int>(raw);
                        if(raw&(1U<<(width-1)))q-=(1<<width);
                        value=static_cast<float>(q)*scales[j];}
                    if(!std::isfinite(value))throw std::runtime_error("Nonfinite weight");
                    net.weights[l][j*n+k]=value;
                }
                for(float& value:net.bias[l]){value=reader.number();if(!std::isfinite(value))throw std::runtime_error("Nonfinite bias");}
            }
        }
        if(reader.position!=byte_count||reader.pending)throw std::runtime_error("Unused packed bits");
        return result;
    }();
    return loaded;
}
}
namespace searchpilot {
struct Search {
    rl::Network actor,critic;
    std::array<rl::Network,3> enemies;
    std::unique_ptr<rl::FastNetwork> policy,value;
    std::array<std::unique_ptr<rl::FastNetwork>,3> responses;
    int depth,candidates;
    double budget_ms;
    Search(const char*,const char*,const char*,const char*,const char*,int horizon,int count,double budget)
        :depth(horizon),candidates(count),budget_ms(budget){
        const auto& data=packed::networks();actor=data[0];critic=data[1];
        int indices[3]={0,2,3};
        for(int i=0;i<3;++i){enemies[i]=data[indices[i]];responses[i]=std::make_unique<rl::FastNetwork>(enemies[i]);}
        policy=std::make_unique<rl::FastNetwork>(actor);value=std::make_unique<rl::FastNetwork>(critic);
    }
};
}
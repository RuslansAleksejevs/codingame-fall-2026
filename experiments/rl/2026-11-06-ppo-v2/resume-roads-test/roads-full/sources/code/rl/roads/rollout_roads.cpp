// Complete-episode self-play rollouts. BC rules, actor and decoder stay unchanged.
#include "policy.hpp"
#include <atomic>
#include <chrono>
#include <fstream>
#include <iomanip>
#include <mutex>
#include <random>
#include <thread>

namespace roads {
using roads_model::FEATURES;
using External=const char*(*)(int,int,int,const char*);
std::string observation(const roads_model::State&s,int p,bool initial) {
    std::ostringstream out;
    if(initial){out<<s.n<<'\n';for(int q=0;q<s.n;q++)out<<q<<' '<<s.x[q]<<' '<<s.y[q]<<'\n';}
    out<<s.score[p]<<' '<<s.score[1-p]<<'\n';
    for(int q=0;q<s.n;q++)out<<q<<' '<<s.u[p][q]<<' '<<s.u[1-p][q]<<'\n';
    std::vector<std::pair<int,int>> roads,links;
    for(int a=0;a<s.n;a++)for(int b=a+1;b<s.n;b++){
        if(s.adj[a][b])roads.push_back({a,b});else if(s.connectable(a,b))links.push_back({a,b});
    }
    out<<roads.size()<<'\n';for(auto[a,b]:roads)out<<a<<' '<<b<<'\n';
    out<<s.ts.size()<<'\n';for(auto&t:s.ts)out<<t->v[0]<<' '<<t->v[1]<<' '<<t->v[2]<<' '<<(t->owner<0?-1:t->owner==p?0:1)<<' '<<t->cap[p]<<' '<<t->cap[1-p]<<'\n';
    out<<links.size()<<'\n';for(auto[a,b]:links)out<<a<<' '<<b<<'\n';return out.str();
}
struct Trace {
    std::vector<std::array<float,FEATURES>> x;
    std::vector<int> counts, choices;
    std::array<float,FEATURES> value{};
    double logp=0, entropy=0;
};
std::array<float,FEATURES> value_features(const roads_model::Decoder&d) {
    std::array<float,FEATURES> out{};
    // Global context followed by permutation-invariant node pooling.
    auto base=d.features({2,0,0,nullptr});std::copy(base.begin(),base.begin()+16,out.begin());
    std::array<float,26> sum{},sq{},lo{},hi{};lo.fill(1e9);hi.fill(-1e9);
    for(int q=0;q<d.s.n;q++){auto f=d.node(q);for(int k=0;k<26;k++){sum[k]+=f[k];sq[k]+=f[k]*f[k];lo[k]=std::min(lo[k],f[k]);hi[k]=std::max(hi[k],f[k]);}}
    for(int k=0;k<26;k++){float mean=sum[k]/d.s.n;out[16+k]=mean;out[42+k]=hi[k];out[68+k]=lo[k];out[94+k]=std::sqrt(std::max(0.f,sq[k]/d.s.n-mean*mean));}
    int controls[3]{},empty=0,tied=0,edges=0,blocked=0;
    for(int q=0;q<d.s.n;q++){int o=d.s.owner(q);controls[o<0?2:o==d.p?0:1]++;empty+=d.s.u[0][q]+d.s.u[1][q]==0;tied+=d.s.u[0][q]==d.s.u[1][q]&&d.s.u[0][q]>0;for(int j=q+1;j<d.s.n;j++)edges+=d.s.adj[q][j];}
    for(auto&t:d.s.ts)blocked+=!t->cap[d.p];
    out[120]=controls[0]/50.f;out[121]=controls[1]/50.f;out[122]=controls[2]/50.f;out[123]=empty/50.f;out[124]=tied/50.f;out[125]=edges/100.f;out[126]=blocked/30.f;out[127]=1;
    return out;
}
std::string plan(const roads_model::Network&net,const roads_model::State&s,int player,std::mt19937_64&rng,double temperature,Trace*trace=nullptr) {
    roads_model::Decoder decoder(s,player,3);
    if(trace)trace->value=value_features(decoder);
    return decoder.run([&](const std::vector<roads_model::Candidate>&cs,const roads_model::Decoder&d){
        std::vector<std::array<float,FEATURES>> features;std::vector<double> logits;features.reserve(cs.size());logits.reserve(cs.size());
        double maxlog=-1e30;int best=0;
        for(int i=0;i<int(cs.size());i++){features.push_back(d.features(cs[i]));double logit=net.evaluate(features.back())/(temperature>0?temperature:1.);logits.push_back(logit);if(logit>maxlog){maxlog=logit;best=i;}}
        double sum=0;for(double&v:logits){v=std::exp(v-maxlog);sum+=v;}
        int choice=best;
        if(temperature>0){double u=std::generate_canonical<double,53>(rng)*sum;for(int i=0;i<int(logits.size());i++){if(u<logits[i]){choice=i;break;}u-=logits[i];}}
        if(trace){trace->logp+=std::log(logits[choice]/sum);for(double v:logits){double p=v/sum;if(p>0)trace->entropy-=p*std::log(p);}
            trace->counts.push_back(cs.size());trace->choices.push_back(choice);trace->x.insert(trace->x.end(),features.begin(),features.end());}
        return choice;
    });
}
struct Game {
    int map=0,kind=0,seat=0,pool=0,anchor_id=0,greedy_history=0,turns=0,winner=-1;
    unsigned long long seed=0;
    int score[2]{};
    std::vector<Trace> traces[2];
    std::vector<std::array<std::string,2>> actions;
    std::vector<std::string> states;
};
struct Collector {
    roads_model::Network actor,bc,anchor;
    External external=nullptr;
    std::vector<roads_model::Network> pool;
    std::vector<std::string> maps;
    std::vector<float> x,values,logps,entropies,rewards;
    std::vector<int> group_offsets,choices,turn_offsets,episode_offsets,game_ids,players;
    std::string error,stats,records;
    Collector(const char*weights){actor.load(weights);bc=actor;anchor=actor;pool.push_back(actor);}
    void set(const float*f){for(int l=0;l<int(actor.weights.size());l++){for(float&v:actor.weights[l])v=*f++;for(float&v:actor.bias[l])v=*f++;}}
    void collect(int count,int workers,unsigned long long seed,double temperature,int audit) {
        auto begin=std::chrono::steady_clock::now();std::vector<Game> games(count);std::atomic<int> next{0};std::mutex lock;error.clear();
        auto run=[&](int worker){while(true){int id=next++;if(id>=count)break;
            try{
                auto&g=games[id];g.seed=seed+0x9e3779b97f4a7c15ULL*(id+1);std::mt19937_64 rng(g.seed);
                g.map=rng()%maps.size();g.kind=id%8<4?0:id%8<6?1:id%8==6?2:external?3:2;g.seat=(id/8)%2;g.pool=rng()%pool.size();g.anchor_id=rng()%10;g.greedy_history=rng()%2;
                roads_model::State s;std::istringstream in(maps[g.map]);s.load(in);
                if(id<audit)g.states.push_back(s.json());
                while(!s.done){std::array<std::string,2> commands;
                    // No command is applied until both policies have read this same state.
                    for(int p=0;p<2;p++){
                        if(g.kind==0||p==g.seat){g.traces[p].emplace_back();commands[p]=plan(actor,s,p,rng,temperature,&g.traces[p].back());}
                        else if(g.kind==3){
                            std::string input=observation(s,p,s.turn==0);const char*answer=external(worker,id,s.turn,input.c_str());
                            if(!answer)throw std::runtime_error("External teacher callback failed");commands[p]=answer;
                        }else if(g.kind==1)commands[p]=(g.anchor_id==0?bc:anchor).act(s,p,2);
                        else commands[p]=plan(pool[g.pool],s,p,rng,g.greedy_history?0:temperature);
                    }
                    s.step(commands[0],commands[1]);if(s.parse_errors[0]||s.parse_errors[1])throw std::runtime_error("Generated invalid plan");
                    if(id<audit){g.actions.push_back(commands);g.states.push_back(s.json());}
                }
                if(g.kind==3&&!external(worker,id,-1,""))throw std::runtime_error("External teacher reset failed");
                g.turns=s.turn;for(int p=0;p<2;p++)g.score[p]=s.score[p];g.winner=s.score[0]>s.score[1]?0:s.score[1]>s.score[0]?1:-1;
            }catch(const std::exception&e){std::lock_guard<std::mutex> guard(lock);error=e.what();}
        }};
        std::vector<std::thread> threads;for(int k=0;k<workers;k++)threads.emplace_back(run,k);for(auto&t:threads)t.join();if(!error.empty())throw std::runtime_error(error);
        x.clear();values.clear();logps.clear();entropies.clear();rewards.clear();choices.clear();game_ids.clear();players.clear();
        group_offsets={0};turn_offsets={0};episode_offsets={0};
        size_t rows=0;for(auto&g:games)for(auto&ts:g.traces)for(auto&t:ts)rows+=t.x.size();x.reserve(rows*FEATURES);
        int kinds[4]{},wins[4]{},draws[4]{},turns=0;std::ostringstream rec;rec<<'[';
        for(int id=0;id<count;id++){
            auto&g=games[id];kinds[g.kind]++;wins[g.kind]+=g.winner==g.seat;draws[g.kind]+=g.winner<0;turns+=g.turns;
            for(int p=0;p<2;p++)if(!g.traces[p].empty()){
                for(size_t j=0;j<g.traces[p].size();j++){
                    auto&t=g.traces[p][j];for(auto&row:t.x)x.insert(x.end(),row.begin(),row.end());
                    for(int size:t.counts)group_offsets.push_back(group_offsets.back()+size);
                    choices.insert(choices.end(),t.choices.begin(),t.choices.end());turn_offsets.push_back(choices.size());
                    values.insert(values.end(),t.value.begin(),t.value.end());logps.push_back(t.logp);entropies.push_back(t.entropy);
                    float reward=j+1==g.traces[p].size()?(g.winner<0?0:g.winner==p?1:-1):0;
                    rewards.push_back(reward);game_ids.push_back(id);players.push_back(p);
                }
                episode_offsets.push_back(logps.size());
                std::vector<Trace>().swap(g.traces[p]);
            }
            if(id<audit){if(id)rec<<',';rec<<"{\"map_index\":"<<g.map<<",\"kind\":"<<g.kind<<",\"learner_seat\":"<<g.seat<<",\"seed\":\""<<g.seed<<"\",\"scores\":["<<g.score[0]<<','<<g.score[1]<<"],\"actions\":[";
                for(size_t j=0;j<g.actions.size();j++){if(j)rec<<',';rec<<"[\""<<g.actions[j][0]<<"\",\""<<g.actions[j][1]<<"\"]";}rec<<"],\"states\":[";
                for(size_t j=0;j<g.states.size();j++){if(j)rec<<',';rec<<g.states[j];}rec<<"]}";
            }
        }
        rec<<']';records=rec.str();double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();
        std::ostringstream o;o<<"{\"games\":"<<count<<",\"joint_turns\":"<<turns<<",\"controlled_decisions\":"<<logps.size()<<",\"groups\":"<<choices.size()<<",\"candidates\":"<<x.size()/FEATURES<<",\"feature_bytes\":"<<x.size()*sizeof(float)<<",\"seconds\":"<<seconds<<",\"pool_size\":"<<pool.size()<<",\"kinds\":[";
        for(int k=0;k<4;k++){if(k)o<<',';o<<"{\"games\":"<<kinds[k]<<",\"learner_seat_wins\":"<<wins[k]<<",\"draws\":"<<draws[k]<<'}';}o<<"]}";stats=o.str();
    }
};
static thread_local std::string error;
}
extern "C" {
void roads_set_external(void*p,roads::External callback){static_cast<roads::Collector*>(p)->external=callback;}
void roads_set_anchor(void*p,const float*f){auto*c=static_cast<roads::Collector*>(p);for(int l=0;l<int(c->anchor.weights.size());l++){for(float&v:c->anchor.weights[l])v=*f++;for(float&v:c->anchor.bias[l])v=*f++;}}
const char* roads_observation(void*p,int player,int initial){static thread_local std::string result;result=roads::observation(*static_cast<roads_model::State*>(p),player,initial);return result.c_str();}
void* roads_new(const char*weights){try{return new roads::Collector(weights);}catch(const std::exception&e){roads::error=e.what();return nullptr;}}
void roads_delete(void*p){delete static_cast<roads::Collector*>(p);}
const char* roads_error(){return roads::error.c_str();}
void roads_add_map(void*p,const char*map){static_cast<roads::Collector*>(p)->maps.emplace_back(map);}
void roads_set_actor(void*p,const float*f){static_cast<roads::Collector*>(p)->set(f);}
void roads_add_pool(void*p){auto*c=static_cast<roads::Collector*>(p);c->pool.push_back(c->actor);if(c->pool.size()>12)c->pool.erase(c->pool.begin());}
void roads_clear_pool(void*p){static_cast<roads::Collector*>(p)->pool.clear();}
int roads_collect(void*p,int games,int workers,unsigned long long seed,double temperature,int audit){try{static_cast<roads::Collector*>(p)->collect(games,workers,seed,temperature,audit);return 0;}catch(const std::exception&e){roads::error=e.what();return -1;}}
const char* roads_stats(void*p){return static_cast<roads::Collector*>(p)->stats.c_str();}
const char* roads_records(void*p){return static_cast<roads::Collector*>(p)->records.c_str();}
const float* roads_float(void*p,int which){auto*c=static_cast<roads::Collector*>(p);switch(which){case 0:return c->x.data();case 1:return c->values.data();case 2:return c->logps.data();case 3:return c->entropies.data();default:return c->rewards.data();}}
const int* roads_int(void*p,int which){auto*c=static_cast<roads::Collector*>(p);switch(which){case 0:return c->group_offsets.data();case 1:return c->choices.data();case 2:return c->turn_offsets.data();case 3:return c->episode_offsets.data();case 4:return c->game_ids.data();default:return c->players.data();}}
int roads_episodes(void*p){return int(static_cast<roads::Collector*>(p)->episode_offsets.size())-1;}
int roads_greedy_game(void*p,const char*map,int seat){try{auto*c=static_cast<roads::Collector*>(p);roads_model::State s;std::istringstream in(map);s.load(in);while(!s.done){std::string a=c->actor.act(s,seat,3),b=c->bc.act(s,1-seat,2);s.step(seat==0?a:b,seat==0?b:a);if(s.parse_errors[0]||s.parse_errors[1])throw std::runtime_error("Invalid selection plan");}return s.score[seat]>s.score[1-seat]?1:s.score[seat]<s.score[1-seat]?-1:0;}catch(const std::exception&e){roads::error=e.what();return -9;}}
const char* roads_feature_probe(void*ptr,int player){
    static thread_local std::string result;auto&s=*static_cast<rl::State*>(ptr);
    roads_model::Decoder current(s,player,3),original(s,player,2);
    std::vector<roads_model::Candidate> candidates;
    for(auto&t:s.ts)if(t->owner==player){auto cs=current.spend(t);candidates.insert(candidates.end(),cs.begin(),cs.end());}
    for(int a=0;a<s.n;a++)if(current.available[a]>0){candidates.push_back({0,a,a,nullptr});for(int b=0;b<s.n;b++)if(s.adj[a][b])candidates.push_back({1,a,b,nullptr});}
    std::ostringstream out;out<<std::setprecision(9)<<'[';bool first=true;
    for(auto&c:candidates){if(!first)out<<',';first=false;auto x=current.features(c),old=original.features(c);
        roads_model::Decoder command(s,player,3);command.choose(c);
        out<<"{\"kind\":"<<c.kind<<",\"action\":\""<<(command.output.empty()?"WAIT":command.output[0])<<"\",\"new\":[";
        for(int k=0;k<roads_model::FEATURES;k++){if(k)out<<',';out<<x[k];}out<<"],\"original\":[";
        for(int k=0;k<roads_model::FEATURES;k++){if(k)out<<',';out<<old[k];}out<<"]}";
    }
    out<<']';result=out.str();return result.c_str();
}
void* roads_net_new(const char*path){try{auto*n=new roads_model::Network();n->load(path);return n;}catch(...){return nullptr;}}
void roads_net_delete(void*p){delete static_cast<roads_model::Network*>(p);}
const char* roads_net_act(void*n,void*s,int player,int style){static thread_local std::string result;result=static_cast<roads_model::Network*>(n)->act(*static_cast<rl::State*>(s),player,style);return result.c_str();}
}

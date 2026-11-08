// Isolated adapter: imports existing rules, actor, trace and value features.
#include "../../league/rollout_league.cpp"
#include "../../sim/api.cpp"
#include "state.hpp"

namespace curriculum {
struct Collector:league::Collector {
    std::vector<rl::State> starts;
    explicit Collector(const char* weights):league::Collector(weights){}
    // schedule columns: ordinary map index, opponent (-1 current or pool index),
    // learner seat, restored start index (-1 ordinary). No hidden start sampling.
    void collect_curriculum(int count,int workers,unsigned long long seed,double temperature,int audit,const int*schedule) {
        auto begin=std::chrono::steady_clock::now();std::vector<league::Game> games(count);
        std::vector<int> start_turns(count),start_ids(count);std::atomic<int> next{0};std::mutex lock;error.clear();
        auto run=[&](int worker){while(true){int id=next++;if(id>=count)break;
            try {
                auto& g=games[id];g.seed=seed+0x9e3779b97f4a7c15ULL*(id+1);std::mt19937_64 rng(g.seed);
                g.map=schedule[id*4];g.pool=schedule[id*4+1];g.seat=schedule[id*4+2];int start=schedule[id*4+3];
                if(g.map<0||g.map>=int(maps.size())||g.pool < -2||g.pool>=int(pool.size())||g.seat<0||g.seat>1||start < -1||start>=int(starts.size())||(g.pool==-2&&!external))throw std::runtime_error("Invalid curriculum schedule");
                if(start>=0&&g.pool==-2)throw std::runtime_error("Stateful external opponent requires an ordinary start");
                g.kind=g.pool==-2?3:g.pool==-1?0:2;
                rl::State s;if(start>=0)s=clone(starts[start]);else{std::istringstream input(maps[g.map]);s.load(input);}
                start_turns[id]=s.turn;start_ids[id]=start;
                if(id<audit)g.states.push_back(snapshot(s));
                while(!s.done){std::array<std::string,2> commands;
                    // Both players observe the unchanged state before either plan executes.
                    for(int p=0;p<2;p++){
                        if(p==g.seat){g.traces[p].emplace_back();commands[p]=league::plan(actor,s,p,rng,temperature,&g.traces[p].back());}
                        else if(g.pool==-2){int relative=s.turn-start_turns[id];auto input=league::observation(s,p,relative==0);auto answer=external(worker,id,relative,input.c_str());if(!answer)throw std::runtime_error("External opponent failed");commands[p]=answer;}
                        else if(g.pool==-1)commands[p]=league::plan(actor,s,p,rng,temperature);
                        else commands[p]=pool[g.pool].act(s,p,2);
                    }
                    s.step(commands[0],commands[1]);if(s.parse_errors[0]||s.parse_errors[1])throw std::runtime_error("Generated invalid plan");
                    if(id<audit){g.actions.push_back(commands);g.states.push_back(snapshot(s));}
                }
                if(g.pool==-2&&!external(worker,id,-1,""))throw std::runtime_error("External reset failed");
                g.turns=s.turn-start_turns[id];for(int p=0;p<2;p++)g.score[p]=s.score[p];g.winner=s.score[0]>s.score[1]?0:s.score[1]>s.score[0]?1:-1;
            }catch(const std::exception& e){std::lock_guard<std::mutex> guard(lock);error=e.what();}
        }};
        std::vector<std::thread> threads;for(int w=0;w<workers;w++)threads.emplace_back(run,w);for(auto& t:threads)t.join();
        if(!error.empty())throw std::runtime_error(error);
        x.clear();values.clear();logps.clear();entropies.clear();rewards.clear();choices.clear();game_ids.clear();players.clear();
        group_offsets={0};turn_offsets={0};episode_offsets={0};std::ostringstream rec;rec<<'[';int total_turns=0,restored=0;
        for(int id=0;id<count;id++){
            auto& g=games[id];auto& traces=g.traces[g.seat];total_turns+=g.turns;restored+=start_ids[id]>=0;
            if(traces.empty())throw std::runtime_error("Empty learner episode");
            for(size_t j=0;j<traces.size();j++){
                auto& t=traces[j];for(auto& row:t.x)x.insert(x.end(),row.begin(),row.end());
                for(int size:t.counts)group_offsets.push_back(group_offsets.back()+size);
                choices.insert(choices.end(),t.choices.begin(),t.choices.end());turn_offsets.push_back(choices.size());
                values.insert(values.end(),t.value.begin(),t.value.end());logps.push_back(t.logp);entropies.push_back(t.entropy);
                rewards.push_back(j+1==traces.size()?(g.winner<0?0:g.winner==g.seat?1:-1):0);game_ids.push_back(id);players.push_back(g.seat);
            }
            episode_offsets.push_back(logps.size());
            if(id<audit){if(id)rec<<',';rec<<"{\"map_index\":"<<g.map<<",\"opponent\":"<<g.pool<<",\"learner_seat\":"<<g.seat<<",\"start_index\":"<<start_ids[id]<<",\"start_turn\":"<<start_turns[id]<<",\"seed\":\""<<g.seed<<"\",\"scores\":["<<g.score[0]<<','<<g.score[1]<<"],\"actions\":[";
                for(size_t j=0;j<g.actions.size();j++){if(j)rec<<',';rec<<"[\""<<g.actions[j][0]<<"\",\""<<g.actions[j][1]<<"\"]";}rec<<"],\"states\":[";
                for(size_t j=0;j<g.states.size();j++){if(j)rec<<',';rec<<g.states[j];}rec<<"]}";
            }
        }
        rec<<']';records=rec.str();double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();
        std::ostringstream out;out<<"{\"games\":"<<count<<",\"joint_turns\":"<<total_turns<<",\"controlled_decisions\":"<<logps.size()<<",\"groups\":"<<choices.size()<<",\"candidates\":"<<x.size()/rl::FEATURES<<",\"restored_games\":"<<restored<<",\"seconds\":"<<seconds<<",\"outcomes\":[";
        for(int id=0;id<count;id++){auto& g=games[id];if(id)out<<',';out<<'['<<g.pool<<','<<g.seat<<','<<start_ids[id]<<','<<(g.winner<0?0:g.winner==g.seat?1:-1)<<','<<g.turns<<']';}out<<"]}";stats=out.str();
    }
};
static thread_local std::string result;
}
extern "C" {
const char* curr_snapshot(void* ptr){curriculum::result=curriculum::snapshot(*static_cast<rl::State*>(ptr));return curriculum::result.c_str();}
void* curr_restore(const char* text){try{return new rl::State(curriculum::restore(text));}catch(const std::exception& e){curriculum::result=e.what();return nullptr;}}
const char* curr_error(){return curriculum::result.c_str();}
void* curr_new(const char* weights){try{return new curriculum::Collector(weights);}catch(const std::exception& e){curriculum::result=e.what();return nullptr;}}
void curr_delete(void* ptr){delete static_cast<curriculum::Collector*>(ptr);}
int curr_add_start(void* ptr,const char* text){try{auto* c=static_cast<curriculum::Collector*>(ptr);c->starts.push_back(curriculum::restore(text));return int(c->starts.size())-1;}catch(const std::exception& e){curriculum::result=e.what();return -1;}}
int curr_add_opponent(void* ptr,const char* weights){try{auto* c=static_cast<curriculum::Collector*>(ptr);rl::Network net;net.load(weights);c->pool.push_back(net);return int(c->pool.size())-1;}catch(const std::exception& e){curriculum::result=e.what();return -1;}}
int curr_collect(void* ptr,int count,int workers,unsigned long long seed,double temperature,int audit,const int* schedule){try{static_cast<curriculum::Collector*>(ptr)->collect_curriculum(count,workers,seed,temperature,audit,schedule);return 0;}catch(const std::exception& e){curriculum::result=e.what();return -1;}}
}
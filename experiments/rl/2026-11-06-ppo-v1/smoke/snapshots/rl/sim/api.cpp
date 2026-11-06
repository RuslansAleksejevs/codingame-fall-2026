#include "../models/policy.hpp"
#include <random>
static thread_local std::string output;
static thread_local std::string label_plan;
static thread_local std::vector<float> features;
static thread_local std::vector<int> groups,targets,phases;
extern "C" {
void* sim_new(const char*map){try{auto s=new rl::State();std::istringstream in(map);s->load(in);return s;}catch(...){return nullptr;}}
void sim_delete(void*p){delete static_cast<rl::State*>(p);}
void* sim_clone(void*p){auto*s=new rl::State(*static_cast<rl::State*>(p));for(auto&t:s->ts)t=std::make_shared<rl::Triangle>(*t);return s;}
const char* sim_state(void*p){output=static_cast<rl::State*>(p)->json();return output.c_str();}
int sim_step(void*p,const char*a,const char*b){try{static_cast<rl::State*>(p)->step(a,b);return 0;}catch(const std::exception&e){output=e.what();return -1;}}
const char* sim_error(){return output.c_str();}
int sim_labels(void*p,int player,int style,const char*line){
    try{auto gs=rl::labels(*static_cast<rl::State*>(p),player,style,line,&label_plan);features.clear();groups.clear();targets.clear();phases.clear();groups.push_back(0);
        for(auto&g:gs){for(auto&x:g.x)features.insert(features.end(),x.begin(),x.end());groups.push_back(features.size()/rl::FEATURES);targets.push_back(g.label);phases.push_back(g.phase);}return gs.size();
    }catch(const std::exception&e){output=e.what();return -1;}
}
const float* sim_features(){return features.data();}
const int* sim_groups(){return groups.data();}
const int* sim_targets(){return targets.data();}
const int* sim_phases(){return phases.data();}
const char* sim_label_plan(){return label_plan.c_str();}
const char* sim_random(void*p,int player,unsigned seed){
    std::mt19937 rng(seed);rl::Decoder d(*static_cast<rl::State*>(p),player,2);
    output=d.run([&](const std::vector<rl::Candidate>&cs,const rl::Decoder&){return int(rng()%cs.size());});return output.c_str();
}
void* net_new(const char*path){try{auto n=new rl::Network();n->load(path);return n;}catch(...){return nullptr;}}
void net_delete(void*p){delete static_cast<rl::Network*>(p);}
float net_evaluate(void*p,const float*x){std::array<float,rl::FEATURES>a;std::copy(x,x+rl::FEATURES,a.begin());return static_cast<rl::Network*>(p)->evaluate(a);}
const char* net_act(void*n,void*s,int p,int style){output=static_cast<rl::Network*>(n)->act(*static_cast<rl::State*>(s),p,style);return output.c_str();}
}

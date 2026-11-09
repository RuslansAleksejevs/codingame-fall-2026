// D16: cooperative per-operation deadline checks; frozen mechanics stay read-only.
#pragma once
#include "../../search/search.hpp"

namespace deadline {
using Clock = std::chrono::steady_clock;
inline double us(Clock::time_point start) {
    return std::chrono::duration<double, std::micro>(Clock::now()-start).count();
}
struct Stop {};
struct Meter {
    double& total;
    double& maximum;
    Clock::time_point start=Clock::now();
    Meter(double& sum,double& peak):total(sum),maximum(peak){}
    ~Meter(){double elapsed=us(start);total+=elapsed;maximum=std::max(maximum,elapsed);}
};
struct Stats {
    int selected=0, generated=0, complete=0, transitions=0, stopped=0, shallow_complete=0, selected_tier=0;
    int emergency=0, forwards=0, choices=0, checks=0, baseline_complete=0;
    double baseline_us=0, response_us=0, proposal_us=0, future_us=0;
    double decoder_us=0, choices_us=0, feature_us=0, forward_us=0;
    double clone_us=0, simulation_us=0, value_us=0, atomic_max_us=0;
    std::vector<double> values, shallow_values;
    std::string json() const {
        std::ostringstream o;
        o<<std::setprecision(10)<<"{\"selected\":"<<selected<<",\"generated\":"<<generated
         <<",\"shallow_complete\":"<<shallow_complete<<",\"selected_tier\":"<<selected_tier<<",\"paired\":"<<(shallow_complete>=2||complete>=2)<<",\"complete\":"<<complete<<",\"transitions\":"<<transitions
         <<",\"stopped\":"<<stopped<<",\"emergency\":"<<emergency
         <<",\"forwards\":"<<forwards<<",\"choices\":"<<choices<<",\"checks\":"<<checks
         <<",\"baseline_complete\":"<<baseline_complete<<",\"baseline_us\":"<<baseline_us<<",\"response_us\":"<<response_us
         <<",\"proposal_us\":"<<proposal_us<<",\"future_us\":"<<future_us
         <<",\"decoder_us\":"<<decoder_us<<",\"choices_us\":"<<choices_us
         <<",\"feature_us\":"<<feature_us<<",\"forward_us\":"<<forward_us
         <<",\"clone_us\":"<<clone_us<<",\"simulation_us\":"<<simulation_us
         <<",\"value_us\":"<<value_us<<",\"atomic_max_us\":"<<atomic_max_us<<",\"values\":[";
        for(size_t i=0;i<values.size();++i){if(i)o<<',';o<<values[i];}
        o<<"],\"shallow_values\":[";for(size_t i=0;i<shallow_values.size();++i){if(i)o<<',';o<<shallow_values[i];}o<<"]}";return o.str();
    }
};

struct Search : searchpilot::Search {
    Stats stats;
    std::vector<std::array<int,4>> boundaries;
    bool completing_baseline=false;
    Clock::time_point origin;
    double limit_ms=16;
    int forward_cap=20000;
    std::string baseline="WAIT", selected_plan="WAIT";
    Search(const char* actor,const char* critic,const char* e0,const char* e1,const char* e2)
      :searchpilot::Search(actor,critic,e0,e1,e2,2,4,0){}
    void check() {
        ++stats.checks;
        if(!completing_baseline && ((limit_ms>0 && us(origin)>=limit_ms*1000) ||
           (forward_cap>0 && stats.forwards>=forward_cap)))throw Stop{};
    }
    std::array<float,rl::FEATURES> features(const rl::Decoder& d,const rl::Candidate& c) {
        check();std::array<float,rl::FEATURES> x;
        {Meter t(stats.feature_us,stats.atomic_max_us);x=d.features(c);}
        check();return x;
    }
    float infer(const rl::FastNetwork& net,const std::array<float,rl::FEATURES>& x) {
        check();float result;
        {Meter t(stats.forward_us,stats.atomic_max_us);result=net.evaluate(x);++stats.forwards;}
        check();return result;
    }
    // Explicit decoder loop permits polling around candidate-list construction.
    // Choice order, float sums and random draws are exactly the frozen decoder's.
    std::string decode(const rl::FastNetwork& net,const rl::State& s,int p,
                       std::mt19937_64* rng=nullptr,double temperature=0) {
        check();std::unique_ptr<rl::Decoder> decoder;
        {Meter t(stats.decoder_us,stats.atomic_max_us);decoder=std::make_unique<rl::Decoder>(s,p,2);}
        check();auto& d=*decoder;
        auto choose=[&](const std::vector<rl::Candidate>& cs) {
            check();++stats.choices;
            int best=0;float highest=-1e30;
            std::vector<double> probabilities;
            double maximum=-1e30;
            for(int j=0;j<int(cs.size());++j){
                float v=infer(net,features(d,cs[j]));
                if(!rng){if(v>highest){highest=v;best=j;}}
                else {double logit=v/temperature;probabilities.push_back(logit);maximum=std::max(maximum,logit);}
            }
            if(rng){
                double sum=0;for(auto& v:probabilities){v=std::exp(v-maximum);sum+=v;}
                double draw=std::generate_canonical<double,53>(*rng)*sum;
                best=int(probabilities.size())-1;
                for(int j=0;j<int(probabilities.size());++j){if(draw<probabilities[j]){best=j;break;}draw-=probabilities[j];}
            }
            check();d.choose(cs.at(best));check();
        };
        for(auto& triangle:s.ts)if(triangle->owner==p){
            check();std::vector<rl::Candidate> cs;
            {Meter t(stats.choices_us,stats.atomic_max_us);cs=d.spend(triangle);}
            check();choose(cs);
        }
        for(int a=0;a<s.n;++a)while(d.available[a]>0){
            check();std::vector<rl::Candidate> cs{{0,a,a,nullptr}};
            {Meter t(stats.choices_us,stats.atomic_max_us);
             for(int b=0;b<s.n;++b)if(s.adj[a][b])cs.push_back({1,a,b,nullptr});}
            check();choose(cs);
        }
        std::string output;
        for(auto& cmd:d.output){check();if(!output.empty())output+=';';output+=cmd;}
        return output.empty()?"WAIT":output;
    }
    rl::State copy(const rl::State& source){
        check();rl::State state;
        {Meter t(stats.clone_us,stats.atomic_max_us);state=searchpilot::clone(source);}
        check();return state;
    }
    double evaluate_checked(const rl::State& s,int p){
        check();Meter total(stats.value_us,stats.atomic_max_us);
        if(s.done)return s.score[p]>s.score[1-p]?1:s.score[p]<s.score[1-p]?-1:0;
        std::unique_ptr<rl::Decoder> own,enemy;
        {Meter t(stats.decoder_us,stats.atomic_max_us);own=std::make_unique<rl::Decoder>(s,p,2);}
        check();
        {Meter t(stats.decoder_us,stats.atomic_max_us);enemy=std::make_unique<rl::Decoder>(s,1-p,2);}
        check();
        auto a=league::value_features(*own);check();double va=infer(*value,a);
        auto b=league::value_features(*enemy);check();double vb=infer(*value,b);
        return std::clamp((va-vb)/2.,-1.,1.);
    }
    std::string act_checked(const rl::State& root,int player,Clock::time_point start,
                            double milliseconds=16,int proposals=4,int cap=20000){
        stats=Stats{};boundaries.clear();origin=start;limit_ms=milliseconds;forward_cap=cap;
        baseline="WAIT";selected_plan="WAIT";completing_baseline=true;
        try {
            {double unused=0;Meter t(stats.baseline_us,unused);baseline=decode(*policy,root,player);}
            completing_baseline=false;stats.baseline_complete=1;
            selected_plan=baseline;stats.generated=1;
            if(proposals==1)return selected_plan;
            std::vector<std::string> plans{baseline};
            std::array<std::string,3> root_responses;
            for(int model=0;model<3;++model){
                double unused=0;Meter t(stats.response_us,unused);
                root_responses[model]=decode(*responses[model],root,1-player);
            }
            check();std::mt19937_64 rng(searchpilot::state_seed(root,player));check();
            const double temperatures[3]={.15,.35,.7};
            auto score=[&](int index,int depth){
                std::array<double,3> outcomes{};
                for(int model=0;model<3;++model){
                    auto state=copy(root);std::string own=plans[index],other=root_responses[model];int performed=0;
                    for(int turn=0;turn<depth&&!state.done;++turn){
                        if(turn>0){
                            double unused=0;Meter t(stats.future_us,unused);
                            own=decode(*policy,state,player);other=decode(*responses[model],state,1-player);
                        }
                        check();
                        {Meter t(stats.simulation_us,stats.atomic_max_us);
                         state.step(player==0?own:other,player==0?other:own);++performed;++stats.transitions;}
                        check();
                        if(state.parse_errors[0]!=root.parse_errors[0]||state.parse_errors[1]!=root.parse_errors[1])
                            throw std::runtime_error("Invalid simulated plan");
                    }
                    outcomes[model]=std::pow(.995,performed-(state.done?1:0))*evaluate_checked(state,player);
                    boundaries.push_back({depth,index,model,stats.forwards});
                }
                check();double mean=std::accumulate(outcomes.begin(),outcomes.end(),0.)/3.;
                return .5*mean+.5**std::min_element(outcomes.begin(),outcomes.end());
            };
            double base_value=-1e30,best=-1e30;
            for(int candidate=0;candidate<proposals;++candidate){
                check();
                if(candidate>0){
                    std::string plan;
                    {double unused=0;Meter t(stats.proposal_us,unused);
                     plan=decode(*policy,root,player,&rng,temperatures[candidate-1]);}
                    if(std::find(plans.begin(),plans.end(),plan)!=plans.end())continue;
                    plans.push_back(plan);++stats.generated;
                }
                int index=int(plans.size())-1;double combined=score(index,1);
                stats.shallow_values.push_back(combined);++stats.shallow_complete;
                if(stats.shallow_complete==1)base_value=best=combined;
                else {
                    stats.selected_tier=1;
                    if(combined>base_value+.02&&combined>best){
                        best=combined;stats.selected=index;selected_plan=plans[index];
                    }
                }
            }
            base_value=best=-1e30;int deep_selected=0;
            for(int index=0;index<int(plans.size());++index){
                check();double combined=score(index,2);
                stats.values.push_back(combined);++stats.complete;
                if(stats.complete==1)base_value=best=combined;
                else {
                    if(combined>base_value+.02&&combined>best){best=combined;deep_selected=index;}
                    stats.selected=deep_selected;stats.selected_tier=2;selected_plan=plans[deep_selected];
                }
            }
        } catch(const Stop&) {
            stats.stopped=1;stats.emergency=stats.generated==0;
        }
        return selected_plan;
    }
};
}
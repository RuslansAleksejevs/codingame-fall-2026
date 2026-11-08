// Capture generator choices, never infer labels by sorting or parsing actions.
#include "api.cpp"
#include <cstring>

namespace trace {
struct Plan {std::string command;std::vector<rl::Group> groups;};
static thread_local std::vector<float> features;
static thread_local std::vector<int> offsets,choices;
static thread_local std::string output;

Plan generate(const rl::FastNetwork& net,const rl::State& root,int player,
              std::mt19937_64* rng=nullptr,double temperature=0){
    Plan result;rl::Decoder decoder(root,player,2);
    result.command=decoder.run([&](const std::vector<rl::Candidate>& cs,const rl::Decoder& d){
        rl::Group group;group.phase=cs[0].tri?1:0;
        int best=0;float high=-1e30;std::vector<double> probs;double maximum=-1e30;
        for(int j=0;j<int(cs.size());++j){
            group.x.push_back(d.features(cs[j]));float v=net.evaluate(group.x.back());
            if(!rng){if(v>high){best=j;high=v;}}
            else {double logit=v/temperature;probs.push_back(logit);maximum=std::max(maximum,logit);}
        }
        if(rng){double sum=0;for(auto& p:probs){p=std::exp(p-maximum);sum+=p;}
            double draw=std::generate_canonical<double,53>(*rng)*sum;best=int(probs.size())-1;
            for(int j=0;j<int(probs.size());++j){if(draw<probs[j]){best=j;break;}draw-=probs[j];}}
        group.label=best;result.groups.push_back(std::move(group));return best;
    });
    // Independent replay of recorded choices: every prefix feature is bit-equal.
    size_t index=0;rl::Decoder replay(root,player,2);
    auto encoded=replay.run([&](const std::vector<rl::Candidate>& cs,const rl::Decoder& d){
        const auto& group=result.groups.at(index++);
        if(cs.size()!=group.x.size()||group.label<0||group.label>=int(cs.size()))throw std::runtime_error("Trace mask mismatch");
        for(size_t j=0;j<cs.size();++j){auto fresh=d.features(cs[j]);
            if(std::memcmp(fresh.data(),group.x[j].data(),sizeof(float)*rl::FEATURES))throw std::runtime_error("Trace prefix feature mismatch");}
        return group.label;
    });
    if(index!=result.groups.size()||encoded!=result.command)throw std::runtime_error("Trace rendering mismatch");
    auto checked=searchpilot::clone(root);checked.parse(encoded,player);
    if(checked.parse_errors[player]!=root.parse_errors[player])throw std::runtime_error("Trace command not legal");
    return result;
}
}

extern "C" {
const char* tr_make(void* pointer,void* state,int player,int selected){
    try {
        auto& teacher=*static_cast<deadline::Search*>(pointer);auto& root=*static_cast<rl::State*>(state);
        const auto before=root.json();std::vector<trace::Plan> plans{trace::generate(*teacher.policy,root,player)};
        std::vector<std::string> reference{teacher.policy->act(root,player,2)};
        std::mt19937_64 rng(searchpilot::state_seed(root,player)),reference_rng(searchpilot::state_seed(root,player));
        if(plans[0].command!=reference[0])throw std::runtime_error("Greedy trace differs from frozen generator");
        for(double temperature:{.15,.35,.7}){
            auto plan=trace::generate(*teacher.policy,root,player,&rng,temperature);
            auto original=searchpilot::sampled(*teacher.policy,root,player,reference_rng,temperature);
            if(plan.command!=original)throw std::runtime_error("Sampled trace differs from frozen generator");
            if(std::find(reference.begin(),reference.end(),original)==reference.end()){
                reference.push_back(original);plans.push_back(std::move(plan));}
        }
        if(selected<0||selected>=int(plans.size()))throw std::runtime_error("Selected proposal absent");
        const auto& plan=plans[selected];trace::features.clear();trace::offsets={0};trace::choices.clear();
        for(const auto& group:plan.groups){
            trace::choices.push_back(group.label);
            for(const auto& x:group.x)trace::features.insert(trace::features.end(),x.begin(),x.end());
            trace::offsets.push_back(int(trace::features.size()/rl::FEATURES));
        }
        if(root.json()!=before)throw std::runtime_error("Trace changed root");
        std::ostringstream out;out<<"{\"selected\":"<<selected<<",\"groups\":"<<plan.groups.size()
            <<",\"candidate_rows\":"<<trace::features.size()/rl::FEATURES<<",\"command\":"<<std::quoted(plan.command)
            <<",\"prefix_feature_bits_exact\":true,\"mask_legal\":true,\"plans\":[";
        for(size_t i=0;i<plans.size();++i){if(i)out<<',';out<<std::quoted(plans[i].command);}out<<"]}";
        trace::output=out.str();return trace::output.c_str();
    }catch(const std::exception& e){error=e.what();return nullptr;}
}
const float* tr_features(){return trace::features.data();}
const int* tr_offsets(){return trace::offsets.data();}
const int* tr_choices(){return trace::choices.data();}
}
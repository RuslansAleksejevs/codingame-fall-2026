// Additional tests only; does not alter the candidate executable or decision rule.
#include "api.cpp"
extern "C" {
const char* ds_contract(void* pointer,void* state,int player,const char* text){
    try {
        auto& search=*static_cast<deadline::Search*>(pointer);
        auto& root=*static_cast<rl::State*>(state);const auto before=root.json();
        std::istringstream in(text);rl::State s;in>>s.n;
        for(int i=0;i<s.n;++i){int id;in>>id;in>>s.x[id]>>s.y[id];}
        in>>s.score[0];s.turn=root.turn;
        if(!deadline::read_turn(in,s))throw std::runtime_error("Incomplete input");
        auto restored=absolute_view(s,player);
        bool hidden_ok=restored.surrounded==root.surrounded;
        for(int p=0;p<2;++p)for(int q=0;q<root.n;++q)hidden_ok&=restored.rem[p][q]==root.rem[p][q];
        for(size_t i=0;i<root.ts.size();++i)hidden_ok&=restored.ts[i]->initial==root.ts[i]->initial;
        if(!hidden_ok||restored.json()!=before)throw std::runtime_error("Hidden restoration mismatch");
        std::vector<std::string> plans{search.policy->act(root,player,2)};
        std::mt19937_64 rng(searchpilot::state_seed(root,player));
        for(double temperature:{.15,.35,.7}){
            auto plan=searchpilot::sampled(*search.policy,root,player,rng,temperature);
            if(std::find(plans.begin(),plans.end(),plan)==plans.end())plans.push_back(plan);
        }
        search.act_checked(root,player,deadline::Clock::now(),0,4,0);auto full=search.stats;
        if(full.complete!=int(plans.size()))throw std::runtime_error("Candidate enumeration mismatch");
        search.act_checked(root,player,deadline::Clock::now(),0,1,0);int base=search.stats.forwards;
        std::vector<int> caps{base+1,full.forwards-1};
        for(int i=1;i<5;++i)caps.push_back(base+(full.forwards-base)*i/5);
        std::sort(caps.begin(),caps.end());caps.erase(std::unique(caps.begin(),caps.end()),caps.end());
        std::ostringstream o;o<<"{\"hidden_restore\":true,\"root_immutable\":true,\"caps\":[";
        for(size_t k=0;k<caps.size();++k){
            auto action=search.act_checked(root,player,deadline::Clock::now(),0,4,caps[k]);auto st=search.stats;
            int expected=0;double best=full.values[0];
            for(int i=0;i<st.complete;++i){
                if(st.values[i]!=full.values[i])throw std::runtime_error("Partial score changed complete prefix");
                if(i&&st.values[i]>full.values[0]+.02&&st.values[i]>best){best=st.values[i];expected=i;}
            }
            if(st.emergency||!st.stopped||st.selected!=expected||action!=plans[expected]||search.baseline!=plans[0])
                throw std::runtime_error("Stop did not return best complete immutable plan");
            if(root.json()!=before)throw std::runtime_error("Root mutation");
            auto clone=searchpilot::clone(root);auto parsed=clone.parse(action,player);(void)parsed;
            if(clone.parse_errors[player]!=root.parse_errors[player])throw std::runtime_error("Illegal selected plan");
            if(k)o<<',';o<<"{\"cap\":"<<caps[k]<<",\"complete\":"<<st.complete<<",\"selected\":"<<st.selected<<"}";
        }
        o<<"]}";result=o.str();return result.c_str();
    }catch(const std::exception& e){error=e.what();return nullptr;}
}
}
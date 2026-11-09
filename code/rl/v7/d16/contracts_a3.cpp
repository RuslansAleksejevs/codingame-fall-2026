// Independent one-turn oracle and complete-tier interruption contracts only.
namespace a3test {
struct Oracle {std::vector<std::string> plans;std::vector<double> shallow;};
double value(deadline::Search& search,const rl::State& state,int player){
    if(state.done)return state.score[player]>state.score[1-player]?1:state.score[player]<state.score[1-player]?-1:0;
    rl::Decoder own(state,player,2),enemy(state,1-player,2);
    double a=search.value->evaluate(league::value_features(own));
    double b=search.value->evaluate(league::value_features(enemy));
    return std::clamp((a-b)/2.,-1.,1.);
}
Oracle oracle(deadline::Search& search,const rl::State& root,int player){
    Oracle out;out.plans={search.policy->act(root,player,2)};
    std::mt19937_64 rng(searchpilot::state_seed(root,player));
    for(double t:{.15,.35,.7}){
        auto plan=searchpilot::sampled(*search.policy,root,player,rng,t);
        if(std::find(out.plans.begin(),out.plans.end(),plan)==out.plans.end())out.plans.push_back(plan);
    }
    std::array<std::string,3> responses;
    for(int m=0;m<3;++m)responses[m]=search.responses[m]->act(root,1-player,2);
    for(auto& plan:out.plans){
        std::array<double,3> values{};
        for(int m=0;m<3;++m){
            auto state=searchpilot::clone(root);int performed=0;
            if(!state.done){state.step(player==0?plan:responses[m],player==0?responses[m]:plan);performed=1;}
            if(state.parse_errors[0]!=root.parse_errors[0]||state.parse_errors[1]!=root.parse_errors[1])throw std::runtime_error("Oracle invalid plan");
            values[m]=std::pow(.995,performed-(state.done?1:0))*value(search,state,player);
        }
        double mean=std::accumulate(values.begin(),values.end(),0.)/3.;
        out.shallow.push_back(.5*mean+.5**std::min_element(values.begin(),values.end()));
    }
    return out;
}
int best(const std::vector<double>& values,int count){
    int selected=0;if(!count)return 0;double high=values[0];
    for(int i=1;i<count;++i)if(values[i]>values[0]+.02&&values[i]>high){high=values[i];selected=i;}
    return selected;
}
}
extern "C" {
const char* ds_a3_oracle(void* pointer,void* state,int player){
    try {
        auto& search=*static_cast<deadline::Search*>(pointer);auto& root=*static_cast<rl::State*>(state);
        auto before=root.json();auto out=a3test::oracle(search,root,player);
        if(out.shallow!=search.stats.shallow_values||int(out.plans.size())!=search.stats.complete||root.json()!=before)
            throw std::runtime_error("Independent shallow oracle mismatch");
        std::ostringstream o;o<<std::setprecision(17)<<"{\"plans\":"<<out.plans.size()<<",\"shallow\":[";
        for(size_t i=0;i<out.shallow.size();++i){if(i)o<<',';o<<out.shallow[i];}
        o<<"]}";result=o.str();return result.c_str();
    }catch(const std::exception& e){error=e.what();return nullptr;}
}
const char* ds_contract(void* pointer,void* state,int player,const char* text){
    try {
        auto& search=*static_cast<deadline::Search*>(pointer);auto& root=*static_cast<rl::State*>(state);
        const auto before=root.json();const char* restored=ds_restore(text,root.turn,player);
        if(!restored||std::string(restored)!=before)throw std::runtime_error("Hidden restoration mismatch");
        auto out=a3test::oracle(search,root,player);
        search.act_checked(root,player,deadline::Clock::now(),0,4,0);auto full=search.stats;auto boundaries=search.boundaries;
        if(full.shallow_values!=out.shallow||full.complete!=int(out.plans.size()))throw std::runtime_error("Full oracle mismatch");
        search.act_checked(root,player,deadline::Clock::now(),0,1,0);int baseline_forwards=search.stats.forwards;
        std::vector<int> caps{baseline_forwards+1,full.forwards-1};
        for(auto b:boundaries)if((b[0]==1&&b[1]<=1&&b[2]<2)||(b[0]==2&&b[1]<=1&&b[2]==2))caps.push_back(b[3]+1);
        std::sort(caps.begin(),caps.end());caps.erase(std::unique(caps.begin(),caps.end()),caps.end());
        std::ostringstream o;o<<"{\"hidden_restore\":true,\"root_immutable\":true,\"caps\":[";bool first=true;
        for(int cap:caps){
            if(cap<=baseline_forwards||cap>=full.forwards)continue;
            auto action=search.act_checked(root,player,deadline::Clock::now(),0,4,cap);auto st=search.stats;
            for(int i=0;i<st.shallow_complete;++i)if(st.shallow_values[i]!=out.shallow[i])throw std::runtime_error("Partial shallow score");
            for(int i=0;i<st.complete;++i)if(st.values[i]!=full.values[i])throw std::runtime_error("Partial deep score");
            int tier=st.complete>=2?2:st.shallow_complete>=2?1:0;
            int chosen=tier==2?a3test::best(full.values,st.complete):a3test::best(out.shallow,st.shallow_complete);
            if(st.emergency||!st.baseline_complete||!st.stopped||st.selected!=chosen||st.selected_tier!=tier||action!=out.plans[chosen]||root.json()!=before)
                throw std::runtime_error("Wrong complete-tier incumbent at interruption");
            auto copy=searchpilot::clone(root);copy.parse(action,player);
            if(copy.parse_errors[player]!=root.parse_errors[player])throw std::runtime_error("Illegal complete-tier output");
            if(!first)o<<',';first=false;
            o<<"{\"cap\":"<<cap<<",\"shallow_complete\":"<<st.shallow_complete<<",\"deep_complete\":"<<st.complete<<",\"tier\":"<<tier<<",\"selected\":"<<chosen<<'}';
        }
        o<<"]}";result=o.str();return result.c_str();
    }catch(const std::exception& e){error=e.what();return nullptr;}
}
}
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
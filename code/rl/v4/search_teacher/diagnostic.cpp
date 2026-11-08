// Offline ranking diagnostic. The existing teacher and simulator stay unchanged.
#include "../../search/search.hpp"

namespace teacherdiag {
static thread_local std::string output;
void quoted(std::ostream& out, const std::string& text) { out << std::quoted(text); }

std::string inspect(searchpilot::Search& teacher, const rl::State& root, int player) {
    const std::string original = root.json();
    std::array<std::string, 3> responses;
    // Commit all opponent root responses before generating our alternatives.
    for (int model = 0; model < 3; ++model)
        responses[model] = teacher.responses[model]->act(root, 1-player, 2);
    std::vector<std::string> plans{teacher.policy->act(root, player, 2)};
    std::mt19937_64 rng(searchpilot::state_seed(root, player));
    for (double temperature : {.15, .35, .7}) {
        auto plan = searchpilot::sampled(*teacher.policy, root, player, rng, temperature);
        if (std::find(plans.begin(), plans.end(), plan) == plans.end()) plans.push_back(plan);
    }
    std::ostringstream out;
    out << std::setprecision(12) << "{\"player\":" << player << ",\"root\":" << original
        << ",\"root_responses\":[";
    for (int model=0; model<3; ++model) { if (model) out << ','; quoted(out,responses[model]); }
    out << "],\"plans\":[";
    for (size_t p=0; p<plans.size(); ++p) {
        if (p) out << ',';
        out << "{\"command\":"; quoted(out, plans[p]); out << ",\"models\":[";
        for (int model=0; model<3; ++model) {
            if (model) out << ',';
            auto state=searchpilot::clone(root);
            std::vector<std::array<std::string,2>> actions;
            std::vector<std::pair<int,std::string>> snapshots;
            std::array<double,4> values{};
            const int horizons[4]={1,2,4,8};
            while (!state.done) {
                if (actions.size()>200) throw std::runtime_error("Non-terminating continuation");
                auto own=actions.empty() ? plans[p] : teacher.policy->act(state,player,2);
                auto other=actions.empty() ? responses[model] : teacher.responses[model]->act(state,1-player,2);
                std::array<std::string,2> pair=player==0 ? std::array<std::string,2>{own,other} : std::array<std::string,2>{other,own};
                state.step(pair[0],pair[1]); actions.push_back(pair);
                if (state.parse_errors[0]!=root.parse_errors[0] || state.parse_errors[1]!=root.parse_errors[1])
                    throw std::runtime_error("Illegal counterfactual plan");
                int performed=int(actions.size());
                for (int h=0;h<4;++h)
                    if (performed==horizons[h] || (state.done && performed<horizons[h]))
                        values[h]=std::pow(.995,performed-(state.done?1:0))*teacher.evaluate(state,player);
                if (performed==1 || performed==2 || performed==4 || performed==8 || state.done)
                    snapshots.emplace_back(performed,state.json());
            }
            out << "{\"short_values\":[";
            for (int h=0;h<4;++h) { if(h)out<<','; out<<values[h]; }
            out << "],\"terminal\":" << teacher.evaluate(state,player)
                << ",\"discounted_terminal\":" << std::pow(.995,int(actions.size())-1)*teacher.evaluate(state,player)
                << ",\"actions\":[";
            for (size_t i=0;i<actions.size();++i) { if(i)out<<','; out<<'[';quoted(out,actions[i][0]);out<<',';quoted(out,actions[i][1]);out<<']'; }
            out << "],\"snapshots\":[";
            for (size_t i=0;i<snapshots.size();++i) { if(i)out<<',';out<<"{\"depth\":"<<snapshots[i].first<<",\"state\":"<<snapshots[i].second<<'}'; }
            out << "]}";
        }
        out << "]}";
    }
    if (root.json()!=original) throw std::runtime_error("Root mutated by diagnostic");
    out << "]}";
    return out.str();
}
}

extern "C" {
const char* teacher_inspect(void* ptr, void* state, int player) {
    try {
        teacherdiag::output=teacherdiag::inspect(*static_cast<searchpilot::Search*>(ptr),*static_cast<rl::State*>(state),player);
        return teacherdiag::output.c_str();
    } catch(const std::exception& error) { searchpilot::last_error=error.what();return nullptr; }
}
}
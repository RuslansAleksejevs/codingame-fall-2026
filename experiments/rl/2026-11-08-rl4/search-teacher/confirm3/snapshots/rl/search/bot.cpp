#include "search.hpp"
#include <iostream>

// The pinned official Board generator assigns player 0 to the three leftmost
// nodes and player 1 to their mirrors (x'=1919-x, y'=959-y). Input labels are
// relative to us, but simultaneous tie ordering and terminal checks are not.
// Validate this exact start before recovering the absolute order; never guess
// on a custom/unknown start. The native API already receives absolute states.
int absolute_player(const rl::State& initial) {
    if (initial.turn != 0 || initial.n < 6)
        throw std::runtime_error("Cannot recover absolute player from this start");
    std::vector<int> ids(initial.n);
    std::iota(ids.begin(), ids.end(), 0);
    std::stable_sort(ids.begin(), ids.end(), [&](int a, int b) { return initial.x[a] < initial.x[b]; });
    int expected[2][rl::NMAX]{};
    for (int k=0;k<3;++k) {
        int q=ids[k], mirror=-1;
        expected[0][q]=1;
        for (int j=0;j<initial.n;++j)
            if (initial.x[j]==1919-initial.x[q] && initial.y[j]==959-initial.y[q]) mirror=j;
        if (mirror<0) throw std::runtime_error("Unknown start: missing official mirror");
        expected[1][mirror]=1;
    }
    for (int player=0;player<2;++player) {
        bool matches=true;
        for (int q=0;q<initial.n;++q)
            matches &= initial.u[0][q]==expected[player][q] && initial.u[1][q]==expected[1-player][q];
        if (matches) return player;
    }
    throw std::runtime_error("Unknown start: cannot verify official absolute player order");
}

rl::State absolute_view(const rl::State& relative, int player) {
    rl::State result=searchpilot::clone(relative);
    if (player==1) {
        std::swap(result.score[0],result.score[1]);
        std::swap(result.parse_errors[0],result.parse_errors[1]);
        for (int q=0;q<result.n;++q) {
            std::swap(result.u[0][q],result.u[1][q]);
            std::swap(result.rem[0][q],result.rem[1][q]);
        }
        for (auto& t:result.ts) {
            if (t->owner>=0) t->owner=1-t->owner;
            if (t->initial>=0) t->initial=1-t->initial;
            std::swap(t->cap[0],t->cap[1]);
        }
    }
    return result;
}

int main(int argc, char** argv) {
    if (argc < 6) {
        std::cerr << "Usage: search-bot ACTOR CRITIC ENEMY0 ENEMY1 ENEMY2 [DEPTH=2] [CANDIDATES=4] [BUDGET_MS=30]\n";
        return 1;
    }
    searchpilot::Search search(argv[1], argv[2], argv[3], argv[4], argv[5],
                              argc > 6 ? std::stoi(argv[6]) : 2,
                              argc > 7 ? std::stoi(argv[7]) : 4,
                              argc > 8 ? std::stod(argv[8]) : 30);
    rl::State state;
    int global_player=-1;
    if (!(std::cin >> state.n)) return 0;
    for (int i=0;i<state.n;++i) { int id; std::cin>>id; std::cin>>state.x[id]>>state.y[id]; }
    while (std::cin >> state.score[0] >> state.score[1]) {
        for (int i=0;i<state.n;++i) {
            int id; std::cin>>id; std::cin>>state.u[0][id]>>state.u[1][id];
            state.rem[0][id]=state.u[0][id]; state.rem[1][id]=state.u[1][id];
        }
        std::fill(&state.adj[0][0], &state.adj[0][0]+rl::NMAX*rl::NMAX, false);
        int count; std::cin>>count;
        for (int i=0;i<count;++i) { int a,b; std::cin>>a>>b; state.adj[a][b]=state.adj[b][a]=true; }
        std::cin>>count; state.ts.clear();
        for (int i=0;i<count;++i) {
            auto triangle=std::make_shared<rl::Triangle>(); int a,b;
            std::cin>>triangle->v[0]>>triangle->v[1]>>triangle->v[2]>>triangle->owner>>a>>b;
            triangle->cap={bool(a),bool(b)}; triangle->initial=triangle->owner; state.ts.push_back(triangle);
        }
        std::cin>>count; for (int i=0;i<count;++i) { int a,b; std::cin>>a>>b; }
        if (!std::cin) return 2;
        auto started=std::chrono::steady_clock::now();
        if (global_player<0) global_player=absolute_player(state);
        auto root=absolute_view(state,global_player);
        std::string action=search.act(root,global_player);
        auto micros=std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now()-started).count();
        int army=0,income=0;for(int i=0;i<state.n;++i)army+=state.u[0][i];for(auto&t:state.ts)income+=t->owner==0;
        std::cerr<<"turn="<<state.turn+1<<" units="<<army<<" triangles="<<income<<" plan_us="<<micros<<'\n';
        std::cerr<<"search="<<search.info<<'\n';
        std::cout<<action<<std::endl;++state.turn;
    }
}
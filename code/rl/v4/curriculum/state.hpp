// Settled-boundary serialization. Mechanics remain in the pinned simulator.
#pragma once
#include "../../sim/simulator.hpp"

namespace curriculum {
inline rl::State clone(const rl::State& source) {
    rl::State result=source;
    for(auto& t:result.ts)t=std::make_shared<rl::Triangle>(*t);
    return result;
}
inline std::string snapshot(const rl::State& s) {
    std::string base=s.json();base.pop_back();std::ostringstream out;
    out<<base<<",\"schema\":1,\"phase\":\"settled_predecision\",\"queue\":[],\"nodes\":[";
    for(int q=0;q<s.n;q++){if(q)out<<',';out<<'['<<s.x[q]<<','<<s.y[q]<<']';}
    out<<"],\"remaining\":[";
    for(int q=0;q<s.n;q++){if(q)out<<',';out<<'['<<s.rem[0][q]<<','<<s.rem[1][q]<<']';}
    out<<"],\"initial_owners\":[";
    for(size_t i=0;i<s.ts.size();i++){if(i)out<<',';out<<s.ts[i]->initial;}
    out<<"],\"surrounded\":"<<(s.surrounded?"true":"false")<<'}';return out.str();
}
inline rl::State restore(const char* text) {
    std::istringstream in(text);std::string magic;rl::State s;
    int terminal=-1,surrounded=-1;in>>magic>>s.n>>s.turn>>s.score[0]>>s.score[1]>>terminal>>surrounded;
    if(!in||magic!="CURRICULUM1"||s.n<1||s.n>rl::NMAX||s.turn<0||s.turn>=200||terminal!=0||surrounded!=1||s.score[0]<0||s.score[1]<0)
        throw std::runtime_error("Invalid settled-state header");
    s.done=terminal;s.surrounded=surrounded;
    for(int q=0;q<s.n;q++){
        in>>s.x[q]>>s.y[q]>>s.u[0][q]>>s.u[1][q]>>s.rem[0][q]>>s.rem[1][q];
        if(!in||s.u[0][q]<0||s.u[1][q]<0||s.u[0][q]!=s.rem[0][q]||s.u[1][q]!=s.rem[1][q])
            throw std::runtime_error("Not a settled unit boundary");
    }
    int edges=-1;in>>edges;if(!in||edges<0||edges>s.n*(s.n-1)/2)throw std::runtime_error("Invalid edge count");
    for(int i=0;i<edges;i++){int a=-1,b=-1;in>>a>>b;if(!in||a<0||a>=b||b>=s.n||s.adj[a][b])throw std::runtime_error("Invalid edge");s.adj[a][b]=s.adj[b][a]=true;}
    s.triangles();int triangles=-1;in>>triangles;
    if(triangles!=int(s.ts.size()))throw std::runtime_error("Triangle topology mismatch");
    for(auto& t:s.ts){int a=-1,b=-1,c=-1,owner=-2,initial=-2,cap0=-1,cap1=-1;in>>a>>b>>c>>owner>>initial>>cap0>>cap1;
        if(!in||t->v!=std::array<int,3>{a,b,c}||owner < -1||owner>1||initial!=owner||(cap0!=0&&cap0!=1)||(cap1!=0&&cap1!=1))
            throw std::runtime_error("Triangle boundary mismatch");
        t->owner=owner;t->initial=initial;t->cap={bool(cap0),bool(cap1)};
        if(owner>=0&&(t->cap[owner]||!t->cap[1-owner]))throw std::runtime_error("Owned capture flags inconsistent");
    }
    if(!in)throw std::runtime_error("Truncated snapshot");std::string extra;if(in>>extra)throw std::runtime_error("Trailing snapshot data");
    // Crucially: no settle(), score increment, or unit-only map load here.
    return s;
}
}
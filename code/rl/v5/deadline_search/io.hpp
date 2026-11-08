// Reuse the audited official-start absolute ordering without editing its source.
#pragma once
#define main frozen_search_reference_main
#include "../../search/bot.cpp"
#undef main

namespace deadline {
inline bool read_turn(std::istream& in,rl::State& s){
    // The caller has already consumed score[0] and started its move clock.
    in>>s.score[1];
    for(int i=0;i<s.n;++i){int id;in>>id;if(id<0||id>=s.n)return false;
        in>>s.u[0][id]>>s.u[1][id];s.rem[0][id]=s.u[0][id];s.rem[1][id]=s.u[1][id];}
    for(auto& row:s.adj)std::fill(std::begin(row),std::end(row),false);
    int count;in>>count;if(count<0||count>2704)return false;
    for(int i=0;i<count;++i){int a,b;in>>a>>b;if(a<0||b<0||a>=s.n||b>=s.n)return false;s.adj[a][b]=s.adj[b][a]=true;}
    in>>count;if(count<0||count>1000)return false;s.ts.clear();
    for(int i=0;i<count;++i){auto t=std::make_shared<rl::Triangle>();int a,b;
        in>>t->v[0]>>t->v[1]>>t->v[2]>>t->owner>>a>>b;
        t->cap={bool(a),bool(b)};t->initial=t->owner;s.ts.push_back(t);}
    in>>count;if(count<0||count>2704)return false;
    for(int i=0;i<count;++i){int a,b;in>>a>>b;}
    s.surrounded=true;return bool(in);
}
}
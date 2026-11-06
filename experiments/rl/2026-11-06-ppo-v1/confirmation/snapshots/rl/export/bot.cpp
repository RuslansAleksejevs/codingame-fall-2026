#include "../models/policy.hpp"
#include <chrono>
#include <iostream>
int main(int argc,char**argv){
    if(argc<2){std::cerr<<"Usage: bc-bot WEIGHTS [STYLE=2]\n";return 1;}
    rl::Network net;net.load(argv[1]);int style=argc>2?std::stoi(argv[2]):2;
    rl::State s;if(!(std::cin>>s.n))return 0;
    for(int i=0;i<s.n;i++){int id;std::cin>>id;std::cin>>s.x[id]>>s.y[id];}
    while(std::cin>>s.score[0]>>s.score[1]){
        for(int i=0;i<s.n;i++){int id;std::cin>>id;std::cin>>s.u[0][id]>>s.u[1][id];s.rem[0][id]=s.u[0][id];s.rem[1][id]=s.u[1][id];}
        std::fill(&s.adj[0][0],&s.adj[0][0]+rl::NMAX*rl::NMAX,false);
        int n;std::cin>>n;for(int i=0;i<n;i++){int a,b;std::cin>>a>>b;s.adj[a][b]=s.adj[b][a]=true;}
        std::cin>>n;s.ts.clear();for(int i=0;i<n;i++){auto t=std::make_shared<rl::Triangle>();int a,b;std::cin>>t->v[0]>>t->v[1]>>t->v[2]>>t->owner>>a>>b;t->cap={bool(a),bool(b)};t->initial=t->owner;s.ts.push_back(t);}
        std::cin>>n;for(int i=0;i<n;i++){int a,b;std::cin>>a>>b;}
        if(!std::cin)return 2;
        auto start=std::chrono::steady_clock::now();std::string line=net.act(s,0,style);
        auto micros=std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now()-start).count();
        int army=0,income=0;for(int q=0;q<s.n;q++)army+=s.u[0][q];for(auto&t:s.ts)income+=t->owner==0;
        std::cerr<<"turn="<<s.turn+1<<" units="<<army<<" triangles="<<income<<" plan_us="<<micros<<'\n';
        std::cout<<line<<std::endl;s.turn++;
    }
}

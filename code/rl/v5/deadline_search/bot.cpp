#include "search.hpp"
#include "io.hpp"
#include <cstdio>

int main(int argc,char** argv){
    if(argc<6)return 1;
    std::ios::sync_with_stdio(false);std::cin.tie(nullptr);
    deadline::Search search(argv[1],argv[2],argv[3],argv[4],argv[5]);
    int proposals=argc>6?std::stoi(argv[6]):4;
    double budget=argc>7?std::stod(argv[7]):16;
    rl::State relative;int player=-1;
    if(!(std::cin>>relative.n))return 0;
    if(relative.n<6||relative.n>rl::NMAX)return 2;
    for(int i=0;i<relative.n;++i){int id;std::cin>>id;if(id<0||id>=relative.n)return 2;std::cin>>relative.x[id]>>relative.y[id];}
    while(std::cin>>relative.score[0]){
        auto began=deadline::Clock::now();
        if(!deadline::read_turn(std::cin,relative))return 2;
        double parse_us=deadline::us(began);
        auto restore=deadline::Clock::now();
        if(player<0)player=absolute_player(relative);
        auto root=absolute_view(relative,player);
        double restore_us=deadline::us(restore);
        auto plan_start=deadline::Clock::now();
        auto action=search.act_checked(root,player,began,budget,proposals,budget>0?20000:0);
        double plan_us=deadline::us(plan_start);
        auto flush_start=deadline::Clock::now();
        // Exactly one newline per observation; no speculative early outputs.
        std::cout<<action<<'\n';std::cout.flush();
        double flush_us=deadline::us(flush_start),total_us=deadline::us(began);
        auto diagnostics_start=deadline::Clock::now();
        int army=0,income=0;for(int i=0;i<root.n;++i)army+=root.u[player][i];for(auto&t:root.ts)income+=t->owner==player;
        std::ostringstream log;
        log<<"turn="<<root.turn+1<<" units="<<army<<" triangles="<<income<<" plan_us="<<int(plan_us)<<'\n'
           <<"deadline={\"turn\":"<<root.turn+1<<",\"player\":"<<player<<",\"parse_us\":"<<parse_us
           <<",\"restore_us\":"<<restore_us<<",\"flush_us\":"<<flush_us<<",\"through_flush_us\":"<<total_us
           <<",\"search\":"<<search.stats.json()<<"}\n";
        auto text=log.str();std::fwrite(text.data(),1,text.size(),stderr);std::fflush(stderr);
        // This last short log write itself is excluded, as is pre-first-token delay.
        std::fprintf(stderr,"post_flush_us=%.3f\n",deadline::us(diagnostics_start));std::fflush(stderr);
        ++relative.turn;
    }
    return 0;
}
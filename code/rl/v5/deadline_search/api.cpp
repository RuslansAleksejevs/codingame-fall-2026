#include "search.hpp"
#include "io.hpp"
static thread_local std::string result,error;
extern "C" {
void* ds_new(const char* a,const char* v,const char* e0,const char* e1,const char* e2){
    try{return new deadline::Search(a,v,e0,e1,e2);}catch(const std::exception& e){error=e.what();return nullptr;}}
void ds_delete(void* p){delete static_cast<deadline::Search*>(p);}
const char* ds_error(){return error.c_str();}
const char* ds_act(void* p,void* state,int player,double budget,int count,int cap,double elapsed){
    try{auto& search=*static_cast<deadline::Search*>(p);
        auto start=deadline::Clock::now()-std::chrono::microseconds(int(elapsed));
        result=search.act_checked(*static_cast<rl::State*>(state),player,start,budget,count,cap);return result.c_str();
    }catch(const std::exception& e){error=e.what();return nullptr;}}
const char* ds_stats(void* p){result=static_cast<deadline::Search*>(p)->stats.json();return result.c_str();}
const char* ds_restore(const char* text,int turn,int player){
    try{std::istringstream in(text);rl::State s;in>>s.n;
        for(int i=0;i<s.n;++i){int id;in>>id;in>>s.x[id]>>s.y[id];}
        in>>s.score[0];s.turn=turn;if(!deadline::read_turn(in,s))throw std::runtime_error("Bad input");
        if(turn==0&&absolute_player(s)!=player)throw std::runtime_error("Wrong absolute player");
        in>>std::ws;if(!in.eof())throw std::runtime_error("Unconsumed input");
        result=absolute_view(s,player).json();return result.c_str();
    }catch(const std::exception& e){error=e.what();return nullptr;}}
}
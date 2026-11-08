// Native port of the pinned TryAngle-Catch referee's mechanical rules.
// Upstream: eulerscheZahl/TryAngle-Catch, b6913124a10de328316ff42906448a18cb948431.
#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <memory>
#include <queue>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace rl {
constexpr int NMAX = 52;
struct Triangle {
    std::array<int,3> v;
    int owner = -1, initial = -1;
    std::array<bool,2> cap{true,true};
};
struct Action {
    int type = -1, player = 0, a = 0, b = 0, c = 0, d = 0, amount = 1;
    std::shared_ptr<Triangle> tri;
};
// Priorities match TaskManager: attack, move, spawn, add, remove.
enum { ATTACK=0, MOVE=1, SPAWN=2, ADD=3, REMOVE=4 };
struct State {
    int n=0, turn=0, score[2]{0,0};
    bool done=false, surrounded=false;
    int x[NMAX]{}, y[NMAX]{}, u[2][NMAX]{}, rem[2][NMAX]{};
    bool adj[NMAX][NMAX]{};
    std::vector<std::shared_ptr<Triangle>> ts;
    int parse_errors[2]{0,0};

    int dist2(int a,int b) const {return (x[a]-x[b])*(x[a]-x[b])+(y[a]-y[b])*(y[a]-y[b]);}
    bool ccw(int a,int b,int c) const {
        return (y[c]-y[a])*(x[b]-x[a]) > (y[b]-y[a])*(x[c]-x[a]);
    }
    bool crossing(int a,int b,int c,int d) const {
        if(a==b||a==c||a==d||b==c||b==d)return false;
        return ccw(a,c,d)!=ccw(b,c,d)&&ccw(a,b,c)!=ccw(a,b,d);
    }
    bool connectable(int a,int b) const {
        if(dist2(a,b)>160000)return false;
        for(int c=0;c<n;c++)for(int d=c+1;d<n;d++)
            if(adj[c][d]&&crossing(a,b,c,d))return false;
        return true;
    }
    bool inside(int q,int a,int b,int c) const {
        if(q==a||q==b||q==c)return false;
        return ccw(q,a,b)==ccw(q,b,c)&&ccw(q,b,c)==ccw(q,c,a);
    }
    void triangles() {
        auto old=ts; ts.clear();
        for(int a=0;a<n;a++)for(int b=a+1;b<n;b++)if(adj[a][b])
            for(int c=b+1;c<n;c++)if(adj[a][c]&&adj[b][c]) {
                bool valid=true;for(int q=0;q<n;q++)if(inside(q,a,b,c)){valid=false;break;}
                if(!valid)continue;
                std::array<int,3> key{a,b,c}; std::shared_ptr<Triangle> t;
                for(auto &o:old)if(o->v==key){t=o;break;}
                if(!t){t=std::make_shared<Triangle>();t->v=key;}
                ts.push_back(t);
            }
    }
    std::shared_ptr<Triangle> triangle(int a,int b,int c) const {
        // Match upstream membership semantics, including repeated command corners.
        for(auto &t:ts) {
            auto has=[&](int q){return std::find(t->v.begin(),t->v.end(),q)!=t->v.end();};
            if(has(a)&&has(b)&&has(c))return t;
        }
        return nullptr;
    }
    int owner(int q) const {
        bool any=false,all0=true,all1=true;
        for(int j=0;j<n;j++)if(adj[q][j]){any=true;all0&=u[0][j]>u[1][j];all1&=u[1][j]>u[0][j];}
        if(any&&all0)return 0;if(any&&all1)return 1;
        return u[0][q]>u[1][q]?0:u[1][q]>u[0][q]?1:-1;
    }
    std::array<int,NMAX> distances(int target) const {
        std::array<int,NMAX> ds;ds.fill(50);ds[target]=0;
        int queue[NMAX],lo=0,hi=0;queue[hi++]=target;
        while(lo<hi){int a=queue[lo++];for(int b=0;b<n;b++)if(adj[a][b]&&ds[b]==50){ds[b]=ds[a]+1;queue[hi++]=b;}}
        return ds;
    }
    int next(int a,int b) const {
        auto ds=distances(b);
        for(int j=0;j<n;j++)if(adj[a][j]&&ds[j]<ds[a])return j;
        return a;
    }
    bool canuse(const std::shared_ptr<Triangle>&t,int p,int cost) const {
        if(!t||t->owner!=p||t->initial!=p)return false;
        for(int q:t->v)if(rem[p][q]<cost)return false;
        return true;
    }
    bool near(const std::shared_ptr<Triangle>&t,int q) const {
        for(int a:t->v)if(adj[a][q])return true;return false;
    }
    bool valid(const Action&a,bool strict=true) const {
        if(!strict){if(a.type==ADD)return connectable(a.a,a.d);if(a.type!=SPAWN)return true;}
        if(a.type==MOVE)return a.a!=a.b&&rem[a.player][a.a]>0&&a.amount>0;
        if(!canuse(a.tri,a.player,a.type==SPAWN?0:1))return false;
        if(a.type==ATTACK)return near(a.tri,a.d);
        if(a.type==ADD)return !adj[a.a][a.d]&&connectable(a.a,a.d);
        if(a.type==REMOVE)return adj[a.a][a.d]&&std::find(a.tri->v.begin(),a.tri->v.end(),a.d)==a.tri->v.end();
        return a.type==SPAWN;
    }
    void use(const std::shared_ptr<Triangle>&t,int amount) {
        int p=t->owner;
        if(p<0)throw std::runtime_error("Spending a neutral triangle");
        for(int q:t->v){int take=std::min(amount,u[p][q]);u[p][q]-=take;rem[p][q]-=take;}
        t->cap[p]=false;t->owner=-1;
    }
    void apply(const Action&a) {
        int p=a.player;
        if(a.type==MOVE){int b=next(a.a,a.b),take=std::min(a.amount,rem[p][a.a]);if(b!=a.a){u[p][a.a]-=take;rem[p][a.a]-=take;u[p][b]+=take;}return;}
        use(a.tri,a.type==SPAWN?0:1);
        if(a.type==ATTACK)u[1-p][a.d]=rem[1-p][a.d]=0;
        if(a.type==SPAWN)u[p][a.a]++;
        if(a.type==ADD||a.type==REMOVE){adj[a.a][a.d]=adj[a.d][a.a]=a.type==ADD;triangles();}
    }
    std::vector<Action> parse(const std::string&line,int p) {
        std::vector<Action> out;std::stringstream ss(line);std::string cmd;
        while(std::getline(ss,cmd,';')) {
            std::stringstream is(cmd);std::string name;is>>name;
            for(char &c:name)c=std::toupper(c);
            if(name.empty()||name=="WAIT"||name=="MSG"||name=="TEXT"||name=="LINE"||name=="RECT"||name=="CIRCLE")continue;
            Action a;a.player=p;
            if(name=="MOVE"){a.type=MOVE;if(!(is>>a.a>>a.b>>a.amount)){parse_errors[p]++;continue;}}
            else {a.type=name=="ATTACK"?ATTACK:name=="SPAWN"?SPAWN:name=="ADD_PATH"?ADD:name=="REMOVE_PATH"?REMOVE:-1;
                if(a.type<0||!(is>>a.a>>a.b>>a.c)||(a.type!=SPAWN&&!(is>>a.d))){parse_errors[p]++;continue;}}
            if(a.a<0||a.a>=n||a.b<0||a.b>=n||a.c<0||a.c>=n||a.d<0||a.d>=n){parse_errors[p]++;continue;}
            if(a.type!=MOVE)a.tri=triangle(a.a,a.b,a.c);
            if(valid(a))out.push_back(a);else parse_errors[p]++;
        }
        return out;
    }
    bool finalize() {
        for(int p=0;p<2;p++)for(int q=0;q<n;q++)rem[p][q]=u[p][q];
        for(auto&t:ts)for(int p=0;p<2;p++) {
            if(t->owner>=0)t->cap[p]=t->owner!=p;
            else {bool empty=true;for(int q:t->v)empty&=u[p][q]==0;t->cap[p]=t->cap[p]||empty;}
        }
        bool killed=false;
        if(!surrounded) {
            surrounded=true;bool advantage[2][NMAX]{};
            for(int p=0;p<2;p++)for(int q=0;q<n;q++)advantage[p][q]=u[p][q]>u[1-p][q];
            for(int p=0;p<2;p++)for(int q=0;q<n;q++)if(u[p][q]>0){bool all=true,any=false;
                for(int j=0;j<n;j++)if(adj[q][j]){any=true;all&=advantage[1-p][j];}
                if(any&&all){u[p][q]=0;killed=true;}}
        }
        if(killed)return true; // Java's short-circuit OR defers captures to the next frame.
        bool captured=false;
        for(auto&t:ts){int old=t->owner;for(int p=0;p<2;p++)if(t->cap[p]){
            bool all=true;for(int q:t->v)all&=owner(q)==p;if(all)t->owner=p;}
            captured|=old!=t->owner;}
        if(captured)return true;
        for(auto&t:ts){if(t->owner>=0)score[t->owner]++;t->initial=t->owner;}
        return false;
    }
    void settle(){int count=0;while(finalize())if(++count>20)throw std::runtime_error("Settle loop");}
    void terminal() {
        int army[2]{},income[2]{};for(int p=0;p<2;p++)for(int q=0;q<n;q++)army[p]+=u[p][q];
        for(auto&t:ts)if(t->owner>=0)income[t->owner]++;
        // Evaluate each player in order, matching the referee's terminal score mutation.
        for(int p=0;p<2;p++)if((army[p]==0&&income[p]==0)||(army[p]==1&&income[p]==0&&score[p]<score[1-p])||income[1-p]>=ts.size()*0.8){score[p]=-1;done=true;}
    }
    void step(const std::string&a,const std::string&b,bool finish=true) {
        surrounded=false;auto tasks=parse(a,0);auto other=parse(b,1);tasks.insert(tasks.end(),other.begin(),other.end());
        while(true) {
            tasks.erase(std::remove_if(tasks.begin(),tasks.end(),[&](const Action&t){return !valid(t);}),tasks.end());
            if(tasks.empty())break;
            int pri=10;for(auto&t:tasks)pri=std::min(pri,t.type);
            std::vector<Action> selected,rest;
            for(auto&t:tasks)(t.type==pri?selected:rest).push_back(t);
            auto cost=[&](const Action&t){return t.type==ADD?dist2(t.a,t.d):0;};
            std::stable_sort(selected.begin(),selected.end(),[&](auto&l,auto&r){return cost(l)<cost(r);});
            std::vector<Action> batch;
            for(int p=0;p<2;p++){
                bool stopped=false;
                for(auto&t:selected)if(t.player==p){
                    if(stopped){rest.push_back(t);continue;}
                    if(!valid(t))continue;
                    batch.push_back(t);if(pri!=MOVE&&pri!=SPAWN)stopped=true;
                }
            }
            std::stable_sort(batch.begin(),batch.end(),[&](auto&l,auto&r){return cost(l)<cost(r);});
            for(auto&t:batch)if(valid(t,false)&&((pri!=MOVE&&pri!=SPAWN)||valid(t)))apply(t);
            tasks=std::move(rest);
        }
        turn++;
        if(finish){if(turn>=200)done=true;else{settle();terminal();}}
    }
    void load(std::istream&in) {
        *this=State();in>>n;if(n<1||n>NMAX)throw std::runtime_error("Bad node count");
        for(int i=0;i<n;i++)in>>x[i]>>y[i]>>u[0][i]>>u[1][i];
        int e;in>>e;for(int i=0;i<e;i++){int a,b;in>>a>>b;adj[a][b]=adj[b][a]=true;}
        if(!in)throw std::runtime_error("Bad map");triangles();settle();settle();
    }
    std::string json() const {
        std::ostringstream o;o<<"{\"turn\":"<<turn<<",\"score\":["<<score[0]<<','<<score[1]<<"],\"units\":[";
        for(int q=0;q<n;q++){if(q)o<<',';o<<'['<<u[0][q]<<','<<u[1][q]<<']';}
        o<<"],\"edges\":[";bool first=true;
        for(int a=0;a<n;a++)for(int b=a+1;b<n;b++)if(adj[a][b]){if(!first)o<<',';first=false;o<<'['<<a<<','<<b<<']';}
        o<<"],\"triangles\":[";first=true;
        for(auto&t:ts){if(!first)o<<',';first=false;o<<'['<<t->v[0]<<','<<t->v[1]<<','<<t->v[2]<<','<<t->owner<<','<<t->cap[0]<<','<<t->cap[1]<<']';}
        o<<"],\"done\":"<<(done?"true":"false")<<",\"errors\":["<<parse_errors[0]<<','<<parse_errors[1]<<"]}";return o.str();
    }
};
}

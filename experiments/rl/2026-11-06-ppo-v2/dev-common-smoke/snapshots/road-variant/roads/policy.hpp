// Shared features and resource-aware decoder for training and native inference.
#pragma once
#include "../sim/simulator.hpp"
#include <functional>
#include <fstream>
#include <numeric>

namespace roads_model {
using namespace rl;
constexpr int FEATURES=128;
struct Candidate {int kind=2,src=0,dst=0;std::shared_ptr<Triangle> tri;};
struct Group {std::vector<std::array<float,FEATURES>> x;int label=0,phase=0;};
struct Decoder {
    const State&s;int p,style,decisions=0;
    int pending[NMAX]{},available[NMAX]{},ds[NMAX][NMAX]{};
    int army[2]{},income[2]{},orientation=1;
    std::vector<std::string> output;
    Decoder(const State&state,int player,int teacher):s(state),p(player),style(teacher){
        float ownx=0,otherx=0;
        for(int q=0;q<s.n;q++){pending[q]=available[q]=s.u[p][q];for(int i=0;i<2;i++)army[i]+=s.u[i][q];ownx+=s.u[p][q]*s.x[q];otherx+=s.u[1-p][q]*s.x[q];auto d=s.distances(q);for(int j=0;j<s.n;j++)ds[q][j]=d[j];}
        for(auto&t:s.ts)if(t->owner>=0)income[t->owner]++;
        orientation=ownx/std::max(1,army[p])>otherx/std::max(1,army[1-p])?-1:1;
    }
    std::array<float,26> node(int q)const {
        std::array<float,26> f{};int k=0;
        auto put=[&](float v){f[k++]=std::clamp(v,-5.f,5.f);};
        put(s.u[p][q]/10.f);put(s.u[1-p][q]/10.f);put(std::log1p(s.u[p][q])/3);put(std::log1p(s.u[1-p][q])/3);
        put(pending[q]/10.f);put(available[q]/10.f);put((pending[q]-s.u[1-p][q])/10.f);
        put(pending[q]>s.u[1-p][q]);put(pending[q]==s.u[1-p][q]);put(pending[q]<s.u[1-p][q]);
        int deg=0,nu=0,ne=0,nc=0,ec=0;
        for(int j=0;j<s.n;j++)if(s.adj[q][j]){deg++;nu+=pending[j];ne+=s.u[1-p][j];nc+=pending[j]>s.u[1-p][j];ec+=pending[j]<s.u[1-p][j];}
        put(deg/8.f);put(nu/20.f);put(ne/20.f);put(nc/8.f);put(ec/8.f);
        int owned=0,enemy=0,neutral=0,blocked=0,ready[3]{},need=20;
        for(auto&t:s.ts)if(std::find(t->v.begin(),t->v.end(),q)!=t->v.end()){
            owned+=t->owner==p;enemy+=t->owner==1-p;neutral+=t->owner==-1&&t->cap[p];blocked+=!t->cap[p];
            int r=0,cost=0;for(int a:t->v)if(a!=q){r+=pending[a]>s.u[1-p][a];cost+=std::max(0,s.u[1-p][a]+1-pending[a]);}
            if(t->cap[p]){ready[r]++;need=std::min(need,cost);}
        }
        put(owned/6.f);put(enemy/6.f);put(neutral/6.f);put(blocked/6.f);
        put(ready[2]/6.f);put(ready[1]/6.f);put(ready[0]/6.f);put(need/6.f);
        int front=50;for(int j=0;j<s.n;j++)if(s.u[1-p][j])front=std::min(front,ds[q][j]);
        put(front/10.f);put(orientation*(s.x[q]-960)/960.f);put(orientation*(s.y[q]-540)/540.f);
        return f;
    }
    std::array<float,3> road_features(const Candidate&c)const {
        std::array<float,3> out{};
        if(c.kind!=5&&c.kind!=6)return out;
        auto add=[&](int a,int b,int q,float sign){
            int friendly=0,enemy=0;
            for(int v:{a,b,q}){
                int own=pending[v];
                if(c.tri&&std::find(c.tri->v.begin(),c.tri->v.end(),v)!=c.tri->v.end())own--;
                friendly+=own>s.u[1-p][v];enemy+=own<s.u[1-p][v];
            }
            out[0]+=sign/2.f;out[1]+=sign*friendly/6.f;out[2]+=sign*enemy/6.f;
        };
        if(c.kind==5){
            for(int q=0;q<s.n;q++)if(q!=c.src&&q!=c.dst&&s.adj[c.src][q]&&s.adj[c.dst][q]){
                bool empty=true;for(int z=0;z<s.n;z++)if(s.inside(z,c.src,c.dst,q)){empty=false;break;}
                if(empty)add(c.src,c.dst,q,1);
            }
        }else{
            for(auto&t:s.ts){
                bool a=std::find(t->v.begin(),t->v.end(),c.src)!=t->v.end();
                bool b=std::find(t->v.begin(),t->v.end(),c.dst)!=t->v.end();
                if(a&&b)for(int q:t->v)if(q!=c.src&&q!=c.dst)add(c.src,c.dst,q,-1);
            }
        }
        return out;
    }
    std::array<float,FEATURES> features(const Candidate&c)const {
        std::array<float,FEATURES> f{};int k=0;
        auto put=[&](float v){if(k>=FEATURES)throw std::runtime_error("Feature overflow");f[k++]=std::clamp(v,-5.f,5.f);};
        put(s.turn/200.f);put(s.score[p]/2000.f);put(s.score[1-p]/2000.f);put((s.score[p]-s.score[1-p])/2000.f);
        put(army[p]/50.f);put(army[1-p]/50.f);put((army[p]-army[1-p])/50.f);
        put(income[p]/20.f);put(income[1-p]/20.f);put(s.ts.size()/40.f);put(s.n/50.f);
        put(std::accumulate(pending,pending+s.n,0)/50.f);put(decisions/100.f);
        if(style==3){for(float v:road_features(c))put(v);}
        else{put(style==0?1.f:style==2?.5f:0.f);put(style==1?1.f:style==2?.5f:0.f);put(1);}
        for(int j=0;j<7;j++)put(c.kind==j);
        auto a=node(c.src),b=node(c.dst);for(float v:a)put(v);for(float v:b)put(v);
        std::array<float,26> mean{};
        if(c.tri)for(int q:c.tri->v){auto v=node(q);for(int j=0;j<26;j++)mean[j]+=v[j]/3;}
        for(float v:mean)put(v);
        put(std::sqrt(s.dist2(c.src,c.dst))/400);put(ds[c.src][c.dst]/10.f);
        put(orientation*(s.x[c.dst]-s.x[c.src])/400.f);put(orientation*(s.y[c.dst]-s.y[c.src])/400.f);
        put(c.tri?c.tri->cap[p]:0);put(c.tri?c.tri->cap[1-p]:0);
        int minunits=20; if(c.tri)for(int q:c.tri->v)minunits=std::min(minunits,available[q]);put(c.tri?minunits/5.f:0);
        // Distance to missing corners, grouped by ownership and completed corners.
        // These are observations, not action-selection scores.
        int from[6],to[6];std::fill(from,from+6,50);std::fill(to,to+6,50);
        float before=0,after=0,reset_before=0,reset_after=0;
        for(auto&t:s.ts){
            int ready=0;for(int q:t->v)ready+=pending[q]>s.u[1-p][q];
            if(t->cap[p]&&t->owner!=p){
                int idx=(t->owner==1-p?3:0)+std::min(2,ready);
                for(int q:t->v)if(pending[q]<=s.u[1-p][q]){from[idx]=std::min(from[idx],ds[c.src][q]);to[idx]=std::min(to[idx],ds[c.dst][q]);}
            }
            bool pre=true,post=true,empty_pre=true,empty_post=true;
            for(int q:t->v){int v=pending[q];if(c.kind==1){v-=(q==c.src);v+=(q==c.dst);}if(c.kind==3)v+=(q==c.dst);
                pre&=pending[q]>s.u[1-p][q];post&=v>s.u[1-p][q];empty_pre&=pending[q]==0;empty_post&=v==0;}
            if(t->cap[p]&&t->owner!=p){before+=pre;after+=post;}
            if(!t->cap[p]){reset_before+=empty_pre;reset_after+=empty_post;}
        }
        for(int j=0;j<6;j++){put(to[j]/10.f);put((from[j]-to[j])/5.f);}
        put(before/5);put(after/5);put((after-before)/3);put(reset_before/5);put(reset_after/5);put((reset_after-reset_before)/3);
        put(c.kind==4?s.u[1-p][c.dst]/10.f:0);put(c.kind==4?(s.u[1-p][c.dst]>0):0);
        if(k!=FEATURES)throw std::runtime_error("Feature dimension mismatch: "+std::to_string(k));
        return f;
    }
    std::vector<Candidate> spend(const std::shared_ptr<Triangle>&t)const {
        std::vector<Candidate> cs{{2,t->v[0],t->v[0],t}};
        for(int q:t->v)cs.push_back({3,q,q,t});
        bool enough=true;for(int q:t->v)enough&=available[q]>0;
        if(!enough)return cs;
        for(int q=0;q<s.n;q++)if(s.near(t,q))cs.push_back({4,t->v[0],q,t});
        for(int a:t->v)for(int q=0;q<s.n;q++){
            if(a==q)continue;
            if(!s.adj[a][q]&&s.connectable(a,q))cs.push_back({5,a,q,t});
            if(s.adj[a][q]&&std::find(t->v.begin(),t->v.end(),q)==t->v.end())cs.push_back({6,a,q,t});
        }
        return cs;
    }
    void choose(const Candidate&c){
        decisions++;std::ostringstream o;
        if(c.kind<=1){available[c.src]--;if(c.kind==1){pending[c.src]--;pending[c.dst]++;o<<"MOVE "<<c.src<<' '<<c.dst<<" 1";}}
        if(c.kind>=3){
            if(c.kind==3){pending[c.dst]++;o<<"SPAWN ";}
            if(c.kind==4)o<<"ATTACK ";if(c.kind==5)o<<"ADD_PATH ";if(c.kind==6)o<<"REMOVE_PATH ";
            int first=c.kind==4?c.tri->v[0]:c.src;o<<first;
            for(int q:c.tri->v)if(q!=first)o<<' '<<q;
            if(c.kind>=4){o<<' '<<c.dst;for(int q:c.tri->v){pending[q]--;available[q]--;}}
        }
        if(!o.str().empty())output.push_back(o.str());
    }
    using Chooser=std::function<int(const std::vector<Candidate>&,const Decoder&)>;
    std::string run(const Chooser&pick){
        for(auto&t:s.ts)if(t->owner==p){auto cs=spend(t);choose(cs.at(pick(cs,*this)));}
        for(int a=0;a<s.n;a++)while(available[a]>0){std::vector<Candidate> cs{{0,a,a,nullptr}};for(int b=0;b<s.n;b++)if(s.adj[a][b])cs.push_back({1,a,b,nullptr});choose(cs.at(pick(cs,*this)));}
        if(output.empty())return "WAIT";std::string result;
        for(auto&cmd:output){if(!result.empty())result+=';';result+=cmd;}return result;
    }
};

inline std::vector<Group> labels(State&s,int p,int style,const std::string&line,std::string*encoded=nullptr){
    int old=s.parse_errors[p];auto actions=s.parse(line,p);
    if(s.parse_errors[p]!=old)throw std::runtime_error("teacher_parse_error");
    std::vector<std::pair<std::shared_ptr<Triangle>,Action>> spends;
    std::vector<int> destinations[NMAX];int costs[NMAX]{};
    for(auto&a:actions)if(a.type!=MOVE){
        for(auto&v:spends)if(v.first==a.tri)throw std::runtime_error("repeated_triangle_spend");
        spends.push_back({a.tri,a});if(a.type!=SPAWN)for(int q:a.tri->v)costs[q]++;
    }
    for(int a=0;a<s.n;a++)if(costs[a]>s.u[p][a])throw std::runtime_error("shared_corner_overspend");
    for(auto&a:actions)if(a.type==MOVE){
        int dest=s.next(a.a,a.b),count=std::min(a.amount,s.u[p][a.a]-costs[a.a]-int(destinations[a.a].size()));
        if(count<0)throw std::runtime_error("move_resource_conflict");
        for(int j=0;j<count;j++)destinations[a.a].push_back(dest);
    }
    for(int a=0;a<s.n;a++){
        while(int(destinations[a].size())<s.u[p][a]-costs[a])destinations[a].push_back(a);
        std::sort(destinations[a].begin(),destinations[a].end());
    }
    int used[NMAX]{};std::vector<Group> groups;Decoder dec(s,p,style);
    std::string plan=dec.run([&](const std::vector<Candidate>&cs,const Decoder&d){
        int target=0;
        if(cs[0].tri){
            for(auto&v:spends)if(v.first==cs[0].tri){
                const auto&a=v.second;int kind=a.type==SPAWN?3:a.type==ATTACK?4:a.type==ADD?5:6;
                int dst=a.type==SPAWN?a.a:a.d;target=-1;
                for(int j=0;j<int(cs.size());j++)if(cs[j].kind==kind&&cs[j].dst==dst&&(kind==4||cs[j].src==a.a)){target=j;break;}
            }
        }else{
            int a=cs[0].src,dst=destinations[a].at(used[a]++);target=-1;
            for(int j=0;j<int(cs.size());j++)if(cs[j].dst==dst){target=j;break;}
        }
        if(target<0)throw std::runtime_error("unsupported_teacher_action");
        Group g;g.label=target;g.phase=cs[0].tri?1:0;
        for(auto&c:cs)g.x.push_back(d.features(c));groups.push_back(std::move(g));return target;
    });if(encoded)*encoded=plan;return groups;
}

struct Network {
    std::vector<int> dims;
    std::vector<std::vector<float>> weights,bias;
    void load(const std::string&path){std::ifstream in(path);std::string magic;int layers;in>>magic>>layers;
        if(magic!="TRYANGLE_MLP_V1"||layers<1||layers>8)throw std::runtime_error("Invalid weights");
        dims.resize(layers+1);for(int&d:dims)in>>d;if(dims.front()!=FEATURES||dims.back()!=1)throw std::runtime_error("Invalid dimensions");
        for(int l=0;l<layers;l++){weights.emplace_back(dims[l]*dims[l+1]);bias.emplace_back(dims[l+1]);for(float&v:weights.back())in>>v;for(float&v:bias.back())in>>v;}
        if(!in)throw std::runtime_error("Truncated weights");
    }
    float evaluate(const std::array<float,FEATURES>&x)const {
        float a[256]{},b[256]{};std::copy(x.begin(),x.end(),a);
        for(int l=0;l<int(weights.size());l++){
            for(int j=0;j<dims[l+1];j++){float v=bias[l][j];const float*w=&weights[l][j*dims[l]];
                for(int k=0;k<dims[l];k++)v+=w[k]*a[k];b[j]=l+1==int(weights.size())?v:std::max(0.f,v);}
            std::copy(b,b+dims[l+1],a);
        }return a[0];
    }
    std::string act(const State&s,int p,int style=2)const {
        Decoder d(s,p,style);return d.run([&](const std::vector<Candidate>&cs,const Decoder&dec){
            int best=0;float value=-1e30;for(int j=0;j<int(cs.size());j++){float v=evaluate(dec.features(cs[j]));if(v>value){best=j;value=v;}}return best;});
    }
};
}

// Local benchmark: port of eulerscheZahl's config/level1/Boss.cs.
// Source commit b6913124a10de328316ff42906448a18cb948431.
// Same greedy three-corner logic; mt19937 replaces C# Random and debug drawing omitted.
// This is NOT an exact copy of the live contest boss. Never submit as our solution.
#include <algorithm>
#include <iostream>
#include <queue>
#include <random>
#include <string>
#include <vector>
using namespace std;
struct T { int v[3],owner,can,opp; };
int main(){
    ios::sync_with_stdio(false); cin.tie(nullptr); mt19937 rng(0);
    int n; if(!(cin>>n))return 0;
    for(int i=0,a,b,c;i<n;i++)cin>>a>>b>>c;
    int score,other;
    while(cin>>score>>other){
        vector<int> units(n), enemies(n); vector<vector<int>> adj(n),d(n,vector<int>(n,1000));
        vector<int> pool;
        for(int i=0,id,a,b;i<n;i++){cin>>id>>a>>b;units[id]=a;enemies[id]=b;for(int j=0;j<a;j++)pool.push_back(id);}
        int k;cin>>k;for(int i=0,a,b;i<k;i++){cin>>a>>b;adj[a].push_back(b);adj[b].push_back(a);}
        cin>>k;vector<T> ts(k);for(auto &t:ts)cin>>t.v[0]>>t.v[1]>>t.v[2]>>t.owner>>t.can>>t.opp;
        cin>>k;for(int i=0,a,b;i<k;i++)cin>>a>>b;
        for(int s=0;s<n;s++){queue<int> q;q.push(s);d[s][s]=0;while(!q.empty()){int x=q.front();q.pop();for(int y:adj[x])if(d[s][y]==1000){d[s][y]=d[s][x]+1;q.push(y);}}}
        vector<string> out={"WAIT"};vector<int> moving;
        if(pool.size()>=3){
            auto chosen=pool;while(chosen.size()>3)chosen.erase(chosen.begin()+rng()%chosen.size());
            int best=1000;
            for(auto t:ts)if(t.owner!=0&&t.can){
                auto free=chosen;vector<int> sources;int cost=0;
                for(int target:t.v){int idx=0;for(int j=1;j<(int)free.size();j++)if(d[target][free[j]]<d[target][free[idx]])idx=j;sources.push_back(free[idx]);free.erase(free.begin()+idx);cost=max(cost,d[target][sources.back()]);}
                if(cost<best){best=cost;out={"WAIT"};moving=sources;for(int j=0;j<3;j++)if(sources[j]!=t.v[j]&&!adj[sources[j]].empty()){
                    int hop=adj[sources[j]][0];for(int v:adj[sources[j]])if(d[v][t.v[j]]<d[hop][t.v[j]])hop=v;
                    out.push_back("MOVE "+to_string(sources[j])+" "+to_string(hop)+" 1");
                }}
            }
        }
        if((int)pool.size()<n)for(auto t:ts)if(t.owner==0){out.push_back("SPAWN "+to_string(t.v[0])+" "+to_string(t.v[1])+" "+to_string(t.v[2]));break;}
        for(int s:moving){auto it=find(pool.begin(),pool.end(),s);if(it!=pool.end())pool.erase(it);}
        for(int s:pool)if(!adj[s].empty())out.push_back("MOVE "+to_string(s)+" "+to_string(adj[s][rng()%adj[s].size()])+" 1");
        for(size_t i=0;i<out.size();i++)cout<<(i?";":"")<<out[i];cout<<endl;
    }
}

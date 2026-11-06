// Simple TryAngle Catch bot: capture nearby triangles, selectively spawn, defend.
// Only MOVE/SPAWN/WAIT. No training, opponent code, or network access.
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <iostream>
#include <numeric>
#include <sstream>
#include <string>
#include <vector>
using namespace std;
constexpr int MAXN = 52, INF = 10000;
struct Triangle { array<int,3> v; int owner, can, oppCan; };
struct Assignment { int from, target, amount; };
struct Plan { double cost=1e9; vector<Assignment> jobs; vector<int> left; };
int n, mine[MAXN], enemy[MAXN], dista[MAXN][MAXN], nextHop[MAXN][MAXN];
vector<int> adj[MAXN];
vector<Triangle> triangles;

int owner(int v) {
    bool ours=!adj[v].empty(), theirs=ours;
    for (int x:adj[v]) { ours &= mine[x]>enemy[x]; theirs &= enemy[x]>mine[x]; }
    if (ours) return 0;
    if (theirs) return 1;
    return mine[v]>enemy[v]?0:(enemy[v]>mine[v]?1:-1);
}
void paths() {
    for (int i=0;i<n;i++) for(int j=0;j<n;j++) {
        dista[i][j]=i==j?0:INF; nextHop[i][j]=-1;
    }
    for (int i=0;i<n;i++) for(int j:adj[i]) { dista[i][j]=1; nextHop[i][j]=j; }
    for (int k=0;k<n;k++) for (int i=0;i<n;i++) for (int j=0;j<n;j++)
        if (dista[i][k]+dista[k][j]<dista[i][j]) {
            dista[i][j]=dista[i][k]+dista[k][j]; nextHop[i][j]=nextHop[i][k];
        }
}

// Try all six orders of the three corners, assigning the nearest available troops.
Plan assign(const Triangle &t, const vector<int> &available, const vector<int> &held) {
    Plan best;
    array<int,3> perm={0,1,2};
    do {
        auto left=available;
        vector<Assignment> jobs;
        double sum=0, farthest=0;
        bool feasible=true;
        for (int k:perm) {
            int target=t.v[k], need=max(0,enemy[target]+1-held[target]);
            // Surrounding control is stable only if those units are not being moved.
            for (int u=0;u<need;u++) {
                int source=-1; double lowest=1e9;
                for (int s=0;s<n;s++) if (left[s]>0 && dista[s][target]<INF) {
                    double c=dista[s][target];
                    int hop=nextHop[s][target];
                    if (s!=target && hop>=0 && enemy[hop]>=mine[hop]+1) c+=2;
                    if (c<lowest) { lowest=c; source=s; }
                }
                if (source<0) { feasible=false; break; }
                left[source]--; jobs.push_back({source,target,1});
                sum+=lowest; farthest=max(farthest,(double)dista[source][target]);
            }
            if (!feasible) break;
        }
        double c=2*farthest+0.6*sum;
        if (feasible && c<best.cost) best={c,jobs,left};
    } while(next_permutation(perm.begin(),perm.end()));
    return best;
}

int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    if (!(cin>>n) || n<=0 || n>MAXN) return 0;
    for (int i=0,id,x,y;i<n;i++) if (!(cin>>id>>x>>y)) return 0;
    array<int,3> previous={-1,-1,-1};
    int turn=0;
    int myScore, oppScore;
    while (cin>>myScore>>oppScore) {
        auto started=chrono::steady_clock::now();
        turn++;
        for (int i=0;i<n;i++) { mine[i]=enemy[i]=0; adj[i].clear(); }
        for (int i=0,id,a,b;i<n;i++) {
            if (!(cin>>id>>a>>b) || id<0 || id>=n) return 0;
            mine[id]=a; enemy[id]=b;
        }
        int count; if (!(cin>>count)) return 0;
        for (int i=0,a,b;i<count;i++) {
            if (!(cin>>a>>b)) return 0;
            adj[a].push_back(b); adj[b].push_back(a);
        }
        if (!(cin>>count)) return 0;
        triangles.clear();
        for (int i=0;i<count;i++) {
            Triangle t;
            if (!(cin>>t.v[0]>>t.v[1]>>t.v[2]>>t.owner>>t.can>>t.oppCan)) return 0;
            triangles.push_back(t);
        }
        if (!(cin>>count)) return 0;
        for (int i=0,a,b;i<count;i++) if (!(cin>>a>>b)) return 0;
        paths();
        vector<int> free(mine,mine+n), held(n,0), enemyDistance(n,INF);
        int total=accumulate(free.begin(),free.end(),0), owned=0;
        vector<bool> onOwned(n,false);
        for (const auto &t:triangles) if(t.owner==0) {
            owned++; for(int v:t.v) onOwned[v]=true;
        }
        for(int v=0;v<n;v++) for(int e=0;e<n;e++) if(enemy[e])
            enemyDistance[v]=min(enemyDistance[v],dista[v][e]);
        // Keep one guard on exposed owned corners, but retain three mobile troops.
        int reserveBudget=max(0,total-3);
        for(int v=0;v<n;v++) if(onOwned[v] && enemyDistance[v]<=1 && mine[v]>enemy[v]) {
            int keep=min({mine[v],enemy[v]+1,reserveBudget});
            held[v]+=keep; free[v]-=keep; reserveBudget-=keep;
        }

        vector<Assignment> jobs;
        vector<bool> selected(triangles.size(),false);
        int mainGoal=-1;
        for(int batch=0;batch<min(total/3+1,12);batch++) {
            int bestIndex=-1; double bestValue=-1e9; Plan best;
            for(int k=0;k<(int)triangles.size();k++) {
                const auto &t=triangles[k];
                if(selected[k] || t.owner==0 || !t.can) continue;
                Plan candidate=assign(t,free,held);
                if(candidate.cost>=1e8) continue;
                double opposition=0; for(int v:t.v) opposition+=enemy[v];
                double value=(t.owner==1?26.0:20.0)-candidate.cost-2*opposition;
                if(t.v==previous) value+=1.5;
                if(value>bestValue) { bestValue=value; bestIndex=k; best=candidate; }
            }
            if(bestIndex<0) break;
            if(mainGoal<0) mainGoal=bestIndex;
            selected[bestIndex]=true;
            jobs.insert(jobs.end(),best.jobs.begin(),best.jobs.end());
            free=best.left;
            // Assigned units stay reserved; later goals must use different troops.
        }
        if(mainGoal>=0) previous=triangles[mainGoal].v;

        // Unassigned troops support reachable, unowned triangles near the frontier.
        for(int s=0;s<n;s++) if(free[s]>0) {
            int target=-1; double best=1e9;
            for(const auto &t:triangles) if(t.owner!=0 && t.can) for(int v:t.v) {
                if(s==v || dista[s][v]>=INF) continue;
                double cost=dista[s][v]+2*enemy[v]+0.5*mine[v];
                if(cost<best) { best=cost; target=v; }
            }
            if(target>=0) jobs.push_back({s,target,free[s]});
        }

        int move[MAXN][MAXN]={}, planned[MAXN]={};
        for(const auto &job:jobs) {
            if(job.from==job.target) continue;
            int hop=nextHop[job.from][job.target];
            int amount=min(job.amount,mine[job.from]-held[job.from]-planned[job.from]);
            if(hop>=0 && amount>0) { move[job.from][hop]+=amount; planned[job.from]+=amount; }
        }
        vector<string> commands;
        for(int s=0;s<n;s++) for(int t=0;t<n;t++) if(move[s][t]>0)
            commands.push_back("MOVE "+to_string(s)+" "+to_string(t)+" "+to_string(move[s][t]));

        int desired=turn<150?n:(turn<175?n/2:3);
        // Early reinforcement trades one income triangle for one permanent troop.
        vector<bool> spent(triangles.size(),false);
        vector<int> spawned(n,0);
        int remainingOwned=owned, created=0;
        while(total+created<desired && remainingOwned>0 && (remainingOwned>=2 || total+created<4)) {
            int bestTri=-1, spawnAt=-1; double best=-1e9;
            for(int k=0;k<(int)triangles.size();k++) if(triangles[k].owner==0 && !spent[k]) {
                for(int v:triangles[k].v) {
                    int goalDist=INF;
                    for(const auto &t:triangles) if(t.owner!=0 && t.can)
                        for(int w:t.v) goalDist=min(goalDist,dista[v][w]);
                    // Avoid spawning into a hostile stack; prefer useful frontier corners.
                    double val=-goalDist-2*enemy[v]-0.2*(mine[v]+spawned[v]);
                    if(val>best) {best=val;bestTri=k;spawnAt=v;}
                }
            }
            if(bestTri>=0) {
                string c="SPAWN "+to_string(spawnAt);
                for(int v:triangles[bestTri].v) if(v!=spawnAt) c+=" "+to_string(v);
                commands.push_back(c);
                spent[bestTri]=true; spawned[spawnAt]++; created++; remainingOwned--;
            } else break;
        }
        if(commands.empty()) commands.push_back("WAIT");
        for(size_t i=0;i<commands.size();i++) cout<<(i?";":"")<<commands[i];
        cout<<endl;
        auto us=chrono::duration_cast<chrono::microseconds>(chrono::steady_clock::now()-started).count();
        cerr<<"turn="<<turn<<" units="<<total<<" triangles="<<owned<<" plan_us="<<us<<'\n';
    }
}

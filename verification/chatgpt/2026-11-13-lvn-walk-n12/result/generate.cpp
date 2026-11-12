// Independent connected simple subcubic graph generator, n<=12.
// Construct every connected n-vertex graph by appending a non-cut vertex
// to a connected (n-1)-vertex graph; remove isomorphic duplicates with
// intrinsic graph invariants and exact adjacency-preserving backtracking.
#include <bits/stdc++.h>
using namespace std;
using ull=uint64_t;
struct Graph {
    int n=0;
    array<uint16_t,12> a{};
    array<ull,12> colors{};
    string sig;
};
static ull mix(ull v){v+=0x9e3779b97f4a7c15ULL;v=(v^(v>>30))*0xbf58476d1ce4e5b9ULL;v=(v^(v>>27))*0x94d049bb133111ebULL;return v^(v>>31);}
static int pc(int x){return __builtin_popcount((unsigned)x);}
static void colorize(Graph& g){
    array<ull,12> c{},d{};
    for(int i=0;i<g.n;i++){
        int degree=pc(g.a[i]), triangle=0;
        int nbrmask=g.a[i];
        for(int j=0;j<g.n;j++) if(nbrmask>>j&1) triangle+=pc(g.a[j]&nbrmask);
        triangle/=2;
        // Profile of distance layers and neighbour degrees is invariant.
        int reach=(1<<i), frontier=reach;
        ull h=mix(degree+257*triangle);
        for(int k=1;k<g.n;k++){
            int nxt=0;
            for(int j=0;j<g.n;j++) if(frontier>>j&1) nxt |= g.a[j];
            frontier=nxt & ~reach;
            reach |= frontier;
            h=mix(h^mix((ull)(pc(frontier)+17*k)));
        }
        int degcnt[4]={};
        for(int j=0;j<g.n;j++) if(g.a[i]>>j&1) degcnt[pc(g.a[j])]++;
        for(int j=1;j<=3;j++)h=mix(h^(degcnt[j]+31*j));
        c[i]=h;
    }
    for(int iter=0;iter<g.n;iter++){
        bool same=true;
        for(int i=0;i<g.n;i++){
            ull ns[3]={};int z=0;
            for(int j=0;j<g.n;j++)if(g.a[i]>>j&1)ns[z++]=c[j];
            sort(ns,ns+z);
            ull h=mix(c[i]^mix(z));
            for(int j=0;j<z;j++)h=mix(h^mix(ns[j]+j));
            d[i]=h;
            if(d[i]!=c[i]) same=false;
        }
        c=d;
        // Usually 4 rounds suffice; n rounds keep fully invariant.
        (void)same;
    }
    g.colors=c;
    vector<ull> sorted(c.begin(),c.begin()+g.n);
    sort(sorted.begin(),sorted.end());
    g.sig.resize(g.n*8);
    for(int i=0;i<g.n;i++)memcpy(g.sig.data()+8*i,&sorted[i],8);
}
static bool isomorphic(const Graph& g,const Graph& h){
    int n=g.n;
    int mapv[12], used=0;fill(mapv,mapv+12,-1);
    auto dfs=[&](auto&& self,int depth,int usedmask)->bool{
        if(depth==n)return true;
        int bi=-1,bnum=999,bconstraint=-1;
        uint16_t bestCandidates=0;
        for(int i=0;i<n;i++)if(mapv[i]<0){
            uint16_t poss=0;int constraint=0;
            for(int j=0;j<n;j++)if(mapv[j]>=0)constraint+=bool(g.a[i]>>j&1);
            for(int k=0;k<n;k++)if(!(usedmask>>k&1)&&g.colors[i]==h.colors[k]){
                bool good=true;
                for(int j=0;j<n;j++)if(mapv[j]>=0 && bool(g.a[i]>>j&1)!=bool(h.a[k]>>mapv[j]&1)){good=false;break;}
                if(good)poss|=1<<k;
            }
            int nposs=pc(poss);
            if(nposs==0)return false;
            if(nposs<bnum||(nposs==bnum&&constraint>bconstraint)){
                bnum=nposs;bi=i;bestCandidates=poss;bconstraint=constraint;
            }
        }
        while(bestCandidates){
            int k=__builtin_ctz(bestCandidates);bestCandidates&=bestCandidates-1;
            mapv[bi]=k;
            if(self(self,depth+1,usedmask|(1<<k)))return true;
            mapv[bi]=-1;
        }
        return false;
    };
    return dfs(dfs,0,0);
}
static void writegraphs(const vector<Graph>& gs,int n,const string& dir){
    ofstream f(dir+"/graphs_n"+to_string(n)+".txt");
    for(const auto& g:gs){
        for(int i=0;i<g.n;i++){
            if(i)f<<' ';
            f<<g.a[i];
        }
        f<<'\n';
    }
}
int main(int argc,char**argv){
    if(argc<3){cerr<<"usage: generate OUTDIR MAX_N\n";return 2;}
    string out=argv[1]; int maxn=stoi(argv[2]);
    if(maxn<1||maxn>12)return 2;
    vector<Graph> gs(1);gs[0].n=1; colorize(gs[0]);
    writegraphs(gs,1,out);
    cout<<"n=1 graphs=1"<<endl;
    const int reference[]={0,1,1,2,6,10,29,64,194,531,1733,5524,19430};
    for(int n=2;n<=maxn;n++){
        vector<Graph> next;
        unordered_map<string,vector<int>> groups;
        size_t candcount=0, collisioncount=0;
        for(const Graph& p:gs){
            vector<int> elig;
            for(int v=0;v<n-1;v++)if(pc(p.a[v])<3)elig.push_back(v);
            int e=elig.size();
            for(int mask=1;mask<(1<<e);mask++){
                int cnt=pc(mask);if(cnt>3)continue;
                Graph q;q.n=n;q.a=p.a;
                for(int j=0;j<e;j++)if(mask>>j&1){
                    int v=elig[j];q.a[v]|=1<<(n-1);q.a[n-1]|=1<<v;
                }
                candcount++;
                colorize(q);
                auto& ids=groups[q.sig];
                bool duplicate=false;
                for(int k:ids){collisioncount++;if(isomorphic(q,next[k])){duplicate=true;break;}}
                if(!duplicate){ids.push_back((int)next.size());next.push_back(move(q));}
            }
        }
        gs=move(next);writegraphs(gs,n,out);
        cout<<"n="<<n<<" graphs="<<gs.size()<<" expected="<<reference[n]
            <<" candidates="<<candcount<<" isomorphism_tests="<<collisioncount
            <<" match="<<(gs.size()==(unsigned)reference[n])<<endl;
        if(gs.size()!=(unsigned)reference[n])cerr<<"COUNT MISMATCH at n="<<n<<"\n";
    }
}

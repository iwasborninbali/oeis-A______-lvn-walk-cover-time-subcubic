// Exact LFV-v state search. This program is not used by check.py.
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>
using Key = unsigned __int128;
struct Hash {
    static uint64_t mix(uint64_t x) {
        x += 0x9e3779b97f4a7c15ULL;
        x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
        x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
        return x ^ (x >> 31);
    }
    size_t operator()(Key x) const {
        return mix(uint64_t(x)) ^ mix(uint64_t(x >> 64));
    }
};
struct Value { int time, frequency; };
int n;
std::vector<int> nbr[16];
std::unordered_map<Key, Value, Hash> memo;
int count(Key c, int v) { return int((c >> (8*v)) & 255); }
Key increment(Key c, int v) {
    if (count(c,v)==255) throw std::runtime_error("counter packing exceeded");
    return c + (Key(1) << (8*v));
}
Value visit(int v, Key c) {
    bool covered=true; int largest=0;
    for (int w=0; w<n; ++w) {
        int f=count(c,w); covered &= f>0; largest=std::max(largest,f);
    }
    if (covered) return {0,0};
    Key key=c | (Key(v) << (8*n));
    auto old=memo.find(key); if (old!=memo.end()) return old->second;
    int least=256;
    for (int w:nbr[v]) least=std::min(least,count(c,w));
    Value answer{0,largest};
    for (int w:nbr[v]) if (count(c,w)==least) {
        Value child=visit(w,increment(c,w));
        answer.time=std::max(answer.time,1+child.time);
        answer.frequency=std::max(answer.frequency,child.frequency);
    }
    memo.emplace(key,answer); return answer;
}
std::vector<int> trace(int v, bool frequency) {
    Key c=Key(1)<<(8*v);
    std::vector<int> path{v};
    for (;;) {
        bool covered=true;
        for(int w=0;w<n;++w) covered &= count(c,w)>0;
        if(covered) return path;
        Value goal=visit(v,c);
        int least=256; for(int w:nbr[v]) least=std::min(least,count(c,w));
        int best=-1;
        // For a frequency witness choose a child retaining the maximum, then
        // finish with time-maximising choices once the target has been attained.
        for(int w:nbr[v]) if(count(c,w)==least) {
            Value child=visit(w,increment(c,w));
            if ((!frequency && child.time+1==goal.time) ||
                (frequency && child.frequency==goal.frequency)) {best=w;break;}
        }
        if(best<0) {
            for(int w:nbr[v]) if(count(c,w)==least &&
                visit(w,increment(c,w)).time+1==goal.time) {best=w;break;}
        }
        v=best;c=increment(c,v);path.push_back(v);
    }
}
void array(std::ostream& out,const std::vector<int>& a) {
    out<<'[';for(size_t i=0;i<a.size();++i){if(i)out<<',';out<<a[i];}out<<']';
}
void witness(const std::string& filename,const std::string& word,int root,int value,bool freq) {
    std::ofstream out(filename);
    out<<"{\"n\":"<<n<<",\"word\":\""<<word<<"\",\"root\":"<<root
       <<",\"objective\":\""<<(freq?"frequency":"time")<<"\",\"value\":"<<value<<",\"path\":";
    array(out,trace(root,freq));out<<"}\n";
}
int main(int argc,char**argv) {
    if(argc!=4) {std::cerr<<"usage: search n catalog.txt output_directory\n";return 1;}
    n=std::stoi(argv[1]);if(n<1||n>15)throw std::runtime_error("unsupported n");
    std::filesystem::create_directories(argv[3]);
    std::string folder=argv[3];
    std::ifstream in(argv[2]);if(!in)throw std::runtime_error("missing catalogue");
    std::ofstream out(folder+"/n"+std::to_string(n)+".jsonl");
    std::string word;int graphs=0,worst=-1,worstf=-1;uint64_t total=0,peak=0;
    auto start=std::chrono::steady_clock::now();
    while(std::getline(in,word)) {
        if(word.size()!=size_t(n*(n-1)/2))throw std::runtime_error("bad graph word");
        for(int v=0;v<n;++v)nbr[v].clear();
        int k=0;for(int i=0;i<n;++i)for(int j=i+1;j<n;++j)
            if(word[k++]=='1'){nbr[i].push_back(j);nbr[j].push_back(i);}
        memo.clear();
        std::vector<int> times,freqs;
        for(int root=0;root<n;++root) {
            Value x=visit(root,Key(1)<<(8*root));times.push_back(x.time);freqs.push_back(x.frequency);
            if(x.time>worst){worst=x.time;witness(folder+"/witness_n"+std::to_string(n)+".json",word,root,worst,false);}
            if(x.frequency>worstf){worstf=x.frequency;witness(folder+"/frequency_n"+std::to_string(n)+".json",word,root,worstf,true);}
        }
        total+=memo.size();peak=std::max(peak,uint64_t(memo.size()));++graphs;
        out<<"{\"word\":\""<<word<<"\",\"times\":";array(out,times);
        out<<",\"frequencies\":";array(out,freqs);out<<",\"states\":"<<memo.size()<<"}\n";
        if(graphs%1000==0) {
            out.flush();
            if(std::filesystem::space(".").available<3ULL*1024*1024*1024)
                throw std::runtime_error("free disk below 3 GiB");
        }
    }
    double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
    std::cout<<"{\"n\":"<<n<<",\"graphs\":"<<graphs<<",\"states\":"<<total
             <<",\"peak_graph_states\":"<<peak<<",\"worst_time\":"<<worst
             <<",\"worst_frequency\":"<<worstf<<",\"seconds\":"<<seconds<<"}\n";
}

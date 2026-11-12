// Independent LFV verifier. Full uint32 counters: no small-field packing or horizon.
// A cached state stores the latest absolute first-cover time reachable from it.
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <sys/resource.h>
#include <unordered_map>
#include <vector>

struct State {
    std::array<uint32_t, 12> counts{};
    uint32_t position = 0;
    bool operator==(const State& other) const {
        return position == other.position && counts == other.counts;
    }
};
struct StateHash {
    size_t operator()(const State& state) const {
        uint64_t h = 0x84222325cbf29ce4ULL ^ state.position;
        for (auto count : state.counts) {
            h ^= count;
            h *= 0x100000001b3ULL;
            h ^= h >> 27;
        }
        return h;
    }
};
struct Answer { uint32_t time = 0, frequency = 0; };

int order;
std::array<std::vector<int>, 12> adjacent;
std::array<uint32_t, 12> counters{};
std::unordered_map<State, Answer, StateHash> cache;

Answer explore(int position, unsigned visited, uint32_t moves, uint32_t peak) {
    const State state{counters, uint32_t(position)};
    auto found = cache.find(state);
    if (found != cache.end()) return found->second;
    uint32_t smallest = UINT32_MAX;
    for (int next : adjacent[position]) smallest = std::min(smallest, counters[next]);
    Answer best{0, peak};
    for (int next : adjacent[position]) {
        if (counters[next] != smallest) continue;
        ++counters[next];
        unsigned marked = visited | (1u << next);
        if (marked == (1u << order) - 1) {
            best.time = std::max(best.time, moves + 1);
        } else {
            Answer child = explore(next, marked, moves + 1, std::max(peak, counters[next]));
            best.time = std::max(best.time, child.time);
            best.frequency = std::max(best.frequency, child.frequency);
        }
        --counters[next];
    }
    cache.emplace(state, best);
    return best;
}

int main() {
    rlimit limit{1000, 1000};
    if (setrlimit(RLIMIT_CPU, &limit)) throw std::runtime_error("CPU limit failed");
    auto started = std::chrono::steady_clock::now();
    std::ofstream output("independent_full_results.jsonl");
    for (order = 1; order <= 12; ++order) {
        std::ifstream input("independent_catalogue/n" + std::to_string(order) + ".txt");
        if (!input) throw std::runtime_error("missing input catalogue");
        int number = 0, max_time = 0, max_frequency = 0;
        uint64_t states = 0;
        std::string word;
        while (std::getline(input, word)) {
            if (word.size() != size_t(order * (order - 1) / 2))
                throw std::runtime_error("bad adjacency word");
            for (auto& list : adjacent) list.clear();
            size_t offset = 0;
            for (int u = 0; u < order; ++u) for (int v = u + 1; v < order; ++v) {
                char bit = word[offset++];
                if (bit != '0' && bit != '1') throw std::runtime_error("bad bit");
                if (bit == '1') { adjacent[u].push_back(v); adjacent[v].push_back(u); }
            }
            for (int u = 0; u < order; ++u)
                if (adjacent[u].size() > 3 || (order > 1 && adjacent[u].empty()))
                    throw std::runtime_error("bad degree");
            cache.clear();
            Answer graph;
            if (order > 1) for (int root = 0; root < order; ++root) {
                counters.fill(0);
                counters[root] = 1;
                Answer value = explore(root, 1u << root, 0, 1);
                graph.time = std::max(graph.time, value.time);
                graph.frequency = std::max(graph.frequency, value.frequency);
            }
            output << "{\"n\":" << order << ",\"word\":\"" << word
                   << "\",\"T\":" << graph.time << ",\"M\":" << graph.frequency
                   << ",\"nonterminal_states\":" << cache.size() << "}\n";
            states += cache.size();
            max_time = std::max(max_time, int(graph.time));
            max_frequency = std::max(max_frequency, int(graph.frequency));
            ++number;
            if (number % 1000 == 0) {
                output.flush();
                std::cout << "{\"checkpoint_n\":" << order << ",\"graphs\":" << number
                          << ",\"states\":" << states << "}" << std::endl;
            }
        }
        rusage usage{};
        getrusage(RUSAGE_SELF, &usage);
        double cpu = usage.ru_utime.tv_sec + usage.ru_utime.tv_usec / 1e6
                   + usage.ru_stime.tv_sec + usage.ru_stime.tv_usec / 1e6;
        double elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now()-started).count();
        std::cout << "{\"n\":" << order << ",\"classes\":" << number << ",\"T\":" << max_time
                  << ",\"M\":" << max_frequency << ",\"states\":" << states
                  << ",\"cpu_seconds\":" << cpu << ",\"elapsed_seconds\":" << elapsed << "}" << std::endl;
    }
}

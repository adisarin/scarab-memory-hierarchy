#include "three_c_classifier.h"
#include <unordered_set>
#include <list>
#include <unordered_map>

static std::unordered_set<unsigned long long> ever_seen;

// Fully-associative LRU cache with total_lines capacity
static unsigned int fa_capacity = 0;
static std::list<unsigned long long> fa_lru_list;
static std::unordered_map<unsigned long long, std::list<unsigned long long>::iterator> fa_lru_map;

extern "C" void three_c_init(unsigned int total_lines) {
    fa_capacity = total_lines;
    ever_seen.clear();
    fa_lru_list.clear();
    fa_lru_map.clear();
}

extern "C" Miss_3C_Type three_c_classify(unsigned long long line_addr) {
    // Check compulsory
    bool first_time = (ever_seen.find(line_addr) == ever_seen.end());
    ever_seen.insert(line_addr);

    if (first_time) {
        // Still insert into FA cache
        if (fa_lru_map.find(line_addr) == fa_lru_map.end()) {
            if ((unsigned int)fa_lru_list.size() >= fa_capacity) {
                unsigned long long evict = fa_lru_list.back();
                fa_lru_list.pop_back();
                fa_lru_map.erase(evict);
            }
            fa_lru_list.push_front(line_addr);
            fa_lru_map[line_addr] = fa_lru_list.begin();
        }
        return MISS_COMPULSORY;
    }

    // Check if it would hit in FA cache (capacity miss if not)
    bool fa_hit = (fa_lru_map.find(line_addr) != fa_lru_map.end());

    // Update FA cache
    if (fa_hit) {
        fa_lru_list.erase(fa_lru_map[line_addr]);
        fa_lru_list.push_front(line_addr);
        fa_lru_map[line_addr] = fa_lru_list.begin();
        // FA hit but real cache missed -> conflict
        return MISS_CONFLICT;
    } else {
        // FA miss -> capacity
        if ((unsigned int)fa_lru_list.size() >= fa_capacity) {
            unsigned long long evict = fa_lru_list.back();
            fa_lru_list.pop_back();
            fa_lru_map.erase(evict);
        }
        fa_lru_list.push_front(line_addr);
        fa_lru_map[line_addr] = fa_lru_list.begin();
        return MISS_CAPACITY;
    }
}

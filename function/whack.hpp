// WHACK 26 One Hour Hack: the whack() function. Call it, don't change it.
//   #include "whack.hpp"
//   std::vector<std::string> words = whack();
// Needs C++17 or newer.
#pragma once

#include <fstream>
#include <iterator>
#include <random>
#include <string>
#include <vector>

// Writes 1-100 random words to a file called "whack" (one per line) and returns them.
inline std::vector<std::string> whack() {
    static const char* const words[] = {
        "whack", "hack", "duck", "quack", "goose", "honk", "bug", "feature", "warwick", "oculus",
        "compsoc", "marshall", "wace", "brevan", "howard", "capital", "one", "bloomberg",
        "netcraft", "incident", "io", "pizza", "coffee", "sleep", "deploy", "merge", "conflict",
        "commit", "push", "prod", "segfault", "null", "pointer", "stack", "overflow", "semicolon",
        "rubber", "demo", "pitch", "prize", "midnight", "wifi",
    };
    static std::mt19937 rng{std::random_device{}()};
    std::uniform_int_distribution<int> lines(1, 100);
    std::uniform_int_distribution<std::size_t> pick(0, std::size(words) - 1);

    const int count = lines(rng);
    std::vector<std::string> result;
    std::ofstream file("whack");
    for (int i = 0; i < count; ++i) {
        result.emplace_back(words[pick(rng)]);
        file << result.back() << '\n';
    }
    return result;
}

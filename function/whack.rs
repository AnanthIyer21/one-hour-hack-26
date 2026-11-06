// WHACK 26 One Hour Hack: the whack() function. Call it, don't change it.
// Put this file next to your main.rs, then:
//   mod whack;
//   let words = whack::whack();
// No crates needed. Rust's standard library has no random numbers, so this borrows HashMap's random keys.

use std::collections::hash_map::RandomState;
use std::fs;
use std::hash::BuildHasher;

const WORDS: [&str; 42] = [
    "whack", "hack", "duck", "quack", "goose", "honk", "bug", "feature", "warwick", "oculus",
    "compsoc", "marshall", "wace", "brevan", "howard", "capital", "one", "bloomberg", "netcraft",
    "incident", "io", "pizza", "coffee", "sleep", "deploy", "merge", "conflict", "commit", "push",
    "prod", "segfault", "null", "pointer", "stack", "overflow", "semicolon", "rubber", "demo",
    "pitch", "prize", "midnight", "wifi",
];

/// Writes 1-100 random words to a file called "whack" (one per line) and returns them.
pub fn whack() -> Vec<String> {
    let random = RandomState::new();
    let count = 1 + random.hash_one(0_u64) % 100;
    let words: Vec<String> = (1..=count)
        .map(|i| WORDS[(random.hash_one(i) % WORDS.len() as u64) as usize].to_string())
        .collect();
    fs::write("whack", words.join("\n") + "\n").expect("couldn't write the whack file");
    words
}

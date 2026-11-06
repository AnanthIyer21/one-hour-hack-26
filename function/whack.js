// WHACK 26 One Hour Hack: the whack() function. Call it, don't change it.
//   const { whack } = require("./whack.js");   // keep the .js: plain "./whack" can pick up the whack file instead
//   const words = whack();
const fs = require("node:fs");

const WORDS = [
  "whack", "hack", "duck", "quack", "goose", "honk", "bug", "feature", "warwick", "oculus",
  "compsoc", "marshall", "wace", "brevan", "howard", "capital", "one", "bloomberg", "netcraft",
  "incident", "io", "pizza", "coffee", "sleep", "deploy", "merge", "conflict", "commit", "push",
  "prod", "segfault", "null", "pointer", "stack", "overflow", "semicolon", "rubber", "demo",
  "pitch", "prize", "midnight", "wifi",
];

/** Writes 1-100 random words to a file called "whack" (one per line) and returns them. */
function whack() {
  const count = 1 + Math.floor(Math.random() * 100);
  const words = Array.from({ length: count }, () => WORDS[Math.floor(Math.random() * WORDS.length)]);
  fs.writeFileSync("whack", words.join("\n") + "\n");
  return words;
}

module.exports = { whack };

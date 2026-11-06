// WHACK 26 One Hour Hack: the whack() function. Call it, don't change it.
//   import { whack } from "./whack.ts";
//   const words = whack();
import { writeFileSync } from "node:fs";

const WORDS: readonly string[] = [
  "whack", "hack", "duck", "quack", "goose", "honk", "bug", "feature", "warwick", "oculus",
  "compsoc", "marshall", "wace", "brevan", "howard", "capital", "one", "bloomberg", "netcraft",
  "incident", "io", "pizza", "coffee", "sleep", "deploy", "merge", "conflict", "commit", "push",
  "prod", "segfault", "null", "pointer", "stack", "overflow", "semicolon", "rubber", "demo",
  "pitch", "prize", "midnight", "wifi",
];

/** Writes 1-100 random words to a file called "whack" (one per line) and returns them. */
export function whack(): string[] {
  const count = 1 + Math.floor(Math.random() * 100);
  const words = Array.from({ length: count }, () => WORDS[Math.floor(Math.random() * WORDS.length)]!);
  writeFileSync("whack", words.join("\n") + "\n");
  return words;
}

// WHACK 26 One Hour Hack: the whack() function. Call it, don't change it.
// Put this file next to your main.go (same package), then:
//
//	words := whack()
package main

import (
	"math/rand"
	"os"
	"strings"
)

var whackWords = []string{
	"whack", "hack", "duck", "quack", "goose", "honk", "bug", "feature", "warwick", "oculus",
	"compsoc", "marshall", "wace", "brevan", "howard", "capital", "one", "bloomberg", "netcraft",
	"incident", "io", "pizza", "coffee", "sleep", "deploy", "merge", "conflict", "commit", "push",
	"prod", "segfault", "null", "pointer", "stack", "overflow", "semicolon", "rubber", "demo", "pitch",
	"prize", "midnight", "wifi",
}

// whack writes 1-100 random words to a file called "whack" (one per line) and returns them.
func whack() []string {
	words := make([]string, 1+rand.Intn(100))
	for i := range words {
		words[i] = whackWords[rand.Intn(len(whackWords))]
	}
	if err := os.WriteFile("whack", []byte(strings.Join(words, "\n")+"\n"), 0o644); err != nil {
		panic(err)
	}
	return words
}

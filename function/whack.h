/* WHACK 26 One Hour Hack: the whack() function. Call it, don't change it.
 *
 *   #include "whack.h"
 *
 *   size_t count;
 *   const char **words = whack(&count);   // words[0] to words[count - 1], then NULL
 *   ...
 *   free(words);                          // free the array when you're done, not the words
 */
#ifndef WHACK_H
#define WHACK_H

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

static const char *const WHACK_WORDS[] = {
    "whack", "hack", "duck", "quack", "goose", "honk", "bug", "feature", "warwick", "oculus",
    "compsoc", "marshall", "wace", "brevan", "howard", "capital", "one", "bloomberg", "netcraft",
    "incident", "io", "pizza", "coffee", "sleep", "deploy", "merge", "conflict", "commit", "push",
    "prod", "segfault", "null", "pointer", "stack", "overflow", "semicolon", "rubber", "demo",
    "pitch", "prize", "midnight", "wifi",
};

/* SplitMix64, seeded from the clock the first time it's used (C has no decent built-in random). */
static inline uint64_t whack_random(void) {
    static uint64_t state = 0;
    if (state == 0) {
        int here;
        state = (uint64_t) time(NULL) ^ ((uint64_t) clock() << 32) ^ (uint64_t) (uintptr_t) &here;
    }
    uint64_t z = (state += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

/* Writes 1-100 random words to a file called "whack" (one per line) and returns them.
 * Returns them as a NULL-terminated array and sets *count to how many there are (pass NULL if you
 * don't need it). Returns NULL if the file can't be written. */
static inline const char **whack(size_t *count) {
    size_t n = 1 + (size_t) (whack_random() % 100);
    const char **words = (const char **) malloc((n + 1) * sizeof *words);
    FILE *file = fopen("whack", "w");
    if (words == NULL || file == NULL) {
        free(words);
        if (file != NULL) fclose(file);
        return NULL;
    }
    for (size_t i = 0; i < n; i++) {
        words[i] = WHACK_WORDS[whack_random() % (sizeof WHACK_WORDS / sizeof WHACK_WORDS[0])];
        fprintf(file, "%s\n", words[i]);
    }
    words[n] = NULL;
    fclose(file);
    if (count != NULL) *count = n;
    return words;
}

#endif

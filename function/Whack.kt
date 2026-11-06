// WHACK 26 One Hour Hack: the whack() function. Call it, don't change it.
//   val words = whack()

import java.io.File
import kotlin.random.Random

private val WORDS = listOf(
    "whack", "hack", "duck", "quack", "goose", "honk", "bug", "feature", "warwick", "oculus",
    "compsoc", "marshall", "wace", "brevan", "howard", "capital", "one", "bloomberg", "netcraft",
    "incident", "io", "pizza", "coffee", "sleep", "deploy", "merge", "conflict", "commit", "push",
    "prod", "segfault", "null", "pointer", "stack", "overflow", "semicolon", "rubber", "demo",
    "pitch", "prize", "midnight", "wifi",
)

/** Writes 1-100 random words to a file called "whack" (one per line) and returns them. */
fun whack(): List<String> {
    val words = List(Random.nextInt(1, 101)) { WORDS.random() }
    File("whack").writeText(words.joinToString("\n", postfix = "\n"))
    return words
}

// WHACK 26 One Hour Hack: the whack() function. Call it, don't change it.
//   List<String> words = Whack.whack();

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;

public final class Whack {
    private static final String[] WORDS = {
        "whack", "hack", "duck", "quack", "goose", "honk", "bug", "feature", "warwick", "oculus",
        "compsoc", "marshall", "wace", "brevan", "howard", "capital", "one", "bloomberg",
        "netcraft", "incident", "io", "pizza", "coffee", "sleep", "deploy", "merge", "conflict",
        "commit", "push", "prod", "segfault", "null", "pointer", "stack", "overflow", "semicolon",
        "rubber", "demo", "pitch", "prize", "midnight", "wifi",
    };

    private Whack() {}

    /** Writes 1-100 random words to a file called "whack" (one per line) and returns them. */
    public static List<String> whack() {
        ThreadLocalRandom random = ThreadLocalRandom.current();
        int count = random.nextInt(1, 101);
        List<String> words = new ArrayList<>(count);
        for (int i = 0; i < count; i++) {
            words.add(WORDS[random.nextInt(WORDS.length)]);
        }
        try {
            Files.writeString(Path.of("whack"), String.join("\n", words) + "\n");
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
        return words;
    }
}

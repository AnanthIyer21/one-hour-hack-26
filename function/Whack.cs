// WHACK 26 One Hour Hack: the whack() function. Call it, don't change it.
//   List<string> words = Whacker.Whack();

using System;
using System.Collections.Generic;
using System.IO;

public static class Whacker
{
    private static readonly string[] Words =
    {
        "whack", "hack", "duck", "quack", "goose", "honk", "bug", "feature", "warwick", "oculus",
        "compsoc", "marshall", "wace", "brevan", "howard", "capital", "one", "bloomberg",
        "netcraft", "incident", "io", "pizza", "coffee", "sleep", "deploy", "merge", "conflict",
        "commit", "push", "prod", "segfault", "null", "pointer", "stack", "overflow", "semicolon",
        "rubber", "demo", "pitch", "prize", "midnight", "wifi",
    };

    private static readonly Random Rng = new Random();

    /// <summary>Writes 1-100 random words to a file called "whack" (one per line) and returns them.</summary>
    public static List<string> Whack()
    {
        int count = Rng.Next(1, 101);
        var words = new List<string>(count);
        for (int i = 0; i < count; i++)
        {
            words.Add(Words[Rng.Next(Words.Length)]);
        }
        File.WriteAllText("whack", string.Join("\n", words) + "\n");
        return words;
    }
}

# WHACK 26 · One Hour Hack 🦆

**Saturday 7 November, 22:30–00:00.** Solo only. Pull requests close at **00:00 sharp**.

The winner takes home a **mini projector**

## The prompt

### **Most creative use of the `whack()` function.**

Everyone gets the same function. What you build around it is up to you.

## The function

`whack()` does the same thing in every language:

1. Picks a random number from 1 to 100.
2. Writes that many lines to a file called `whack` in the current folder, each one a random word from the same list of 42 (WHACK, our sponsors, ducks, geese and some classic hackathon suffering).
3. Returns the words it wrote, in order.

Each call replaces the previous `whack` file.

| Language | File | How to call it |
|---|---|---|
| Python | [`function/whack.py`](function/whack.py) | `from whack import whack` then `words = whack()` |
| JavaScript (Node) | [`function/whack.js`](function/whack.js) | `const { whack } = require("./whack.js")` then `whack()` |
| TypeScript (Node, Deno, Bun) | [`function/whack.ts`](function/whack.ts) | `import { whack } from "./whack.ts"` then `whack()` |
| Java | [`function/Whack.java`](function/Whack.java) | `List<String> words = Whack.whack();` |
| Kotlin | [`function/Whack.kt`](function/Whack.kt) | `val words = whack()` |
| C | [`function/whack.h`](function/whack.h) | `const char **words = whack(&count);` then `free(words)` when you're done |
| C++ (17 or newer) | [`function/whack.hpp`](function/whack.hpp) | `std::vector<std::string> words = whack();` |
| C# | [`function/Whack.cs`](function/Whack.cs) | `List<string> words = Whacker.Whack();` |
| Go | [`function/whack.go`](function/whack.go) | `words := whack()` (put the file next to your `main.go`) |
| Rust | [`function/whack.rs`](function/whack.rs) | `mod whack;` then `let words = whack::whack();` |
| Haskell | [`function/Whack.hs`](function/Whack.hs) | `import Whack (whack)` then `ws <- whack` |
| Ruby | [`function/whack.rb`](function/whack.rb) | `require_relative "whack"` then `words = whack` |
| Bash | [`function/whack.sh`](function/whack.sh) | `source whack.sh` then `whack` (prints the words) |

Want to see it first? From the `function` folder:

```sh
python3 -c "from whack import whack; print(whack())"
cat whack
```

Using a language that isn't listed? Call one of these from it. Running `whack.py` as a subprocess counts.

Don't name your own program or folder `whack`, since the function writes a file with that name wherever it runs.

## Rules

- **Call `whack()`, don't change it.** Copy the file for your language into your project as it is. Adding a package line or renaming the file to fit your setup is fine. Editing the function or its word list isn't.
- **Make it the star.** Build your hack around what `whack()` gives you. Call it as often as you like and do anything you want with the words or the file.
- **Solo only.** Beyond that, use any language, library, framework or API you like.
- **Keep it harmless.** Nothing that deletes files, fills up disks, floods networks or touches anyone else's machine.
- **00:00 is the deadline.** Pull requests opened after 00:00 aren't judged. GitHub's timestamp is the clock.

## How to submit

1. [**Fork this repo.**](https://github.com/WarwickHack/one-hour-hack-26/fork)
2. Put everything in a new folder named after your GitHub username, `submissions/your-username/`. Don't change anything outside it.
3. Copy [`submissions/_template/README.md`](submissions/_template/README.md) into your folder and fill it in: who you are, a one-line pitch, how to run it, and a screenshot or GIF.
4. Open a pull request to this repo called `Submission: your name` before 00:00.

**Never made a pull request?** You can do it all on github.com. Fork the repo, go into the `submissions` folder of your fork and click **Add file → Upload files**. Drag in your folder and commit. Then go back to the front page of your fork and click **Contribute → Open pull request**.

**GitHub not playing along?** Post a link to your code (a repo, gist or zip) and a screenshot in **#one-hour-hack** on the WHACK Discord before 00:00 and we'll count it.

## Judging

We'll judge from the README, screenshot and code in your folder. We're looking for:

- **Creativity:** did you do something with a pile of random words that nobody else thought of?
- **Use of `whack()`:** is it at the heart of your hack, or bolted on at the end?
- **Fun:** did it make us laugh, gasp or ask "wait, how?"

We might run your code as well, in a sandbox.

The winner is announced at the closing ceremony on Sunday. Good luck!

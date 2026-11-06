# WHACK 26 One Hour Hack: the whack() function. Call it, don't change it.
#   require_relative "whack"
#   words = whack

WHACK_WORDS = %w[
  whack hack duck quack goose honk bug feature warwick oculus compsoc marshall wace brevan howard
  capital one bloomberg netcraft incident io pizza coffee sleep deploy merge conflict commit push
  prod segfault null pointer stack overflow semicolon rubber demo pitch prize midnight wifi
].freeze

# Writes 1-100 random words to a file called "whack" (one per line) and returns them.
def whack
  words = Array.new(rand(1..100)) { WHACK_WORDS.sample }
  File.write("whack", words.join("\n") + "\n")
  words
end

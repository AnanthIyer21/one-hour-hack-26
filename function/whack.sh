# WHACK 26 One Hour Hack: the whack() function. Call it, don't change it.
#   source whack.sh
#   whack               # prints the words, one per line
#   words=($(whack))    # or keep them in an array
# Needs bash (not sh or zsh). On a Mac, run your script with bash.

# Writes 1-100 random words to a file called "whack" (one per line) and prints them.
whack() {
  local words=(
    whack hack duck quack goose honk bug feature warwick oculus compsoc marshall wace brevan howard
    capital one bloomberg netcraft incident io pizza coffee sleep deploy merge conflict commit push
    prod segfault null pointer stack overflow semicolon rubber demo pitch prize midnight wifi
  )
  local count=$((RANDOM % 100 + 1)) i
  local -a picked=()
  for ((i = 0; i < count; i++)); do
    picked+=("${words[RANDOM % ${#words[@]}]}")
  done
  printf '%s\n' "${picked[@]}" > whack
  printf '%s\n' "${picked[@]}"
}

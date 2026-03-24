"""
Filter ENABLE word list and generate valid puzzle letter sets.
Output: words.js containing the filtered word list and valid 7-letter sets.
"""
import json
from collections import defaultdict

# Read and filter words: 4-7 letters, only a-z, max 7 distinct letters
with open("enable1.txt") as f:
    all_words = [w.strip().lower() for w in f if w.strip()]

filtered = []
for w in all_words:
    if 4 <= len(w) <= 7 and w.isalpha():
        unique = set(w)
        if len(unique) <= 7:
            filtered.append(w)

print(f"Filtered words: {len(filtered)}")

# Group words by their unique letter set (as frozenset)
by_letterset = defaultdict(list)
for w in filtered:
    by_letterset[frozenset(w)].append(w)

# Find all 7-letter sets where each letter has at least one word starting with it
valid_sets = []
for letters, words in by_letterset.items():
    if len(letters) != 7:
        continue
    sorted_letters = sorted(letters)
    # Check: for each letter, is there at least one word starting with it?
    all_covered = True
    for letter in sorted_letters:
        has_word = any(w[0] == letter for w in words)
        if not has_word:
            # Also check subsets — words using fewer than 7 unique letters
            # whose letters are all within this set
            all_covered = False
            break
    if all_covered:
        valid_sets.append(sorted_letters)

print(f"Valid 7-letter sets (strict): {len(valid_sets)}")

# Now expand: for each valid 7-letter set, find ALL words from the full filtered
# list whose letters are a subset of the 7 letters
# Also re-check coverage including subset words
final_sets = []
for letters in valid_sets:
    letter_set = set(letters)
    matching_words = [w for w in filtered if set(w).issubset(letter_set)]
    # Verify each letter has at least one starting word
    covered = all(
        any(w[0] == l for w in matching_words)
        for l in letters
    )
    if covered:
        final_sets.append(letters)

print(f"Valid 7-letter sets (with subset words): {len(final_sets)}")

# Also find sets where we missed them because the 7-letter frozenset didn't have
# words for every starting letter, but subset words fill the gaps
# Let's do a broader search: for every combination of 7 letters that appears
# as the unique letters of ANY word, collect all matching words and check coverage
all_letter_sets_7 = set()
for w in filtered:
    u = frozenset(w)
    if len(u) == 7:
        all_letter_sets_7.add(u)

print(f"Total 7-distinct-letter sets from words: {len(all_letter_sets_7)}")

better_sets = []
for ls in all_letter_sets_7:
    letters = sorted(ls)
    matching = [w for w in filtered if set(w).issubset(ls)]
    covered = all(
        any(w[0] == l for w in matching)
        for l in letters
    )
    if covered:
        better_sets.append(letters)

print(f"Valid sets (full check): {len(better_sets)}")

# Build the word set for JS (only words whose letters fit in <=7 unique chars)
# We'll send all filtered words and let JS do the subset check per puzzle
# But to keep file size down, let's just send the filtered list

# Write output
output = {
    "words": sorted(filtered),
    "puzzleSets": sorted(better_sets)
}

with open("words.js", "w") as f:
    f.write("// Auto-generated word game data\n")
    f.write(f"const WORD_LIST = new Set({json.dumps(output['words'])});\n\n")
    f.write(f"const PUZZLE_SETS = {json.dumps(output['puzzleSets'])};\n")

print(f"Wrote words.js with {len(filtered)} words and {len(better_sets)} puzzle sets")

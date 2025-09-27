# CompPhysUVA_PseudoRandom_taylorjcolaizzi
Vibe coding exercises due Monday September 29th in Dr. Hirsoky's computational physics class.

Example 1
Copilot calculated the entropy of the data file (rnd.dat) as 7.790677 bits/byte.
It said the size of the large text file (large.txt) was 256,004 bytes. Its entropy was 4.130562 bits/byte; when normalized, that was 51.63% of the 8 bits/byte maximum.
The compressed file (large.txt.gz) was 1,463 bytes and its entropy was 4.838450 bits/byte. Normalized, this was 60.48% of the 8 bits/byte maximum.
"To produce locally," quote,
"# 1) Use a large text file you have (e.g., logs, an eBook, or a source tree):
python entropy.py large.txt

# 2) Compress it (keep original):
gzip -k large.txt    # produces large.txt.gz

# 3) Entropy on the compressed file:
python entropy.py large.txt.gz
" end quote.
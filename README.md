# CompPhysUVA_PseudoRandom_taylorjcolaizzi
Vibe coding exercises due Monday September 29th in Dr. Hirsoky's computational physics class.

Example 1
Copilot calculated the entropy of the data file (rnd.dat) as 7.790677 bits/byte.
It said the size of the large text file (large.txt) was 256,004 bytes. Its entropy was 4.130562 bits/byte; when normalized, that was 51.63% of the 8 bits/byte maximum.
The compressed file (large.txt.gz) was 1,463 bytes and its entropy was 4.838450 bits/byte. Normalized, this was 60.48% of the 8 bits/byte maximum.
"To produce locally," quote, "
'# 1) Use a large text file you have (e.g., logs, an eBook, or a source tree):
python entropy.py large.txt
'# 2) Compress it (keep original):
gzip -k large.txt    # produces large.txt.gz
'# 3) Entropy on the compressed file:
python entropy.py large.txt.gz
" end quote.

Example 2
Copilot calculated the output. Count was 1000000, mean was 0.500064557021, and std_dev (sample) was 0.288563026623. This is close to the theoretical mean and population standard deviation.
After modifying for the moments: expected values were 1/2, 1/3, 1/4, and 1/5. Computed values were 0.500064557021, 0.333333098254, 0.249939919680, and 0.199893774021.

Example 3
So, Copilot accidentally gave me two scripts for this. I called the first one scatter.py and the second one scatter2.py.
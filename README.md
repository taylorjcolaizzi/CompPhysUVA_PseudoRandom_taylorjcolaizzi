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
"How to run.
1.  Put lpr.py and lcg_stats.py in the same directory.
2.  Run with defaults (1,000,000 normalized [0,1) values):
python lcg_stats.py
"

Example 3
So, Copilot accidentally gave me two scripts for this. I called the first one scatter.py and the second one scatter2.py.
How to run: just do
python scatter.py
python scatter2.py

Example 4
It made the program.
How to run:
python exp.py

Example 5
Prompting this: "Modify the script so that the first number has a mean of 0 and standard deviation of 1, and the second has a mean of 0 and standard deviation of 2." had no effect.
It was hard to read the final plot with everything at the same colormap. So, I had it increae the visual contrast.
How to run:
To create a pair of random numbers, one with mean 0 std_dev 1 and another with mean 0 and std_dev 2, do
python norm2.py
To input a seed (42), do
python norm2.py --seed 42
To plot 10,000 points, do
python norm2.py --plot
To also show it, do
python norm2.py --plot --show
To have 4 plots on a single canvas, do
python norm2.py --plot --grid --rho 0 0.5 1 -1 --show
import numpy as np

# Generate a pair of normally distributed random numbers
mean = 0       # Mean of the distribution
std_dev = 1    # Standard deviation of the distribution

# Generate two random numbers from a normal distribution
random_numbers = np.random.normal(mean, std_dev, 2)

# Print the generated numbers
print("Generated normally distributed random numbers:", random_numbers)

import numpy as np

lambda_param = 10
random_numbers = np.random.exponential(scale=1/lambda_param, size=1000)
print(random_numbers)

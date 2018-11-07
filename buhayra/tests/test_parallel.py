
from math import sqrt
from joblib import Parallel, delayed
Parallel(n_jobs=8, prefer="threads")(delayed(sqrt)(i ** 2) for i in range(100))

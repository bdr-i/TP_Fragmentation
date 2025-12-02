import re
import numpy as np

def build_usage_matrix(workload, attributes):
    matrix = []
    # Construire la matrice d'usage
    for query in workload:
        row = [1 if attr in query else 0 for attr in attributes]
        matrix.append(row)

    return np.array(matrix)

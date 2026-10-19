import numpy as np
from PIL import Image

def get_averaging_kernel(size=3):
    kernel = np.ones((size, size)) / (size * size)

    return kernel

def get_sharpening_kernel(strength=1.0):
    return np.array([
        [0, -strength, 0],
        [-strength, 1 + 4 * strength, -strength],
        [0, -strength, 0]
    ])

def get_gaussian_kernel(sigma=1.0, size=3):
    kernel = np.zeros((size, size))
    
    for x in range(size):
        for y in range(size):
            x_dist = x - size // 2
            y_dist = y - size // 2
            # GenAI: Gemini used to help with using correct Gaussian kernel formula
            kernel[x, y] = np.exp(-(x_dist**2 + y_dist**2) / (2 * (sigma**2)))
            
    kernel /= np.sum(kernel)

    return kernel

def get_laplacian_kernel():
    return np.array([
        [0, 1, 0],
        [1, -4, 1],
        [0, 1, 0]
    ])

FILTER_CONFIG = {
    "Averaging": get_averaging_kernel,
    "Sharpening": get_sharpening_kernel,
    "Gaussian": get_gaussian_kernel,
    "Laplacian": get_laplacian_kernel
}
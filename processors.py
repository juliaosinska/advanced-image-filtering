import numpy as np
from PIL import Image

from convolution import optimized_convolution, basic_convolution

PROCESSOR_REGISTRY = {
    "run_averaging": run_averaging,
    "run_gaussian_separable": run_gaussian_separable,
    "run_sharpening": run_sharpening,
    "run_laplacian": run_laplacian,
    "run_unsharp_mask": run_unsharp_mask,
    "run_high_boost": run_high_boost,
    "run_dog": run_dog,
    "run_log": run_log,
}

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

def get_laplacian_kernel(size=3):
    if size == 3:
        # leaving this as its the most popular literature kernel for Laplacian
        return np.array([
            [0, 1, 0],
            [1, -4, 1],
            [0, 1, 0]
        ])
    else:
        # using diagonal-inclusive Laplacian kernel for larger sizes
        kernel = np.ones((size, size))
        center = size // 2
        kernel[center, center] = 1 - (size * size)

        return kernel
    
def run_averaging(image: Image.Image, kernel_size: int = 3, optimized: bool = True) -> Image.Image:
    kernel = get_averaging_kernel(size=kernel_size)
    if optimized:
        return optimized_convolution(image, kernel)
    else:
        return basic_convolution(image, kernel)

def run_sharpening(image: Image.Image, strength: float = 1.0, optimized: bool = True) -> Image.Image:
    kernel = get_sharpening_kernel(strength=strength)
    if optimized:
        return optimized_convolution(image, kernel)
    else:
        return basic_convolution(image, kernel)

def run_laplacian(image: Image.Image, laplacian_size: int = 3, optimized: bool = True) -> Image.Image:
    kernel = get_laplacian_kernel(size=laplacian_size)
    if optimized:
        return optimized_convolution(image, kernel)
    else:
        return basic_convolution(image, kernel)
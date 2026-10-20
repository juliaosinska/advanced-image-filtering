import numpy as np
from PIL import Image

from convolution import optimized_convolution, basic_convolution

# ==========================================
#  LEAVING KERNEL GENERATION AS PREVIOUSLY IMPLEMENTED (ONLY MODIFIED TO USE SEPARABLE GAUSSIAN)
# ==========================================

def get_averaging_kernel(size=3):
    kernel = np.ones((size, size)) / (size * size)

    return kernel

def get_sharpening_kernel(strength=1.0):
    return np.array([
        [0, -strength, 0],
        [-strength, 1 + 4 * strength, -strength],
        [0, -strength, 0]
    ])

def get_separable_gaussian_kernel(sigma=1.0):
    radius = int(np.ceil(3 * sigma))
    size = 2 * radius + 1

    x = np.arange(-radius, radius + 1)
    # GenAI: Gemini used to help with using correct Gaussian kernel formula
    kernel = np.exp(-(x**2) / (2 * (sigma**2)))
             
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

# ==========================================
# BASIC FILTERS PROCESSORS
# ==========================================   

def run_averaging(image: Image.Image, kernel_size: int = 3, optimized: bool = True) -> Image.Image:
    kernel = get_averaging_kernel(size=kernel_size)
    if optimized: 
        final_image = optimized_convolution(image, kernel)
    else:
        final_image = basic_convolution(image, kernel)

    return final_image

def run_gaussian_separable(image: Image.Image, sigma: float = 1.0, optimized: bool = True) -> Image.Image:
    kernel = get_separable_gaussian_kernel(sigma=sigma)
    size = len(kernel)

    kernel_h = kernel.reshape((1, size))
    kernel_v = kernel.reshape((size, 1))

    convolution_version = optimized_convolution if optimized else basic_convolution

    h_convolved_image = convolution_version(image, kernel_h)
    final_image = convolution_version(h_convolved_image, kernel_v)

    return final_image

def run_sharpening(image: Image.Image, strength: float = 1.0, optimized: bool = True) -> Image.Image:
    kernel = get_sharpening_kernel(strength=strength)
    if optimized:
        final_image = optimized_convolution(image, kernel)
    else:
        final_image = basic_convolution(image, kernel)

    return final_image

def run_laplacian(image: Image.Image, laplacian_size: int = 3, optimized: bool = True) -> Image.Image:
    kernel = get_laplacian_kernel(size=laplacian_size)
    if optimized:
        final_image = optimized_convolution(image, kernel)
    else:
        final_image = basic_convolution(image, kernel)
    
    return final_image

# ==========================================
# ADVANCED FILTERS PROCESSORS
# ==========================================   

def run_unsharp_mask(image: Image.Image, sigma: float = 1.0, alpha: float = 1.0, optimized: bool = True) -> Image.Image:
    Gaussian_blurred = run_gaussian_separable(image, sigma=sigma, optimized=optimized)
    mask = np.array(image) - np.array(Gaussian_blurred)
    unsharp_image = np.array(image) + alpha * mask
    unsharp_image = np.clip(unsharp_image, 0, 255).astype(np.uint8)
    return Image.fromarray(unsharp_image)

def run_high_boost(image: Image.Image, sigma: float = 1.0, a_param: float = 1.2, optimized: bool = True) -> Image.Image:
    Gaussian_blurred = run_gaussian_separable(image, sigma=sigma, optimized=optimized)
    high_boost_image = np.array(image) * a_param - np.array(Gaussian_blurred)
    high_boost_image = np.clip(high_boost_image, 0, 255).astype(np.uint8)
    return Image.fromarray(high_boost_image)

def run_dog(image: Image.Image, sigma1: float = 1.0, sigma2: float = 2.0, optimized: bool = True) -> Image.Image:
    Gaussian_blurred1 = run_gaussian_separable(image, sigma=sigma1, optimized=optimized)
    Gaussian_blurred2 = run_gaussian_separable(image, sigma=sigma2, optimized=optimized)
    dog_image = np.array(Gaussian_blurred1) - np.array(Gaussian_blurred2)
    dog_image = np.clip(dog_image, 0, 255).astype(np.uint8)
    return Image.fromarray(dog_image)

def run_log(image: Image.Image, sigma: float = 1.0, laplacian_size: int = 3, optimized: bool = True) -> Image.Image:
    Gaussian_blurred = run_gaussian_separable(image, sigma=sigma, optimized=optimized)
    laplacian_image = run_laplacian(Gaussian_blurred, laplacian_size=laplacian_size, optimized=optimized)
    log_image = np.array(laplacian_image)
    log_image = np.clip(log_image, 0, 255).astype(np.uint8)
    return Image.fromarray(log_image)

# ==========================================
# REGISTRY OF PROCESSORS
# ==========================================

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
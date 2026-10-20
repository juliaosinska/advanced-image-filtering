import numpy as np
from PIL import Image

from convolution import optimized_convolution, basic_convolution
from filters_config import FILTER_CONFIG

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
    image_array = np.array(image)

    gaussian_blurred = run_gaussian_separable(image, sigma=sigma, optimized=optimized)
    gaussian_blurred_array = np.array(gaussian_blurred)

    mask_array = image_array - gaussian_blurred_array

    unsharp_array = image_array + alpha * mask_array
    unsharp_array = np.clip(unsharp_array, 0, 255).astype(np.uint8)
    
    return {
        "Original (I)": image,
        "Gaussian (Gσ)": gaussian_blurred,
        "Mask (I − Gσ)": Image.fromarray(mask_array),
        "Unsharp (U)": Image.fromarray(unsharp_array)
    }

def run_high_boost(image: Image.Image, sigma: float = 1.0, a_param: float = 1.2, optimized: bool = True) -> Image.Image:
    image_array = np.array(image)

    gaussian_blurred = run_gaussian_separable(image, sigma=sigma, optimized=optimized)
    gaussian_blurred_array = np.array(gaussian_blurred)

    mask_array = image_array - gaussian_blurred_array

    # GenAI: Gemini helped with adjusting the high-boost formula to ensure avoiding dark images
    # A * I - Gσ = I + (A - 1) * I - Gσ = I + (A - 1) * (I - Gσ)
    high_boost_array = image_array + (a_param - 1.0) * mask_array
    high_boost_array = np.clip(high_boost_array, 0, 255).astype(np.uint8)
    
    return {
        "Original (I)": image,
        "Gaussian (Gσ)": gaussian_blurred,
        "High-Boost (H)": Image.fromarray(high_boost_array)
    }

def run_dog(image: Image.Image, sigma1: float = 1.0, sigma2: float = 2.0, optimized: bool = True) -> Image.Image:
    gaussian_blurred1 = run_gaussian_separable(image, sigma=sigma1, optimized=optimized)
    gaussian_blurred2 = run_gaussian_separable(image, sigma=sigma2, optimized=optimized)

    gaussian_blurred1_array = np.array(gaussian_blurred1)
    gaussian_blurred2_array = np.array(gaussian_blurred2)
    
    dog_array = gaussian_blurred1_array - gaussian_blurred2_array
    dog_array = np.clip(dog_array, 0, 255).astype(np.uint8)

    return {
        "Original (I)": image,
        "Gaussian 1 (σ₁)": gaussian_blurred1,
        "Gaussian 2 (σ₂)": gaussian_blurred2,
        "DoG (D)": Image.fromarray(dog_array)
    }

def run_log(image: Image.Image, sigma: float = 1.0, laplacian_size: int = 3, optimized: bool = True) -> Image.Image:
    gaussian_blurred = run_gaussian_separable(image, sigma=sigma, optimized=optimized)

    laplacian_image = run_laplacian(gaussian_blurred, laplacian_size=laplacian_size, optimized=optimized)
    
    log_array = np.array(laplacian_image)
    log_array = np.clip(log_array + 128, 0, 255).astype(np.uint8)
    
    return {
        "Original (I)": image,
        "Gaussian (Gσ)": gaussian_blurred,
        "LoG Result": Image.fromarray(log_array)
    }

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

# ==========================================
# HELPER FUNCTION TO APPLY FILTERS BASED ON CONFIGURATION
# ==========================================

def apply_filter(image: Image.Image, filter_name: str, params: dict, optimized: bool = True) -> Image.Image:
    if filter_name not in FILTER_CONFIG:
        raise ValueError(f"Filter '{filter_name}' is not defined in FILTER_CONFIG.")

    filter_config = FILTER_CONFIG[filter_name]
    filter_type = filter_config["type"]
    filter_processor_key = filter_config["processor"]

    if filter_processor_key not in PROCESSOR_REGISTRY:
        raise ValueError(f"Processor '{filter_processor_key}' for filter '{filter_name}' is not registered.")

    processor_function = PROCESSOR_REGISTRY[filter_processor_key]


    if filter_type == "basic":
        result_image = processor_function(image, **params, optimized=optimized)
        return {
            filter_config["previews"][0]: image,
            filter_config["previews"][1]: result_image
        }
    elif filter_type == "combination":
        return processor_function(image, **params, optimized=optimized)
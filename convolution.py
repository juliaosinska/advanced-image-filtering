from PIL import Image, ImageOps
import numpy as np

from filters_config import FILTER_CONFIG

def optimized_convolution(image: Image.Image, kernel: np.ndarray) -> Image.Image:
    img_array = np.array(image, dtype=np.float32)
    image_height, image_width, image_channels = img_array.shape

    kernel_height, kernel_width = kernel.shape
    pad_height = kernel_height // 2
    pad_width = kernel_width // 2

    padded_img_array = np.pad(img_array, ((pad_height, pad_height), (pad_width, pad_width), (0, 0)), mode='edge')

    output_img_array = np.zeros_like(img_array)

    # GenAI: Gemini used to help with optimizing the convolution operation by iterating over the kernel and applying it to the entire image at once
    for n in range(kernel_height):
        for m in range(kernel_width):
            weight = kernel[n,m]

            if weight == 0:
                continue
            
            piece_of_image = padded_img_array[n:n + image_height, m:m + image_width, :]
            output_img_array += piece_of_image * weight

    output_img_array = np.clip(output_img_array, 0, 255).astype(np.uint8)
    return Image.fromarray(output_img_array)

def basic_convolution(image: Image.Image, kernel: np.ndarray) -> Image.Image:
    img_array = np.array(image, dtype=np.float32)
    image_height, image_width, image_channels = img_array.shape

    kernel_height, kernel_width = kernel.shape
    pad_height = kernel_height // 2
    pad_width = kernel_width // 2

    # GenAI: Gemini used to help with edge handling by padding the image with edge values
    padded_img_array = np.pad(img_array, ((pad_height, pad_height), (pad_width, pad_width), (0, 0)), mode='edge')

    output_img_array = np.zeros_like(img_array)
    
    for i in range(image_height):
        for j in range(image_width):

            pixel_sum = np.zeros(image_channels, dtype=np.float32)

            for n in range(kernel_height):
                for m in range(kernel_width):

                    weight = kernel[n,m]
                    pixel_value = padded_img_array[i + n, j + m, :]
                    pixel_sum += pixel_value * weight

            output_img_array[i, j, :]= pixel_sum

    output_img_array = np.clip(output_img_array, 0, 255).astype(np.uint8)
    return Image.fromarray(output_img_array)

def apply_filter(image: Image.Image, filter_name: str, optimized: bool = True, sigma: float = 1.0, strength: float = 1.0, kernel_size: int = 3) -> Image.Image:
    if filter_name in FILTER_CONFIG:
        kernel_function = FILTER_CONFIG[filter_name]

        if filter_name == "Gaussian":
            kernel = kernel_function(sigma=sigma, size=kernel_size)
        elif filter_name == "Sharpening":
            kernel = kernel_function(strength=strength)
        elif filter_name == "Averaging":
            kernel = kernel_function(size=kernel_size)
        else:
            kernel = kernel_function()

        if optimized:
            return optimized_convolution(image, kernel)
        else:
            return basic_convolution(image, kernel)
    else:
        raise ValueError(f"Filter '{filter_name}' is not defined in FILTER_CONFIG.")
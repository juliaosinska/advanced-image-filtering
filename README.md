# Image Filtering App

Base of this solution can be accessed in this repository: [image-filtering](https://github.com/juliaosinska/image-filtering)

Current project repository: [advanced-image-filtering](https://github.com/juliaosinska/advanced-image-filtering)

A small Python desktop app for applying convolution-based image filters.

## Overview

This project lets you upload an image, choose a filter, adjust its parameters, preview the result, and save the processed output. The app uses NumPy and Pillow for image processing and includes optional optimized convolution paths for faster execution.

## Included filters

- Averaging
- Separable Gaussian
- Sharpening
- Laplacian
- Unsharp Mask (USM)
- High-Boost Filter
- Difference of Gaussians (DoG)
- Laplacian of Gaussian (LoG)

## Features

- Upload an image from disk
- Preview the original image and filtered output side by side
- View multiple intermediate previews for advanced filters
- Adjust parameters such as kernel size, sigma, strength, and boost factor
- Toggle between optimized and basic convolution implementations
- Save the filtered image as PNG or JPG

## Filter descriptions and parameter effects

### Averaging
- Purpose: smooths the image and reduces noise by replacing each pixel with the average of nearby pixels.
- Effect of parameters: the `Kernel Size` controls the neighborhood size. A larger kernel produces stronger blur, softer transitions, and less visible detail.

### Separable Gaussian
- Purpose: applies Gaussian blur, commonly used to smooth images and prepare them for other enhancement techniques.
- Effect of parameters: the `Sigma` value controls the amount of blur. Larger sigma values produce stronger smoothing and suppress fine details and edges more aggressively.

### Sharpening
- Purpose: increases local contrast around edges to make the image appear sharper.
- Effect of parameters: the `Strength` parameter controls the amount of edge enhancement. Higher values produce stronger sharpening but may introduce halos or unnatural artifacts if set too high.

### Laplacian
- Purpose: highlights rapid intensity changes and detects edges in the image.
- Effect of parameters: the `Laplacian Size` changes the kernel size used for edge detection. Larger kernels detect broader transitions and produce heavier, thicker edge responses.

#### Note: you can see the examples for those basic filters in the related repo: [image-filtering](https://github.com/juliaosinska/image-filtering)

### Unsharp Mask (USM)
- Purpose: creates a sharper image by emphasizing the difference between the original image and its blurred version.
- Effect of parameters: `Sigma` defines the blur used to create the mask; larger sigma gives a smoother base image and a broader sharpening effect. `Alpha` controls the strength of the enhancement; higher values make edges more pronounced but can over-sharpen the image.
<img width="1196" height="878" alt="image" src="https://github.com/user-attachments/assets/eee6b357-728a-4733-8b28-906d01a12af4" />

### High-Boost Filter
- Purpose: enhances fine details more strongly than a standard unsharp mask while preserving contrast in the image.
- Effect of parameters: `Sigma` controls the amount of initial blur, while `A (Boost Factor)` controls the enhancement strength. Larger values increase detail contrast and edge emphasis, but too high a value can make the image look exaggerated or unnatural.
<img width="1197" height="878" alt="image" src="https://github.com/user-attachments/assets/31f672b5-78a5-4494-b58e-88ccba51f0c1" />

### Difference of Gaussians (DoG)
- Purpose: detects edges and features by subtracting one blurred version of the image from another with a different blur scale.
- Effect of parameters: `Sigma 1` and `Sigma 2` control the two Gaussian blurs. Increasing either sigma emphasizes larger image structures, while the difference between the values determines which details stand out most.
<img width="1194" height="877" alt="image" src="https://github.com/user-attachments/assets/e720679c-404b-451e-9fbc-72ce812251f2" />

### Laplacian of Gaussian (LoG)
- Purpose: combines Gaussian smoothing and Laplacian edge detection to detect edges and blob-like structures.
- Effect of parameters: `Sigma` sets the smoothing scale; larger values suppress fine details and emphasize larger structures. `Laplacian Size` changes the sensitivity and thickness of the detected edges.
<img width="1194" height="876" alt="image" src="https://github.com/user-attachments/assets/9ccc4b5d-0fe2-4d52-8915-6e021e937d2d" />

## Project structure

- `gui.py` — Tkinter GUI and user controls
- `processors.py` — filter implementations and processor registry
- `convolution.py` — low-level convolution operations
- `filters_config.py` — filter definitions and parameter metadata

## Requirements

Install the required libraries before running the app:

```bash
pip install pillow numpy
```

## Run the app

From the project root:

```bash
python gui.py
```

## Notes

   ### GenAI tools used - Gemini for:
   - User Interface implementation (desktop window, user controls etc.),
   - helping with the development of the optimized convolution (vectorization for faster image processing),
   - handling image edges,
   - getting the Gaussian filter kernel formula right for adjustable sigma value,
   - helping to prepare the `filters_config.py` file by gathering all necessary parameters in one place,
   - helping with adjusting the high-boost formula to ensure avoiding dark images,
   - helped with adjusting the LoG output to ensure proper visualization by shifting the values by +128 to bring negative values into the visible range,
   - some basic debugging of erros caused by e.g. overlooked type changes needed to be applied in a few places,
   - README.md generation (except the `Notes` section).

   ### DoG vs LoG
   - Both methods are based on Gaussian smoothing followed by a second-order response, so they often highlight similar edges and blob-like structures when the parameters are chosen appropriately.
   - DoG is a direct subtraction of two Gaussian-smoothed images, while LoG applies a Laplacian operator after Gaussian filtering. In practice, LoG is more continuous and can be interpreted as a scale-normalized edge detector, while DoG is often simpler and computationally convenient as an approximation of LoG.
   - When `sigma1` and `sigma2` in DoG are close together, the DoG response approximates the LoG response around a certain scale. This is why both techniques tend to give similar edge localization and feature detection results for comparable scales.

   ### High-Boost relation to Unsharp Mask
   The high-boost filter is defined as
  `H = A · I − Gσ`, where `A ≥ 1`.
  Since `I − Gσ` is the high-frequency mask, we can rewrite it as
  `H = I + (A − 1) · (I − Gσ)`.
  This is exactly the unsharp-mask form
  `U = I + α · (I − Gσ)`
  with `α = A − 1`.
  Therefore, the high-boost filter is a generalization of USM: for `A = 1`, the enhancement term disappears, and for `A > 1` the image is sharpened proportionally to `A − 1`.

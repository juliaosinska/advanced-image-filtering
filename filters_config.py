# GENAI: Gemini - help with moving all existing base filters to a new config file
# and adding new advancedfilters with their parameters and previews

FILTER_CONFIG = {
    # ==========================================
    # 1. BASE FILTERS
    # ==========================================
    "Averaging": {
        "type": "basic",
        "processor": "run_averaging",
        "params": {
            "kernel_size": {"label": "Kernel Size", "type": "int", "default": 3, "min": 3, "max": 7, "step": 2}
        },
        "previews": ["Original", "Filtered"]
    },
    "Separable Gaussian": {
        "type": "basic",
        "processor": "run_gaussian_separable",
        "params": {
            "sigma": {"label": "Sigma", "type": "float", "default": 1.0, "min": 0.5, "max": 5.0, "step": 0.1}
        },
        "previews": ["Original", "Filtered"]
    },
    "Sharpening": {
        "type": "basic",
        "processor": "run_sharpening",
        "params": {
            "strength": {"label": "Strength", "type": "float", "default": 1.0, "min": 0.1, "max": 5.0, "step": 0.1}
        },
        "previews": ["Original", "Filtered"]
    },
    "Laplacian": {
        "type": "basic",
        "processor": "run_laplacian",
        "params": {
            "laplacian_size": {"label": "Laplacian Size", "type": "int", "default": 3, "min": 3, "max": 9, "step": 2}
        },
        "previews": ["Original", "Filtered"]
    },

    # ==========================================
    # 2. ADVANCED FILTERS
    # ==========================================
    "Unsharp Mask (USM)": {
        "type": "combination",
        "processor": "run_unsharp_mask",
        "params": {
            "sigma": {"label": "Sigma (Blur)", "type": "float", "default": 1.0, "min": 0.5, "max": 5.0, "step": 0.1},
            "alpha": {"label": "Alpha (Strength)", "type": "float", "default": 1.0, "min": 0.5, "max": 5.0, "step": 0.1}
        },
        "previews": ["Original (I)", "Gaussian (Gσ)", "Mask (I − Gσ)", "Unsharp (U)"]
    },
    
    "High-Boost Filter": {
        "type": "combination",
        "processor": "run_high_boost",
        "params": {
            "sigma": {"label": "Sigma (Blur)", "type": "float", "default": 1.0, "min": 0.5, "max": 5.0, "step": 0.1},
            "a_param": {"label": "A (Boost Factor)", "type": "float", "default": 1.2, "min": 1.0, "max": 3.0, "step": 0.1}
        },
        "previews": ["Original (I)", "Gaussian (Gσ)", "High-Boost (H)"]
    },

    "Difference of Gaussians (DoG)": {
        "type": "combination",
        "processor": "run_dog",
        "params": {
            "sigma1": {"label": "Sigma 1", "type": "float", "default": 1.0, "min": 0.5, "max": 3.0, "step": 0.1},
            "sigma2": {"label": "Sigma 2", "type": "float", "default": 2.0, "min": 1.0, "max": 6.0, "step": 0.1}
        },
        "previews": ["Original", "Gaussian 1 (σ₁)", "Gaussian 2 (σ₂)", "DoG (D)"]
    },

    "Laplacian of Gaussian (LoG)": {
        "type": "combination",
        "processor": "run_log",
        "params": {
            "sigma": {"label": "Sigma (Gaussian)", "type": "float", "default": 1.0, "min": 0.5, "max": 4.0, "step": 0.1},
            "laplacian_size": {"label": "Laplacian Size", "type": "int", "default": 3, "min": 3, "max": 9, "step": 2}
        },
        "previews": ["Original", "Gaussian (Gσ)", "LoG Result"]
    },
}
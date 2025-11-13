"""
Setup configuration for Model Fine-Tuning Platform CLI.
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file) as f:
        requirements = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith('#') and not line.startswith('git+')
        ]

# Add CLI-specific requirements
cli_requirements = [
    'click>=8.1.0',
    'requests>=2.31.0',
]

# Combine requirements, avoiding duplicates
all_requirements = list(set(requirements + cli_requirements))

setup(
    name="model-train",
    version="0.1.0",
    description="Comprehensive CLI for ML model fine-tuning with XML pattern synthesis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Model Train Team",
    author_email="team@modeltrain.dev",
    url="https://github.com/yourusername/model-train",
    license="MIT",

    # Package discovery
    packages=find_packages(exclude=["tests", "tests.*"]),

    # Include package data
    include_package_data=True,

    # Python version requirement
    python_requires=">=3.8",

    # Dependencies
    install_requires=cli_requirements,  # Only CLI deps for minimal install

    # Optional dependencies for full installation
    extras_require={
        "full": all_requirements,
        "dev": [
            "pytest>=7.4.4",
            "black>=24.1.0",
            "ruff>=0.1.14",
            "mypy>=1.0.0",
        ],
        "backend": [
            "fastapi>=0.109.0",
            "uvicorn[standard]>=0.27.0",
            "pydantic>=2.5.3",
        ],
    },

    # Console scripts entry point
    entry_points={
        "console_scripts": [
            "model-train=cli.main:main",
        ],
    },

    # Classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    # Keywords
    keywords=[
        "machine-learning",
        "fine-tuning",
        "llm",
        "training",
        "cli",
        "xml-patterns",
        "synthetic-data",
        "lora",
        "unsloth",
    ],

    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/yourusername/model-train/issues",
        "Source": "https://github.com/yourusername/model-train",
        "Documentation": "https://github.com/yourusername/model-train/wiki",
    },
)

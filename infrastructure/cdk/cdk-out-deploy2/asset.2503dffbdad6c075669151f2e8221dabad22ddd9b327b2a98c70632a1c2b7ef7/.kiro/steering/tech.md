# Technology Stack

## Core Technologies

- **Python 3.10+**: Primary language
- **PyTorch 2.8.0**: Deep learning framework with CUDA 12.8 support
- **Diffusers 0.35.2**: Hugging Face diffusion models library (custom git version)
- **Transformers 4.57.1**: Hugging Face transformers for text encoding
- **Accelerate**: Multi-GPU and distributed training support

## Key Dependencies

- **google-genai**: Gemini API integration for VLM capabilities
- **huggingface-hub**: Model hosting and downloading
- **PEFT**: Parameter-Efficient Fine-Tuning (LoRA support)
- **bitsandbytes**: Quantization and optimization
- **einops**: Tensor operations
- **datasets**: Data loading and processing

## Package Management

- **uv**: Modern Python package manager (replaces pip/poetry)
- **pyproject.toml**: Project configuration and dependencies
- **uv.lock**: Lockfile for reproducible builds

## Development Tools

- **Ruff**: Fast Python linter and formatter (replaces black, flake8, isort)
- **pre-commit**: Git hooks for code quality
- **pytest**: Testing framework
- **Makefile**: Development task automation

## Common Commands

### Setup
```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate
export PYTHONPATH=${PYTHONPATH}:${PWD}

# Install dev tools and pre-commit hooks
make install
```

### Development
```bash
# Run linters (no changes)
make lint

# Auto-format code
make format

# Run all checks (lint + format)
make check

# Run tests
pytest
# or
python tests/test_all_modes.py
```

### Generation
```bash
# Basic generation with Gemini VLM
python generate.py --prompt "your prompt" --seed 1

# Use local VLM instead of Gemini
python generate.py --prompt "your prompt" --model-mode local

# Enable TeaCache for 3x speed boost
python generate.py --prompt "your prompt" --enable-teacache

# Refine existing structured prompt
python generate.py --structured-prompt output.json --prompt "make it blue"

# Generate from image inspiration
python generate.py --image-path image.jpg --prompt "make it futuristic"
```

### Environment Variables
- `GOOGLE_API_KEY`: Required for Gemini VLM mode
- `PYTHONPATH`: Must include project root for imports
# Project Structure

## Root Level Files

- `generate.py`: Main CLI entry point for image generation
- `pyproject.toml`: Project configuration, dependencies, and tool settings
- `Makefile`: Development automation (install, lint, format, test)
- `default_json_caption.json`: Default structured prompt used by demo
- `uv.lock`: Dependency lockfile for reproducible builds

## Source Code Organization

### `src/fibo_inference/`
Core inference pipeline and utilities:

- `fibo_pipeline.py`: Main FIBO pipeline implementation
- `inference.py`: High-level inference functions and pipeline creation
- `parse_caption.py`: JSON caption parsing and cleaning utilities
- `prompt_to_json.py`: VLM prompt expansion logic
- `transformer_fibo.py`: FIBO transformer model implementation
- `teacache.py`: TeaCache optimization for faster inference
- `pipeline_output.py`: Output handling and formatting

#### `src/fibo_inference/vlm/`
Vision-Language Model integrations:

- `common.py`: Shared VLM utilities and configurations
- `gemini_api.py`: Google Gemini API integration
- `local_vlm.py`: Local VLM (FIBO-VLM) implementation

### `src/fine_tuning/`
Fine-tuning capabilities and utilities:

- `fine_tune_fibo.py`: Main fine-tuning script using LoRA
- `fine_tune_utils.py`: Fine-tuning helper functions
- `generate_with_lora.py`: Generation with LoRA checkpoints
- `example_structured_prompt.json`: Example structured prompt format
- `vae_config.json`: VAE configuration for fine-tuning
- `exmaple_finetune_data/`: Sample dataset with images and metadata.csv

## Assets and Examples

- `assets/`: Demo images, logos, and example outputs
- `examples/`: Usage examples and documentation
- `examples/outputs/`: Generated example images (created during runtime)

## Testing

- `tests/test_all_modes.py`: Integration tests for all generation modes
- Tests cover Generate, Refine, and Inspire modes with local VLM

## Code Conventions

### Import Structure
- Absolute imports from `src/` packages
- Local imports use relative paths within modules
- External dependencies imported first, then local modules

### File Naming
- Snake_case for Python files and directories
- Descriptive names that indicate functionality
- VLM-related code isolated in `vlm/` subdirectory

### Configuration Files
- JSON for structured prompts and model configs
- TOML for project configuration (pyproject.toml)
- CSV for dataset metadata (fine-tuning)

### Output Organization
- Generated images saved with corresponding `.json` structured prompts
- Outputs organized by task type (generate, refine, inspire)
- Fine-tuning checkpoints saved in separate results directories
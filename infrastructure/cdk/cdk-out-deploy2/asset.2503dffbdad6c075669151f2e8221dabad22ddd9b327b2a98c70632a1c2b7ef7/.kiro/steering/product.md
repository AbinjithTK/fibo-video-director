# FIBO Product Overview

FIBO is an open-source, JSON-native text-to-image model designed for professional workflows and enterprise use. It's the first model trained exclusively on long structured captions (up to 1,000+ words) using only licensed data.

## Key Capabilities

- **Structured JSON prompting**: Uses detailed JSON schemas for precise control over lighting, composition, color, and camera settings
- **Three generation modes**:
  - **Generate**: Transform short prompts into detailed structured prompts and generate images
  - **Refine**: Iteratively modify specific attributes without breaking the scene
  - **Inspire**: Extract structured prompts from images and generate variations
- **Professional control**: Native disentanglement allows targeted refinement without prompt drift
- **Enterprise-grade**: 100% licensed data with governance and legal compliance
- **VLM integration**: Uses Vision-Language Models (Gemini 2.5 Flash or local FIBO-VLM) for prompt expansion

## Architecture

- 8B-parameter DiT-based flow-matching model
- SmolLM3-3B text encoder with DimFusion conditioning
- Wan 2.2 VAE
- TeaCache support for 3x faster inference with minimal quality loss

## Licensing

- Open source for non-commercial use (CC BY-NC 4.0)
- Commercial licensing available through Bria.ai
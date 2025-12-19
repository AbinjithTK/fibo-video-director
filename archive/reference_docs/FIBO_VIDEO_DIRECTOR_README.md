# FIBO Video Director

A complete AI-powered video generation system that transforms movie scripts into FIBO-generated video sequences through an intelligent checkpoint-based workflow.

## 🎬 Overview

The FIBO Video Director combines:
- **AI Script Analysis**: Strands agents analyze movie scripts and break them into 8-second segments
- **Checkpoint System**: Each segment becomes a selectable checkpoint with detailed FIBO prompts
- **FIBO Integration**: Direct integration with FIBO for consistent, high-quality frame generation
- **React Frontend**: Modern web interface for script input, checkpoint management, and frame generation

## 🏗️ Architecture

```
Movie Script → AI Director → Checkpoints → FIBO Generation → Video Frames
     ↓              ↓            ↓              ↓              ↓
  Text Input   Strands Agent  JSON Prompts   Image Files   Final Video
```

### Components

1. **Backend (Python)**
   - `fibo_video_director.py`: Standard AI Director using Strands agents
   - `enhanced_fibo_director.py`: Enhanced multi-agent system with Strands Swarm pattern
   - `api_server.py`: FastAPI server with REST endpoints
   - `fibo_integration.py`: Direct FIBO integration service

2. **Frontend (React)**
   - Script input with sample scripts
   - Interactive timeline with checkpoints
   - Frame generation with progress tracking
   - Download management for generated content

### Enhanced Director Features

The `enhanced_fibo_director.py` provides production-ready capabilities:

- **Strands Swarm Pattern**: Three specialized agents (Editor, Cinematographer, Action Director) collaborate
- **Shared State Management**: Cross-agent communication via `invocation_state`
- **Tool Context Integration**: Tools access shared production context
- **AgentCore Compatibility**: Ready for deployment on Amazon Bedrock AgentCore Runtime

## 🚀 Quick Start

### Prerequisites

1. **FIBO Installation**: Ensure FIBO is properly installed and working
2. **Google API Key**: Required for Gemini VLM integration
3. **Python 3.10+**: For backend services
4. **Node.js 16+**: For React frontend

### Backend Setup

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**
   ```bash
   # Required
   export GOOGLE_API_KEY=your_google_api_key
   
   # Optional
   export FIBO_ROOT=/path/to/fibo  # Defaults to current directory
   export PYTHONPATH=${PYTHONPATH}:${PWD}
   export USE_ENHANCED_DIRECTOR=true  # Enable enhanced multi-agent system
   ```

3. **Start the API Server**
   ```bash
   python start_server.py
   ```
   
   The server will start at `http://localhost:8000`

### Frontend Setup

1. **Navigate to Frontend Directory**
   ```bash
   cd frontend
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Start Development Server**
   ```bash
   npm start
   ```
   
   The frontend will start at `http://localhost:3000`

## 📋 API Endpoints

### Core Endpoints

- `POST /api/generate-plan`: Generate video plan from script
- `GET /api/project/{project_id}`: Get project details
- `GET /api/checkpoint/{project_id}/{checkpoint_id}`: Get checkpoint prompts
- `POST /api/generate-frames`: Start FIBO frame generation
- `GET /api/generation-status/{generation_id}`: Check generation progress
- `GET /api/download/{filename}`: Download generated files
- `GET /api/fibo-status`: Check FIBO integration status
- `GET /api/director-mode`: Get current director mode (standard/enhanced)
- `POST /api/director-mode`: Toggle between standard and enhanced director

### Example Usage

```javascript
// Generate video plan
const response = await fetch('/api/generate-plan', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ script_text: 'FADE IN: ...' })
});

// Start frame generation
const generation = await fetch('/api/generate-frames', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    project_id: 'uuid', 
    checkpoint_id: 1 
  })
});
```

## 🎯 Workflow

### 1. Script Input
- Enter movie script in the web interface
- Choose from sample scripts (cyberpunk, space, fantasy)
- AI Director analyzes and creates video plan

### 2. Checkpoint Management
- View interactive timeline with all checkpoints
- Each checkpoint represents an 8-second video segment
- Click checkpoints to expand and view details

### 3. Frame Generation
- Select checkpoint and click "Generate Frames"
- FIBO creates start and end frames with consistent styling
- Download generated images and structured JSON prompts

### 4. Video Assembly
- Use generated frames as keyframes for video creation
- Apply video generation prompts for motion between frames
- Maintain visual consistency across entire sequence

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google Gemini API key | Yes |
| `FIBO_ROOT` | Path to FIBO installation | No (defaults to `.`) |
| `PYTHONPATH` | Python path including FIBO | No (auto-set) |

### FIBO Integration

The system integrates directly with your existing FIBO installation:

```python
# Automatic integration with generate.py
python generate.py --structured-prompt checkpoint_1_start.json --output-name frame_1_start

# Supports all FIBO features
--enable-teacache    # 3x faster generation
--model-mode local   # Use local VLM instead of Gemini
--seed 42           # Reproducible generation
```

## 📁 File Structure

```
FIBO-main/
├── fibo_video_director.py      # AI Director (Strands agents)
├── api_server.py               # FastAPI backend
├── fibo_integration.py         # FIBO integration service
├── start_server.py             # Server startup script
├── requirements.txt            # Python dependencies
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── services/          # API integration
│   │   └── App.js             # Main application
│   └── package.json           # Node dependencies
├── cache/                     # Generated files cache
└── examples/outputs/          # FIBO output directory
```

## 🎨 Features

### AI Director Capabilities
- **Script Analysis**: Intelligent parsing of movie scripts
- **Scene Segmentation**: Automatic 8-second checkpoint creation
- **Visual Consistency**: Unified style across all segments
- **FIBO Optimization**: Structured JSON prompts optimized for FIBO

### Frontend Features
- **Interactive Timeline**: Visual checkpoint management
- **Real-time Progress**: Live generation status updates
- **Download Management**: Easy access to generated content
- **Responsive Design**: Works on desktop and mobile
- **Caching System**: Efficient data management

### FIBO Integration
- **Direct Integration**: Uses existing FIBO installation
- **Structured Prompts**: Detailed JSON for consistent generation
- **TeaCache Support**: 3x faster generation when enabled
- **Fallback Mode**: JSON-only mode if FIBO generation fails

## 🔍 Troubleshooting

### Common Issues

1. **FIBO Not Found**
   ```
   Error: FIBO generate.py not found
   Solution: Ensure you're running from FIBO project root
   ```

2. **API Key Missing**
   ```
   Error: GOOGLE_API_KEY not set
   Solution: Set environment variable with your Gemini API key
   ```

3. **Generation Fails**
   ```
   Error: FIBO generation failed
   Solution: Check FIBO installation and dependencies
   ```

### Debug Mode

Enable debug logging:
```bash
export FASTMCP_LOG_LEVEL=DEBUG
python start_server.py
```

### Health Checks

Check system status:
```bash
curl http://localhost:8000/api/fibo-status
```

## 🚀 Production Deployment

### Docker Deployment (Recommended)

```dockerfile
FROM python:3.10-slim

# Install FIBO and dependencies
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

# Build frontend
RUN cd frontend && npm install && npm run build

# Start server
CMD ["python", "start_server.py"]
```

### Environment Setup

```bash
# Production environment variables
export GOOGLE_API_KEY=your_production_key
export FIBO_ROOT=/app
export NODE_ENV=production
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project extends FIBO's licensing:
- **Non-commercial use**: CC BY-NC 4.0
- **Commercial licensing**: Available through Bria.ai

## 🙏 Acknowledgments

- **FIBO Team**: For the amazing JSON-native image generation model
- **Strands SDK**: For powerful AI agent capabilities
- **React Community**: For excellent frontend tools
- **FastAPI**: For high-performance API framework

---

**Ready to transform your movie scripts into AI-generated videos? Start with the Quick Start guide above!** 🎬✨
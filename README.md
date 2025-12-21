# 🎬 FIBO Video Director

> **Transform movie scripts into AI-generated video sequences with FIBO's multi-agent system**

A sophisticated video production planning tool that uses **multi-agent AI collaboration** to convert movie scripts into detailed FIBO prompts for professional video generation.

![FIBO Video Director](https://img.shields.io/badge/FIBO-Video%20Director-blue?style=for-the-badge)
![Multi-Agent](https://img.shields.io/badge/Multi--Agent-Swarm-green?style=for-the-badge)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react)
![Python](https://img.shields.io/badge/Python-Backend-3776AB?style=for-the-badge&logo=python)

## ✨ Features

### 🤖 Multi-Agent AI System
- **Script Analyst Agent**: Analyzes narrative structure and pacing
- **Visual Director Agent**: Makes cinematographic decisions
- **FIBO Specialist Agent**: Creates detailed technical prompts

### 🎥 Professional Video Planning
- **Intelligent Script Segmentation**: Breaks scripts into 8-second video segments
- **Cinematic Analysis**: Professional lighting, camera angles, and composition
- **FIBO Integration**: Generates detailed JSON prompts for FIBO image generation
- **Visual Consistency**: Maintains style across all video segments

### 🌐 Modern Web Interface
- **React Frontend**: Intuitive script input and timeline visualization
- **Real-time Processing**: Watch agents collaborate in real-time
- **Interactive Timeline**: Click checkpoints to view detailed FIBO prompts
- **Professional UI**: Clean, modern interface for video production

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** with pip
- **Node.js 16+** and npm
- **Google Gemini API Key** (free tier available)
- **FAL.ai API Key** for image generation

### 1. Clone Repository

```bash
git clone https://github.com/AbinjithTK/fibo-video-director.git
cd fibo-video-director
```

### 2. Setup Environment

```bash
# Install Python dependencies
pip install -r requirements.txt

# Setup environment variables
python scripts/setup-env.py

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 3. Start the Application

**Terminal 1: Start Backend**
```bash
python app.py
```

**Terminal 2: Start Frontend**
```bash
cd frontend
npm start
```

### 4. Test & Open

```bash
# Verify setup is working
python test_local_setup.py

# Open in browser
# http://localhost:3000
```

That's it! 🎬 Your FIBO Video Director is ready!

## 📖 Usage Guide

### Basic Workflow

1. **Paste Your Script**: Enter your movie script in the text area
2. **Generate Plan**: Click "Generate Video Plan" to start multi-agent processing
3. **View Timeline**: Explore generated checkpoints on the interactive timeline
4. **Review FIBO Prompts**: Click checkpoints to see detailed FIBO prompts
5. **Generate Images**: Use the FIBO prompts with FAL.ai or local FIBO

### Sample Scripts

The application includes sample scripts for:
- 🌃 **Cyberpunk Heist**: Neon-lit city infiltration
- 🚀 **Space Adventure**: Spaceship under alien attack  
- 🧙 **Fantasy Quest**: Enchanted forest dragon encounter

## 🧪 Testing & Validation

### Run Complete System Test

```bash
python tests/integration/test_full_system.py
```

This validates:
- ✅ Environment configuration
- ✅ Multi-agent system functionality
- ✅ API server endpoints
- ✅ Frontend-backend integration

### Run Local Workflow Test

```bash
python tests/integration/test_local_workflow.py
```

Tests the complete user workflow from script input to FIBO prompt generation.

## 🏗️ Architecture

### Backend (Python)
- **FastAPI**: High-performance API server
- **Strands Agents**: Multi-agent collaboration framework
- **Google Gemini**: Advanced language model for script analysis
- **FAL.ai Integration**: Professional image generation

### Frontend (React)
- **Modern React**: Hooks-based component architecture
- **Real-time Updates**: Live agent processing feedback
- **Responsive Design**: Works on desktop and mobile
- **Professional UI**: Clean, intuitive interface

### Multi-Agent System
```
Script Input → Script Analyst → Visual Director → FIBO Specialist → Video Plan
```

## 🔧 Configuration

### Environment Variables

Create `.env` file with:

```env
# Required: Google Gemini API Key
GOOGLE_API_KEY=your_google_gemini_api_key_here

# Required: FAL.ai API Key for image generation
FAL_KEY=your_fal_api_key_here

# Optional: S3 bucket for caching
FIBO_S3_BUCKET=your_s3_bucket_name_here

# Optional: AWS credentials
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_DEFAULT_REGION=us-east-1

# Optional: Enable enhanced multi-agent director
USE_ENHANCED_DIRECTOR=true
```

### API Keys Setup

1. **Google Gemini API**: Get free API key at [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **FAL.ai API**: Sign up at [FAL.ai](https://fal.ai/) for image generation
3. **AWS (Optional)**: For S3 caching and advanced features

## 📁 Project Structure

```
fibo-video-director/
├── 🎬 Core System
│   ├── core/
│   │   ├── api_server.py              # FastAPI backend server
│   │   ├── enhanced_fibo_director.py  # Multi-agent director system
│   │   ├── working_fibo_director.py   # Fallback director
│   │   └── fal_fibo_integration.py    # FAL.ai integration
├── 🌐 Frontend
│   ├── frontend/src/App.js            # Main React application
│   ├── frontend/src/components/       # React components
│   └── frontend/src/services/         # API services
├── 🧪 Testing
│   ├── tests/integration/
│   │   ├── test_full_system.py        # Complete system validation
│   │   └── test_local_workflow.py     # End-to-end workflow test
│   └── test_app.py                    # Quick structure test
├── ⚙️ Scripts & Setup
│   ├── scripts/
│   │   ├── setup-env.py               # Interactive environment setup
│   │   └── start_fibo_app.py          # Application launcher
│   ├── app.py                         # Main application entry point
│   └── .env.example                   # Environment template
├── 📁 Archive & Reference
│   ├── archive/old_implementations/   # Previous versions for reference
│   ├── archive/test_scripts/          # Development test scripts
│   └── archive/reference_docs/        # Technical documentation
└── 📚 Documentation
    └── README.md                      # This file
```

## 🔍 Troubleshooting

### Common Issues

**"API quota exceeded"**
- Gemini free tier has 20 requests/day limit
- Upgrade to paid plan or wait for quota reset

**"Frontend not loading"**
- Ensure both backend (port 8000) and frontend (port 3000) are running
- Check browser console for errors

**"Multi-agent system not working"**
- Verify `GOOGLE_API_KEY` is set correctly
- Check `USE_ENHANCED_DIRECTOR=true` in `.env`

### Debug Mode

Enable detailed logging:
```bash
export FASTMCP_LOG_LEVEL=DEBUG
python api_server.py
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FIBO Team** for the revolutionary JSON-native image generation model
- **Strands Framework** for multi-agent collaboration capabilities
- **Google Gemini** for advanced language understanding
- **FAL.ai** for professional image generation services

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/AbinjithTK/fibo-video-director/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/AbinjithTK/fibo-video-director/discussions)
- 📧 **Email**: [Your Email Here]

---

<div align="center">

**⭐ Star this repository if you find it useful!**

Made with ❤️ for the AI video generation community

</div>
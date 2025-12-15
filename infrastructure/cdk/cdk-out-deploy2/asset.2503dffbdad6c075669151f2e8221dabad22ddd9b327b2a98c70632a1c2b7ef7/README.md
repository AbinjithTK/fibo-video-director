<p align="center">
  <img src="assets/Bria-logo.svg" width="200"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/AI%20Movie%20Director-Production%20Ready-FF6B6B?style=for-the-badge" alt="AI Movie Director"/>
  &nbsp;
  <img src="https://img.shields.io/badge/Video%20Generation-Veo%20Compatible-4ECDC4?style=for-the-badge" alt="Veo Compatible"/>
  &nbsp;
  <img src="https://img.shields.io/badge/Script%20Analysis-AI%20Powered-45B7D1?style=for-the-badge" alt="AI Powered"/>
</p>

<p align="center">
  <b>AI Movie Director: Intelligent script-to-video production pipeline for AI video producers</b>
  <br><br>
  <i>Transform scripts into structured shot divisions with precise prompts for 8-second video segments</i>
</p>

<!-- ===================== MAIN CONTENT ===================== -->

<h2>🎬 What's AI Movie Director?</h2>
<p>AI Movie Director revolutionizes video production by intelligently analyzing scripts and generating structured shot divisions optimized for AI video generation models like Veo. Upload your script and receive professional-grade shot breakdowns with precise start/end frame descriptions and detailed prompts for each 8-second video segment.</p>

<h2>🔑 Key Features</h2>
<ul>
  <li><b>Intelligent Script Analysis</b>: AI-powered parsing of scripts to identify scenes, actions, and visual elements</li>
  <li><b>Automated Shot Division</b>: Smart segmentation into optimal 8-second video chunks for AI video models</li>
  <li><b>Detailed Frame Prompts</b>: Generate precise start and end frame descriptions for each video segment</li>
  <li><b>Veo Model Integration</b>: Optimized prompts specifically designed for Veo and similar video generation models</li>
  <li><b>Production-Ready Output</b>: Export structured JSON with all shot data for seamless video production workflow</li>
  <li><b>Web Interface</b>: User-friendly frontend for script upload and shot management</li>
  <li><b>AWS Deployment</b>: Scalable cloud infrastructure with CDK for enterprise use</li>
</ul>

<h2>🎯 How It Works</h2>

<ul>
  <li>
    <b>Script Upload:</b> Upload your screenplay or script through the web interface. The AI analyzes narrative structure, dialogue, and scene descriptions.
  </li>
  <li>
    <b>Shot Division:</b> Advanced AI algorithms automatically divide your script into optimal 8-second segments, considering pacing, action sequences, and visual continuity.
  </li>
  <li>
    <b>Prompt Generation:</b> Each shot receives detailed start and end frame descriptions, camera angles, lighting conditions, and visual elements optimized for video AI models.
  </li>
  <li>
    <b>Export & Produce:</b> Download structured JSON files containing all shot data, ready for input into Veo or other video generation platforms.
  </li>
</ul>

<h2>📋 Output Format</h2>

Each processed script generates a structured JSON with the following format:

```json
{
  "project_title": "Your Movie Title",
  "total_shots": 25,
  "estimated_duration": "200 seconds",
  "shots": [
    {
      "shot_id": 1,
      "duration": 8,
      "scene_description": "Opening establishing shot",
      "start_frame_prompt": "Wide aerial view of a bustling city at dawn, golden sunlight reflecting off glass buildings, camera slowly descending towards the main street",
      "end_frame_prompt": "Close-up of the protagonist walking confidently down the sidewalk, morning light creating dramatic shadows",
      "camera_movement": "Aerial descent to ground level",
      "lighting": "Golden hour, natural sunlight",
      "mood": "Optimistic, energetic"
    }
  ]
}
```

<h2>⚡ Quick Start</h2>

### Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend)
- AWS CLI configured (for deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/ai-movie-director.git
   cd ai-movie-director
   ```

2. **Install Python dependencies**
   ```bash
   uv sync
   source .venv/bin/activate
   export PYTHONPATH=${PYTHONPATH}:${PWD}
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (OpenAI, Anthropic, etc.)
   ```

4. **Start the backend server**
   ```bash
   python api_server.py
   ```

5. **Start the frontend (in a new terminal)**
   ```bash
   cd frontend
   npm install
   npm start
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000

### Using the API

**Process a script:**
```bash
curl -X POST http://localhost:8000/api/process-script \
  -H "Content-Type: application/json" \
  -d '{
    "script_content": "FADE IN: EXT. CITY STREET - DAWN...",
    "project_title": "My Movie",
    "target_duration": 120
  }'
```

**Get shot details:**
```bash
curl http://localhost:8000/api/shots/{project_id}
```

<h2>🚀 Deployment</h2>

### AWS Deployment with CDK

1. **Install AWS CDK**
   ```bash
   npm install -g aws-cdk
   ```

2. **Deploy infrastructure**
   ```bash
   cd infrastructure/cdk
   npm install
   cdk bootstrap
   cdk deploy
   ```

3. **Deploy application**
   ```bash
   make deploy
   ```

The deployment includes:
- API Gateway for REST endpoints
- Lambda functions for script processing
- S3 bucket for script storage
- CloudFront distribution for frontend
- DynamoDB for shot metadata

<h2>🎥 Supported Video Models</h2>

AI Movie Director generates prompts optimized for:

- **Google Veo**: Primary target with 8-second segment optimization
- **Runway ML**: Compatible prompt format
- **Pika Labs**: Adapted for their prompt structure
- **Stable Video Diffusion**: Basic compatibility
- **Custom Models**: Extensible prompt templates

<h2>📁 Project Structure</h2>

```
ai-movie-director/
├── api_server.py              # Main API server
├── enhanced_fibo_director.py  # Core script analysis engine
├── fibo_video_director.py     # Video-specific processing
├── frontend/                  # React web interface
│   ├── src/components/        # UI components
│   └── src/services/          # API integration
├── infrastructure/            # AWS CDK deployment
│   └── cdk/                   # Infrastructure as code
├── agentcore_fibo_agent/      # AWS AgentCore integration
└── tests/                     # Test suites
```

<h2>🔧 Configuration</h2>

### Environment Variables

```bash
# AI Model Configuration
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# AWS Configuration (for deployment)
AWS_REGION=us-east-1
S3_BUCKET=your-scripts-bucket

# Application Settings
MAX_SCRIPT_LENGTH=50000
DEFAULT_SHOT_DURATION=8
MAX_SHOTS_PER_SCRIPT=100
```

### Customizing Shot Duration

Modify the default 8-second segments:

```python
# In enhanced_fibo_director.py
SHOT_DURATION = 10  # Change to 10 seconds
```

<h2>🧪 Testing</h2>

Run the test suite:

```bash
# Unit tests
pytest tests/

# Integration tests
python tests/test_script_processing.py

# End-to-end tests
python tests/test_api_endpoints.py
```

<h2>📊 Performance</h2>

- **Script Processing**: ~30 seconds for a 10-page script
- **Shot Generation**: ~2 seconds per 8-second segment
- **Concurrent Users**: Supports 50+ simultaneous script uploads
- **Storage**: Efficient JSON compression for large scripts

<h2>🤝 Contributing</h2>

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

<h2>📄 License</h2>

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<h2>💬 Support</h2>

- **Documentation**: Check our [Wiki](https://github.com/your-org/ai-movie-director/wiki)
- **Issues**: Report bugs on [GitHub Issues](https://github.com/your-org/ai-movie-director/issues)
- **Discussions**: Join our [GitHub Discussions](https://github.com/your-org/ai-movie-director/discussions)
- **Email**: Contact us at support@your-domain.com

<h2>🎬 Example Output</h2>

Here's what AI Movie Director generates from a simple script input:

**Input Script:**
```
FADE IN:
EXT. COFFEE SHOP - MORNING
SARAH, 25, rushes down the sidewalk, checking her phone.
She bumps into MIKE, 28, spilling his coffee.
```

**Generated Output:**
- **Shot 1** (0-8s): Wide establishing shot of busy morning street, camera pans to follow Sarah
- **Shot 2** (8-16s): Medium shot of Sarah checking phone while walking, increasing pace
- **Shot 3** (16-24s): Two-shot collision scene, coffee spill in slow motion, surprised expressions

Each shot includes detailed prompts for camera angles, lighting, character positioning, and visual effects.

---

<p align="center">
  <b>🎬 Transform your scripts into professional video productions with AI Movie Director</b>
</p>
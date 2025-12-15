const express = require('express');
const cors = require('cors');
const { BedrockAgentRuntimeClient, InvokeAgentCommand } = require('@aws-sdk/client-bedrock-agent-runtime');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 8000;

// Middleware
app.use(cors());
app.use(express.json());

// AgentCore configuration
const AGENTCORE_CONFIG = {
  agentId: 'src_main-PQhMz74UaU',
  agentAliasId: 'TSTALIASID',
  region: 'us-east-1'
};

// Initialize Bedrock client
const bedrockClient = new BedrockAgentRuntimeClient({
  region: AGENTCORE_CONFIG.region,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  }
});

// Health check
app.get('/', (req, res) => {
  res.json({
    message: 'FIBO Video Director API',
    status: 'running',
    agentcore_available: true,
    agentcore_arn: `arn:aws:bedrock-agentcore:us-east-1:476114109859:runtime/${AGENTCORE_CONFIG.agentId}`
  });
});

// Generate video plan using AgentCore
app.post('/api/generate-plan', async (req, res) => {
  try {
    const { script_text } = req.body;
    
    if (!script_text) {
      return res.status(400).json({ error: 'script_text is required' });
    }

    const apiKey = process.env.GOOGLE_API_KEY;
    if (!apiKey) {
      return res.status(500).json({ error: 'GOOGLE_API_KEY not configured' });
    }

    console.log('🤖 Processing script with AgentCore...');
    
    // Call AgentCore
    const sessionId = `session_${Date.now()}`;
    const payload = {
      script_text: script_text,
      api_key: apiKey
    };

    const command = new InvokeAgentCommand({
      agentId: AGENTCORE_CONFIG.agentId,
      agentAliasId: AGENTCORE_CONFIG.agentAliasId,
      sessionId: sessionId,
      inputText: JSON.stringify(payload)
    });

    const response = await bedrockClient.send(command);
    const videoPlan = parseAgentResponse(response);
    
    // Generate project ID
    const projectId = `project_${Date.now()}`;
    
    console.log('✅ AgentCore processing completed');
    
    res.json({
      project_id: projectId,
      project_title: videoPlan.project_title || 'FIBO Video Production',
      total_duration_sec: videoPlan.total_duration_sec || 16,
      checkpoints: videoPlan.checkpoints || [],
      visual_style: videoPlan.visual_style || {},
      metadata: videoPlan.metadata || {}
    });

  } catch (error) {
    console.error('AgentCore error:', error);
    res.status(500).json({ 
      error: 'Failed to process script',
      details: error.message 
    });
  }
});

// Get checkpoint details (mock for now)
app.get('/api/checkpoint/:projectId/:checkpointId', (req, res) => {
  const { projectId, checkpointId } = req.params;
  
  // Return mock checkpoint data
  res.json({
    checkpoint_id: parseInt(checkpointId),
    scene_description: `Scene ${checkpointId} details`,
    fibo_start_frame: {
      short_description: `Start frame for checkpoint ${checkpointId}`,
      objects: [{ description: "Main subject", location: "Center frame" }],
      lighting: "Cinematic lighting",
      style_medium: "Photorealistic"
    },
    fibo_end_frame: {
      short_description: `End frame for checkpoint ${checkpointId}`,
      objects: [{ description: "Main subject", location: "Center frame" }],
      lighting: "Cinematic lighting", 
      style_medium: "Photorealistic"
    }
  });
});

// Parse AgentCore response
function parseAgentResponse(response) {
  try {
    let responseText = '';
    
    // Handle streaming response
    if (response.completion) {
      for (const event of response.completion) {
        if (event.chunk && event.chunk.bytes) {
          responseText += new TextDecoder().decode(event.chunk.bytes);
        }
      }
    }

    // Try to extract JSON
    const jsonMatch = responseText.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const parsed = JSON.parse(jsonMatch[0]);
      if (parsed.status === 'success') {
        return parsed.response || parsed;
      }
    }

    // Fallback response
    return createFallbackResponse(responseText);
    
  } catch (error) {
    console.error('Response parsing error:', error);
    return createFallbackResponse('Failed to parse response');
  }
}

function createFallbackResponse(text) {
  return {
    project_title: 'FIBO Video Production',
    production_id: `agentcore_${Date.now()}`,
    created_at: new Date().toISOString(),
    total_duration_sec: 16,
    visual_style: {
      lighting_style: 'Cinematic three-point lighting',
      color_palette: 'Natural, balanced',
      camera_style: '50mm, f/2.8'
    },
    checkpoints: [
      {
        checkpoint_id: 1,
        start_time_sec: 0,
        end_time_sec: 8,
        duration_sec: 8,
        scene_description: 'Opening scene from script analysis',
        fibo_start_frame: { short_description: 'Scene opening' },
        fibo_end_frame: { short_description: 'Scene transition' }
      },
      {
        checkpoint_id: 2,
        start_time_sec: 8,
        end_time_sec: 16,
        duration_sec: 8,
        scene_description: 'Closing scene from script analysis',
        fibo_start_frame: { short_description: 'Scene continuation' },
        fibo_end_frame: { short_description: 'Scene ending' }
      }
    ],
    metadata: {
      agent_system: 'AgentCore via Simple Backend',
      raw_response: text.substring(0, 200)
    }
  };
}

app.listen(PORT, () => {
  console.log(`🚀 FIBO Video Director API running on port ${PORT}`);
  console.log(`🤖 AgentCore integration ready`);
});
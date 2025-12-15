const { BedrockAgentRuntimeClient, InvokeAgentCommand } = require('@aws-sdk/client-bedrock-agent-runtime');

// AgentCore configuration
const AGENTCORE_CONFIG = {
  agentId: 'src_main-PQhMz74UaU',
  agentAliasId: 'TSTALIASID',
  region: 'us-east-1'
};

export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { script_text } = req.body;
    
    if (!script_text) {
      return res.status(400).json({ error: 'script_text is required' });
    }

    const apiKey = process.env.GOOGLE_API_KEY;
    if (!apiKey) {
      return res.status(500).json({ error: 'GOOGLE_API_KEY not configured' });
    }

    // Initialize Bedrock client
    const bedrockClient = new BedrockAgentRuntimeClient({
      region: AGENTCORE_CONFIG.region,
      credentials: {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID,
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
      }
    });

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
}

function parseAgentResponse(response) {
  try {
    let responseText = '';
    
    if (response.completion) {
      for (const event of response.completion) {
        if (event.chunk && event.chunk.bytes) {
          responseText += new TextDecoder().decode(event.chunk.bytes);
        }
      }
    }

    const jsonMatch = responseText.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const parsed = JSON.parse(jsonMatch[0]);
      if (parsed.status === 'success') {
        return parsed.response || parsed;
      }
    }

    return createFallbackResponse(responseText);
    
  } catch (error) {
    return createFallbackResponse('Failed to parse response');
  }
}

function createFallbackResponse(text) {
  return {
    project_title: 'FIBO Video Production',
    total_duration_sec: 16,
    checkpoints: [
      {
        checkpoint_id: 1,
        start_time_sec: 0,
        end_time_sec: 8,
        scene_description: 'Opening scene',
        fibo_start_frame: { short_description: 'Scene opening' },
        fibo_end_frame: { short_description: 'Scene transition' }
      },
      {
        checkpoint_id: 2,
        start_time_sec: 8,
        end_time_sec: 16,
        scene_description: 'Closing scene',
        fibo_start_frame: { short_description: 'Scene continuation' },
        fibo_end_frame: { short_description: 'Scene ending' }
      }
    ],
    metadata: { agent_system: 'AgentCore via Vercel', raw_response: text.substring(0, 200) }
  };
}
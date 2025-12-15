import { BedrockAgentRuntimeClient, InvokeAgentCommand } from "@aws-sdk/client-bedrock-agent-runtime";

// AgentCore configuration
const AGENTCORE_CONFIG = {
  agentId: "src_main-PQhMz74UaU",
  agentAliasId: "TSTALIASID",
  region: "us-east-1"
};

/**
 * Direct AgentCore client for frontend
 */
class AgentCoreService {
  constructor() {
    // Initialize Bedrock client with credentials from environment
    this.client = new BedrockAgentRuntimeClient({
      region: AGENTCORE_CONFIG.region,
      credentials: {
        accessKeyId: process.env.REACT_APP_AWS_ACCESS_KEY_ID,
        secretAccessKey: process.env.REACT_APP_AWS_SECRET_ACCESS_KEY,
      }
    });
  }

  /**
   * Process script using AgentCore
   * @param {string} scriptText - Movie script to process
   * @param {string} apiKey - Gemini API key
   * @returns {Promise<Object>} Video production plan
   */
  async processScript(scriptText, apiKey) {
    try {
      const sessionId = `session_${Date.now()}`;
      
      const payload = {
        script_text: scriptText,
        api_key: apiKey
      };

      const command = new InvokeAgentCommand({
        agentId: AGENTCORE_CONFIG.agentId,
        agentAliasId: AGENTCORE_CONFIG.agentAliasId,
        sessionId: sessionId,
        inputText: JSON.stringify(payload)
      });

      console.log("🤖 Calling AgentCore directly...");
      const response = await this.client.send(command);
      
      return this.parseAgentResponse(response);
      
    } catch (error) {
      console.error("AgentCore error:", error);
      throw new Error(`AgentCore processing failed: ${error.message}`);
    }
  }

  /**
   * Parse AgentCore response
   */
  parseAgentResponse(response) {
    try {
      // Handle streaming response
      let responseText = "";
      
      if (response.completion) {
        for (const event of response.completion) {
          if (event.chunk && event.chunk.bytes) {
            responseText += new TextDecoder().decode(event.chunk.bytes);
          }
        }
      }

      // Try to parse JSON response
      const jsonMatch = responseText.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0]);
        if (parsed.status === 'success') {
          return parsed.response || parsed;
        }
      }

      // Fallback: create structured response
      return this.createFallbackResponse(responseText);
      
    } catch (error) {
      console.error("Response parsing error:", error);
      return this.createFallbackResponse("Failed to parse agent response");
    }
  }

  createFallbackResponse(text) {
    return {
      project_title: "FIBO Video Production",
      production_id: `agentcore_${Date.now()}`,
      created_at: new Date().toISOString(),
      total_duration_sec: 16,
      visual_style: {
        lighting_style: "Cinematic three-point lighting",
        color_palette: "Natural, balanced",
        camera_style: "50mm, f/2.8"
      },
      checkpoints: [
        {
          checkpoint_id: 1,
          start_time_sec: 0,
          end_time_sec: 8,
          duration_sec: 8,
          scene_description: "Opening scene",
          fibo_start_frame: { short_description: "Scene opening" },
          fibo_end_frame: { short_description: "Scene transition" }
        },
        {
          checkpoint_id: 2,
          start_time_sec: 8,
          end_time_sec: 16,
          duration_sec: 8,
          scene_description: "Closing scene",
          fibo_start_frame: { short_description: "Scene continuation" },
          fibo_end_frame: { short_description: "Scene ending" }
        }
      ],
      metadata: {
        agent_system: "AgentCore Direct",
        raw_response: text.substring(0, 200)
      }
    };
  }
}

export default new AgentCoreService();
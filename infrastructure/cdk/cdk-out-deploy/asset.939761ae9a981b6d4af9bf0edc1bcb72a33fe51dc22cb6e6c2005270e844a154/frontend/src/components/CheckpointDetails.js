import { useState, useEffect } from 'react';
import { 
  Image, 
  Download, 
  Copy, 
  Loader2, 
  CheckCircle, 
  AlertCircle
} from 'lucide-react';
import toast from 'react-hot-toast';
import { 
  getCheckpointPrompts, 
  generateFrames, 
  getGenerationStatus,
  downloadFile,
  cache
} from '../services/api';
import './CheckpointDetails.css';

function CheckpointDetails({ checkpoint, projectId, onGenerationComplete }) {
  const [prompts, setPrompts] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [generationStatus, setGenerationStatus] = useState(null);
  const [generationId, setGenerationId] = useState(null);

  // Cache key for this checkpoint
  const cacheKey = `generation_${projectId}_${checkpoint.checkpoint_id}`;

  // Reset state and load cached data when checkpoint changes
  useEffect(() => {
    // Reset generation state
    setGenerating(false);
    setGenerationId(null);
    setGenerationStatus(null);
    
    // Try to load cached generation status for this checkpoint
    const cachedStatus = cache.get(cacheKey);
    if (cachedStatus) {
      setGenerationStatus(cachedStatus);
    }
    
    // Load prompts
    loadCheckpointPrompts();
  }, [checkpoint.checkpoint_id, projectId]);

  useEffect(() => {
    let interval;
    if (generationId && generating) {
      interval = setInterval(checkGenerationStatus, 2000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [generationId, generating]);

  const loadCheckpointPrompts = async () => {
    try {
      setLoading(true);
      const data = await getCheckpointPrompts(projectId, checkpoint.checkpoint_id);
      setPrompts(data);
    } catch (error) {
      console.error('Error loading prompts:', error);
      toast.error('Failed to load checkpoint prompts');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateFrames = async () => {
    try {
      setGenerating(true);
      const response = await generateFrames(projectId, checkpoint.checkpoint_id);
      setGenerationId(response.generation_id);
      toast.success('Frame generation started!');
    } catch (error) {
      console.error('Error starting generation:', error);
      toast.error('Failed to start frame generation');
      setGenerating(false);
    }
  };

  const checkGenerationStatus = async () => {
    if (!generationId) return;

    try {
      const status = await getGenerationStatus(generationId);
      setGenerationStatus(status);

      if (status.status === 'completed') {
        setGenerating(false);
        // Cache the completed status for this checkpoint
        cache.set(cacheKey, status, 24 * 60 * 60 * 1000); // 24 hour TTL
        // Notify parent that generation is complete
        if (onGenerationComplete) {
          onGenerationComplete(checkpoint.checkpoint_id, status);
        }
        toast.success('Frame generation completed!');
      } else if (status.status === 'error') {
        setGenerating(false);
        toast.error(`Generation failed: ${status.message}`);
      }
    } catch (error) {
      console.error('Error checking status:', error);
    }
  };

  const copyToClipboard = async (text, label) => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success(`${label} copied to clipboard!`);
    } catch (error) {
      console.error('Failed to copy:', error);
      toast.error('Failed to copy to clipboard');
    }
  };

  const handleDownload = async (url, filename) => {
    try {
      // Check if it's a FAL URL (external) or local API URL
      if (url.startsWith('http://') || url.startsWith('https://')) {
        // External URL - open in new tab or download directly
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.target = '_blank';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        toast.success(`Downloaded ${filename}`);
      } else {
        // Local API URL
        await downloadFile(url, filename);
        toast.success(`Downloaded ${filename}`);
      }
    } catch (error) {
      console.error('Download failed:', error);
      toast.error('Download failed');
    }
  };

  // Check if we have actual images (not just JSON)
  // FAL URLs are from fal.media CDN and don't have extensions
  const isImageUrl = (url) => {
    if (!url) return false;
    // FAL CDN URLs are images
    if (url.includes('fal.media') || url.includes('fal.ai')) return true;
    // Local URLs with image extensions
    if (url.includes('.png') || url.includes('.jpg') || url.includes('.jpeg')) return true;
    // External HTTPS URLs that aren't JSON
    if (url.startsWith('https://') && !url.endsWith('.json')) return true;
    return false;
  };

  const hasStartImage = generationStatus?.start_frame_url && isImageUrl(generationStatus.start_frame_url);
  const hasEndImage = generationStatus?.end_frame_url && isImageUrl(generationStatus.end_frame_url);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="checkpoint-details loading">
        <div className="loading-content">
          <Loader2 className="spin" size={24} />
          <span>Loading checkpoint details...</span>
        </div>
      </div>
    );
  }

  if (!prompts) {
    return (
      <div className="checkpoint-details error">
        <AlertCircle size={24} />
        <span>Failed to load checkpoint details</span>
      </div>
    );
  }

  return (
    <div className="checkpoint-details fade-in">
      <div className="details-header">
        <div className="checkpoint-info">
          <h3>Checkpoint {checkpoint.checkpoint_id}</h3>
          <div className="checkpoint-meta">
            <span className="time-range">
              {formatTime(checkpoint.start_time_sec)} → {formatTime(checkpoint.end_time_sec)}
            </span>
            <span className="duration">{checkpoint.duration_sec}s</span>
          </div>
        </div>
        
        <div className="generation-controls">
          {!generating && !generationStatus?.start_frame_url ? (
            <button 
              className="generate-frames-btn"
              onClick={handleGenerateFrames}
            >
              <Image size={16} />
              Generate Frames
            </button>
          ) : generating ? (
            <div className="generation-progress">
              <Loader2 className="spin" size={16} />
              <span>Generating...</span>
              {generationStatus && (
                <div className="progress-info">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill"
                      style={{ width: `${generationStatus.progress * 100}%` }}
                    />
                  </div>
                  <span className="progress-text">{generationStatus.message}</span>
                </div>
              )}
            </div>
          ) : (
            <div className="generation-complete">
              <CheckCircle size={16} />
              <span>Frames Generated</span>
              {generationStatus?.generation_time_sec !== undefined && (
                <span className="generation-time">
                  ({generationStatus.generation_time_sec.toFixed(1)}s)
                  {(generationStatus.start_frame_cached || generationStatus.end_frame_cached) && (
                    <span className="cache-badge">cached</span>
                  )}
                </span>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="scene-description">
        <h4>Scene Description</h4>
        <p>{prompts.scene_description}</p>
      </div>

      <div className="frames-section">
        <div className="frame-container">
          <div className="frame-header">
            <h4>Start Frame</h4>
            <div className="frame-actions">
              <button
                className="action-btn copy-btn"
                onClick={() => copyToClipboard(
                  JSON.stringify(prompts.fibo_start_frame, null, 2),
                  'Start frame prompt'
                )}
                title="Copy JSON prompt"
              >
                <Copy size={14} />
              </button>
              {generationStatus?.start_frame_url && (
                <button
                  className="action-btn download-btn"
                  onClick={() => handleDownload(
                    generationStatus.start_frame_url,
                    `start_frame_checkpoint_${checkpoint.checkpoint_id}.png`
                  )}
                  title="Download Image"
                >
                  <Download size={14} />
                </button>
              )}
            </div>
          </div>
          
          <div className="frame-content">
            {generating && !hasStartImage ? (
              <div className="generated-frame">
                <div className="frame-placeholder generating">
                  <Loader2 className="spin" size={48} />
                  <span>Generating Start Frame...</span>
                  <small>{generationStatus?.message || 'Please wait...'}</small>
                </div>
              </div>
            ) : hasStartImage ? (
              <div className="generated-frame">
                <img 
                  src={generationStatus.start_frame_url.startsWith('http') 
                    ? generationStatus.start_frame_url 
                    : `http://localhost:8000${generationStatus.start_frame_url}`}
                  alt="Start Frame"
                  className="frame-image"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
                <div className="frame-placeholder error-state" style={{display: 'none'}}>
                  <AlertCircle size={48} />
                  <span>Image loading failed</span>
                </div>
              </div>
            ) : generationStatus?.start_frame_url ? (
              <div className="generated-frame">
                <div className="frame-placeholder completed">
                  <CheckCircle size={48} />
                  <span>Frame Ready</span>
                  <button 
                    className="view-image-btn"
                    onClick={() => window.open(
                      generationStatus.start_frame_url.startsWith('http') 
                        ? generationStatus.start_frame_url 
                        : `http://localhost:8000${generationStatus.start_frame_url}`,
                      '_blank'
                    )}
                  >
                    View Image
                  </button>
                </div>
              </div>
            ) : (
              <div className="frame-prompt">
                <div className="prompt-preview">
                  <strong>Description:</strong>
                  <p>{prompts.fibo_start_frame?.short_description || 'No description'}</p>
                </div>
                <div className="prompt-details">
                  <span><strong>Objects:</strong> {prompts.fibo_start_frame?.objects?.length || 0}</span>
                  <span><strong>Lighting:</strong> {prompts.fibo_start_frame?.lighting || 'N/A'}</span>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="frame-container">
          <div className="frame-header">
            <h4>End Frame</h4>
            <div className="frame-actions">
              <button
                className="action-btn copy-btn"
                onClick={() => copyToClipboard(
                  JSON.stringify(prompts.fibo_end_frame, null, 2),
                  'End frame prompt'
                )}
                title="Copy JSON prompt"
              >
                <Copy size={14} />
              </button>
              {generationStatus?.end_frame_url && (
                <button
                  className="action-btn download-btn"
                  onClick={() => handleDownload(
                    generationStatus.end_frame_url,
                    `end_frame_checkpoint_${checkpoint.checkpoint_id}.png`
                  )}
                  title="Download Image"
                >
                  <Download size={14} />
                </button>
              )}
            </div>
          </div>
          
          <div className="frame-content">
            {generating && !hasEndImage ? (
              <div className="generated-frame">
                <div className="frame-placeholder generating">
                  <Loader2 className="spin" size={48} />
                  <span>Generating End Frame...</span>
                  <small>{generationStatus?.message || 'Please wait...'}</small>
                </div>
              </div>
            ) : hasEndImage ? (
              <div className="generated-frame">
                <img 
                  src={generationStatus.end_frame_url.startsWith('http') 
                    ? generationStatus.end_frame_url 
                    : `http://localhost:8000${generationStatus.end_frame_url}`}
                  alt="End Frame"
                  className="frame-image"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
                <div className="frame-placeholder error-state" style={{display: 'none'}}>
                  <AlertCircle size={48} />
                  <span>Image loading failed</span>
                </div>
              </div>
            ) : generationStatus?.end_frame_url ? (
              <div className="generated-frame">
                <div className="frame-placeholder completed">
                  <CheckCircle size={48} />
                  <span>Frame Ready</span>
                  <button 
                    className="view-image-btn"
                    onClick={() => window.open(
                      generationStatus.end_frame_url.startsWith('http') 
                        ? generationStatus.end_frame_url 
                        : `http://localhost:8000${generationStatus.end_frame_url}`,
                      '_blank'
                    )}
                  >
                    View Image
                  </button>
                </div>
              </div>
            ) : (
              <div className="frame-prompt">
                <div className="prompt-preview">
                  <strong>Description:</strong>
                  <p>{prompts.fibo_end_frame?.short_description || 'No description'}</p>
                </div>
                <div className="prompt-details">
                  <span><strong>Objects:</strong> {prompts.fibo_end_frame?.objects?.length || 0}</span>
                  <span><strong>Lighting:</strong> {prompts.fibo_end_frame?.lighting || 'N/A'}</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="video-generation-section">
        <div className="section-header">
          <h4>Video Generation Prompt</h4>
          <button
            className="action-btn copy-btn"
            onClick={() => copyToClipboard(
              prompts.video_generation_notes,
              'Video generation prompt'
            )}
            title="Copy video prompt"
          >
            <Copy size={14} />
            Copy Prompt
          </button>
        </div>
        <div className="video-prompt">
          <p>{prompts.video_generation_notes}</p>
        </div>
      </div>

      <div className="visual-style-section">
        <h4>Visual Style Consistency</h4>
        <div className="style-grid">
          <div className="style-item">
            <strong>Lighting:</strong>
            <span>{prompts.visual_style?.lighting_style}</span>
          </div>
          <div className="style-item">
            <strong>Color Palette:</strong>
            <span>{prompts.visual_style?.color_palette}</span>
          </div>
          <div className="style-item">
            <strong>Camera Style:</strong>
            <span>{prompts.visual_style?.camera_style}</span>
          </div>
          <div className="style-item">
            <strong>Environment:</strong>
            <span>{prompts.visual_style?.environment_theme}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CheckpointDetails;
import React from 'react';
import { Clock, Play, ChevronRight, CheckCircle } from 'lucide-react';
import './VideoTimeline.css';

function VideoTimeline({ videoPlan, selectedCheckpoint, onCheckpointSelect, generatedCheckpoints = {} }) {
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getCheckpointName = (checkpoint) => {
    // Extract a short name from the scene description
    const description = checkpoint.scene_description || '';
    const words = description.split(' ').slice(0, 4).join(' ');
    return words.length > 30 ? words.substring(0, 30) + '...' : words;
  };

  return (
    <div className="video-timeline">
      <div className="timeline-header">
        <div className="header-info">
          <Clock size={20} />
          <h3>Video Timeline</h3>
        </div>
        <div className="visual-style-info">
          <span className="style-label">Style:</span>
          <span className="style-value">
            {videoPlan.visual_style?.artistic_direction || 'Cinematic'}
          </span>
        </div>
      </div>

      <div className="timeline-container">
        <div className="timeline-track">
          {videoPlan.checkpoints.map((checkpoint, index) => {
            const isSelected = selectedCheckpoint?.checkpoint_id === checkpoint.checkpoint_id;
            const isGenerated = generatedCheckpoints[checkpoint.checkpoint_id];
            const progress = ((checkpoint.end_time_sec / videoPlan.total_duration_sec) * 100);
            
            return (
              <div
                key={checkpoint.checkpoint_id}
                className={`checkpoint ${isSelected ? 'selected' : ''} ${isGenerated ? 'generated' : ''}`}
                style={{ left: `${(checkpoint.start_time_sec / videoPlan.total_duration_sec) * 100}%` }}
                onClick={() => onCheckpointSelect(checkpoint)}
              >
                <div className="checkpoint-dot">
                  {isGenerated ? (
                    <CheckCircle size={14} className="generated-icon" />
                  ) : (
                    <span className="checkpoint-number">{checkpoint.checkpoint_id}</span>
                  )}
                </div>
                <div className="checkpoint-info">
                  <div className="checkpoint-time">
                    {formatTime(checkpoint.start_time_sec)} - {formatTime(checkpoint.end_time_sec)}
                  </div>
                  <div className="checkpoint-name">
                    {getCheckpointName(checkpoint)}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="timeline-ruler">
          {Array.from({ length: Math.ceil(videoPlan.total_duration_sec / 10) + 1 }, (_, i) => (
            <div
              key={i}
              className="ruler-mark"
              style={{ left: `${(i * 10 / videoPlan.total_duration_sec) * 100}%` }}
            >
              <span className="ruler-time">{formatTime(i * 10)}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="checkpoints-list">
        <h4>Checkpoints Overview</h4>
        <div className="checkpoints-grid">
          {videoPlan.checkpoints.map((checkpoint) => {
            const isSelected = selectedCheckpoint?.checkpoint_id === checkpoint.checkpoint_id;
            const isGenerated = generatedCheckpoints[checkpoint.checkpoint_id];
            
            return (
              <div
                key={checkpoint.checkpoint_id}
                className={`checkpoint-card ${isSelected ? 'selected' : ''} ${isGenerated ? 'generated' : ''}`}
                onClick={() => onCheckpointSelect(checkpoint)}
              >
                <div className="card-header">
                  <div className="checkpoint-badge">
                    {isGenerated ? (
                      <CheckCircle size={12} className="generated-icon" />
                    ) : (
                      <Play size={12} />
                    )}
                    Checkpoint {checkpoint.checkpoint_id}
                  </div>
                  <div className="checkpoint-duration">
                    {checkpoint.duration_sec}s
                    {isGenerated && <span className="generated-badge">✓</span>}
                  </div>
                </div>
                
                <div className="card-content">
                  <h5 className="checkpoint-title">
                    {getCheckpointName(checkpoint)}
                  </h5>
                  <p className="checkpoint-description">
                    {checkpoint.scene_description}
                  </p>
                  <div className="checkpoint-time-range">
                    {formatTime(checkpoint.start_time_sec)} → {formatTime(checkpoint.end_time_sec)}
                  </div>
                </div>

                <div className="card-footer">
                  <span className="select-hint">
                    {isGenerated ? 'Frames generated' : 'Click to expand'} <ChevronRight size={14} />
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default VideoTimeline;
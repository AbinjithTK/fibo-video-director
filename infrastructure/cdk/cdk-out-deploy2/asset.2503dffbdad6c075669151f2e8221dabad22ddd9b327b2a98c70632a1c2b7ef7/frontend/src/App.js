import React, { useState, useCallback, useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import ScriptInput from './components/ScriptInput';
import VideoTimeline from './components/VideoTimeline';
import CheckpointDetails from './components/CheckpointDetails';
import { Film, Sparkles } from 'lucide-react';
import { cache } from './services/api';
import './App.css';

function App() {
  const [videoPlan, setVideoPlan] = useState(null);
  const [selectedCheckpoint, setSelectedCheckpoint] = useState(null);
  const [loading, setLoading] = useState(false);
  const [generatedCheckpoints, setGeneratedCheckpoints] = useState({});

  // Load cached generation states when video plan changes
  useEffect(() => {
    if (videoPlan?.project_id && videoPlan?.checkpoints) {
      const cached = {};
      videoPlan.checkpoints.forEach(cp => {
        const cacheKey = `generation_${videoPlan.project_id}_${cp.checkpoint_id}`;
        const status = cache.get(cacheKey);
        if (status?.status === 'completed') {
          cached[cp.checkpoint_id] = status;
        }
      });
      setGeneratedCheckpoints(cached);
    }
  }, [videoPlan?.project_id]);

  const handlePlanGenerated = useCallback((plan) => {
    setVideoPlan(plan);
    setSelectedCheckpoint(null);
    setGeneratedCheckpoints({});
  }, []);

  const handleCheckpointSelect = useCallback((checkpoint) => {
    setSelectedCheckpoint(checkpoint);
  }, []);

  const handleGenerationComplete = useCallback((checkpointId, status) => {
    setGeneratedCheckpoints(prev => ({
      ...prev,
      [checkpointId]: status
    }));
  }, []);

  return (
    <div className="app">
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#1a1a2e',
            color: '#ffffff',
            border: '1px solid #4a5568',
          },
        }}
      />
      
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <Film className="logo-icon" />
            <h1>FIBO Video Director</h1>
            <Sparkles className="sparkle-icon" />
          </div>
          <p className="subtitle">
            Transform movie scripts into AI-generated video sequences with FIBO
          </p>
        </div>
      </header>

      <main className="app-main">
        <div className="container">
          {!videoPlan ? (
            <div className="script-section fade-in">
              <ScriptInput 
                onPlanGenerated={handlePlanGenerated}
                loading={loading}
                setLoading={setLoading}
              />
            </div>
          ) : (
            <div className="video-production fade-in">
              <div className="production-header">
                <h2>{videoPlan.project_title}</h2>
                <div className="production-stats">
                  <span className="stat">
                    <strong>{videoPlan.total_duration_sec}s</strong> total duration
                  </span>
                  <span className="stat">
                    <strong>{videoPlan.checkpoints.length}</strong> checkpoints
                  </span>
                  <button 
                    className="new-project-btn"
                    onClick={() => {
                      setVideoPlan(null);
                      setSelectedCheckpoint(null);
                    }}
                  >
                    New Project
                  </button>
                </div>
              </div>

              <div className="production-content">
                <div className="timeline-section">
                  <VideoTimeline 
                    videoPlan={videoPlan}
                    selectedCheckpoint={selectedCheckpoint}
                    onCheckpointSelect={handleCheckpointSelect}
                    generatedCheckpoints={generatedCheckpoints}
                  />
                </div>

                {selectedCheckpoint && (
                  <div className="checkpoint-section">
                    <CheckpointDetails 
                      key={selectedCheckpoint.checkpoint_id}
                      checkpoint={selectedCheckpoint}
                      projectId={videoPlan.project_id}
                      onGenerationComplete={handleGenerationComplete}
                    />
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>Powered by FIBO AI • Built with React</p>
      </footer>
    </div>
  );
}

export default App;
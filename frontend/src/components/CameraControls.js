import React, { useState, useEffect } from 'react';
import './CameraControls.css';

const CameraControls = ({ onCameraChange, initialSettings = {} }) => {
  const [cameraSettings, setCameraSettings] = useState({
    camera: 'ARRI Alexa',
    lens: '50mm',
    focalLength: 50,
    aperture: 2.8,
    angle: 'Eye-level',
    movement: 'Static',
    frameRate: 24,
    resolution: '4K',
    ...initialSettings
  });

  // Camera options
  const cameraOptions = [
    'ARRI Alexa', 'RED Dragon', 'Canon C300', 'Sony FX9', 
    'Blackmagic URSA', 'Panasonic EVA1', 'Film Camera'
  ];

  const lensOptions = [
    '14mm', '24mm', '35mm', '50mm', '85mm', '135mm', '200mm'
  ];

  const angleOptions = [
    'Bird\'s Eye', 'High Angle', 'Eye-level', 'Low Angle', 
    'Worm\'s Eye', 'Dutch Angle', 'Over Shoulder'
  ];

  const movementOptions = [
    'Static', 'Pan Left', 'Pan Right', 'Tilt Up', 'Tilt Down',
    'Dolly In', 'Dolly Out', 'Tracking Shot', 'Handheld'
  ];

  const resolutionOptions = ['HD', '2K', '4K', '6K', '8K'];

  useEffect(() => {
    onCameraChange(cameraSettings);
  }, [cameraSettings, onCameraChange]);

  const handleSliderChange = (key, value) => {
    setCameraSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleSelectChange = (key, value) => {
    setCameraSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  return (
    <div className="camera-controls">
      <div className="camera-controls-header">
        <h3>🎥 Cinema Camera Controls</h3>
        <p>Adjust professional camera settings for cinematic FIBO prompts</p>
      </div>

      <div className="controls-grid">
        {/* Camera Selection */}
        <div className="control-group">
          <label>Camera Body</label>
          <select 
            value={cameraSettings.camera}
            onChange={(e) => handleSelectChange('camera', e.target.value)}
            className="camera-select"
          >
            {cameraOptions.map(camera => (
              <option key={camera} value={camera}>{camera}</option>
            ))}
          </select>
        </div>

        {/* Lens Selection */}
        <div className="control-group">
          <label>Lens</label>
          <select 
            value={cameraSettings.lens}
            onChange={(e) => handleSelectChange('lens', e.target.value)}
            className="camera-select"
          >
            {lensOptions.map(lens => (
              <option key={lens} value={lens}>{lens}</option>
            ))}
          </select>
        </div>

        {/* Focal Length Slider */}
        <div className="control-group">
          <label>Focal Length: {cameraSettings.focalLength}mm</label>
          <input
            type="range"
            min="14"
            max="200"
            value={cameraSettings.focalLength}
            onChange={(e) => handleSliderChange('focalLength', parseInt(e.target.value))}
            className="camera-slider"
          />
          <div className="slider-labels">
            <span>Wide (14mm)</span>
            <span>Telephoto (200mm)</span>
          </div>
        </div>

        {/* Aperture Slider */}
        <div className="control-group">
          <label>Aperture: f/{cameraSettings.aperture}</label>
          <input
            type="range"
            min="1.4"
            max="16"
            step="0.1"
            value={cameraSettings.aperture}
            onChange={(e) => handleSliderChange('aperture', parseFloat(e.target.value))}
            className="camera-slider"
          />
          <div className="slider-labels">
            <span>Shallow DOF (f/1.4)</span>
            <span>Deep DOF (f/16)</span>
          </div>
        </div>

        {/* Camera Angle */}
        <div className="control-group">
          <label>Camera Angle</label>
          <select 
            value={cameraSettings.angle}
            onChange={(e) => handleSelectChange('angle', e.target.value)}
            className="camera-select"
          >
            {angleOptions.map(angle => (
              <option key={angle} value={angle}>{angle}</option>
            ))}
          </select>
        </div>

        {/* Camera Movement */}
        <div className="control-group">
          <label>Camera Movement</label>
          <select 
            value={cameraSettings.movement}
            onChange={(e) => handleSelectChange('movement', e.target.value)}
            className="camera-select"
          >
            {movementOptions.map(movement => (
              <option key={movement} value={movement}>{movement}</option>
            ))}
          </select>
        </div>

        {/* Frame Rate Slider */}
        <div className="control-group">
          <label>Frame Rate: {cameraSettings.frameRate}fps</label>
          <input
            type="range"
            min="23.976"
            max="120"
            step="0.001"
            value={cameraSettings.frameRate}
            onChange={(e) => handleSliderChange('frameRate', parseFloat(e.target.value))}
            className="camera-slider"
          />
          <div className="slider-labels">
            <span>Cinema (24fps)</span>
            <span>Slow Motion (120fps)</span>
          </div>
        </div>

        {/* Resolution */}
        <div className="control-group">
          <label>Resolution</label>
          <select 
            value={cameraSettings.resolution}
            onChange={(e) => handleSelectChange('resolution', e.target.value)}
            className="camera-select"
          >
            {resolutionOptions.map(res => (
              <option key={res} value={res}>{res}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Camera Settings Preview */}
      <div className="camera-preview">
        <h4>📋 Current Camera Setup</h4>
        <div className="preview-text">
          <strong>{cameraSettings.camera}</strong> with <strong>{cameraSettings.lens}</strong> lens, 
          f/<strong>{cameraSettings.aperture}</strong> aperture, <strong>{cameraSettings.angle}</strong> angle, 
          <strong>{cameraSettings.movement}</strong> movement, <strong>{cameraSettings.frameRate}fps</strong> at <strong>{cameraSettings.resolution}</strong>
        </div>
      </div>

      {/* Professional Presets */}
      <div className="camera-presets">
        <h4>🎬 Professional Presets</h4>
        <div className="preset-buttons">
          <button 
            onClick={() => setCameraSettings({
              ...cameraSettings,
              camera: 'ARRI Alexa',
              lens: '50mm',
              focalLength: 50,
              aperture: 2.8,
              angle: 'Eye-level',
              movement: 'Static',
              frameRate: 24,
              resolution: '4K'
            })}
            className="preset-btn"
          >
            🎭 Drama
          </button>
          <button 
            onClick={() => setCameraSettings({
              ...cameraSettings,
              camera: 'RED Dragon',
              lens: '24mm',
              focalLength: 24,
              aperture: 4.0,
              angle: 'Low Angle',
              movement: 'Handheld',
              frameRate: 24,
              resolution: '6K'
            })}
            className="preset-btn"
          >
            🚀 Action
          </button>
          <button 
            onClick={() => setCameraSettings({
              ...cameraSettings,
              camera: 'Canon C300',
              lens: '85mm',
              focalLength: 85,
              aperture: 1.8,
              angle: 'Eye-level',
              movement: 'Dolly In',
              frameRate: 24,
              resolution: '4K'
            })}
            className="preset-btn"
          >
            💕 Romance
          </button>
          <button 
            onClick={() => setCameraSettings({
              ...cameraSettings,
              camera: 'Blackmagic URSA',
              lens: '14mm',
              focalLength: 14,
              aperture: 8.0,
              angle: 'High Angle',
              movement: 'Pan Right',
              frameRate: 24,
              resolution: '4K'
            })}
            className="preset-btn"
          >
            🌄 Landscape
          </button>
        </div>
      </div>
    </div>
  );
};

export default CameraControls;
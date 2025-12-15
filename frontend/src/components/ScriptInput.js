import React, { useState } from 'react';
import { FileText, Wand2, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { generateVideoPlan } from '../services/api';
import './ScriptInput.css';

const SAMPLE_SCRIPTS = {
  cyberpunk: `FADE IN:

EXT. CYBERPUNK CITY - NIGHT

Rain falls on neon-lit streets. Holographic advertisements flicker on towering buildings.

JACK (30s, cybernetic arm, leather jacket) walks through the crowded street, dodging flying cars overhead. His augmented reality display shows incoming messages.

JACK
(to his AI assistant)
Show me the route to the data center.

A holographic path appears in his vision, leading through dark alleys.

Jack turns into a narrow alley where ZARA (20s, punk hacker, glowing tattoos) waits by a hidden door.

ZARA
You're late. The security window closes in five minutes.

JACK
Traffic was hell. Flying cars everywhere.

Zara activates a device that makes the door shimmer and become transparent.

ZARA
After you, corporate spy.

Jack smirks and steps through the shimmering portal.

FADE OUT.`,

  space: `FADE IN:

INT. SPACESHIP BRIDGE - DAY

Warning lights flash red. Alarms blare. The ship shudders violently.

CAPTAIN SARAH (40s, uniform torn, blood on forehead) grips her command chair as the ship rocks.

SARAH
(shouting over alarms)
Damage report!

ENGINEER TORRES (30s, panicked) frantically works at his console.

TORRES
Hull breach on deck seven! We're losing atmosphere fast!

Sarah's eyes widen as she sees something on the main viewscreen - a massive alien vessel approaching.

SARAH
(whispered)
My God... what is that thing?

The alien ship fires. A brilliant beam of energy streaks toward them.

SARAH
(screaming)
Brace for impact!

FADE OUT.`,

  fantasy: `FADE IN:

EXT. ENCHANTED FOREST - DAY

Sunlight filters through ancient trees. ELENA (25, ranger, bow) tracks mysterious footprints.

ELENA
(to herself)
These tracks... they're not human.

A rustling in the bushes. She draws her bow, arrow nocked.

A DRAGON HATCHLING (small, iridescent scales) emerges, injured and afraid.

ELENA
(softening)
Hey there, little one. I won't hurt you.

She slowly approaches, hand extended. The hatchling sniffs cautiously.

ELENA
Where's your mother?

A thunderous ROAR echoes through the forest. Both Elena and the hatchling look up in alarm.

FADE OUT.`
};

function ScriptInput({ onPlanGenerated, loading, setLoading }) {
  const [scriptText, setScriptText] = useState('');
  const [showSamples, setShowSamples] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!scriptText.trim()) {
      toast.error('Please enter a movie script');
      return;
    }

    setLoading(true);
    
    try {
      console.log('Sending script to backend...');
      const plan = await generateVideoPlan(scriptText);
      console.log('Received plan:', plan);
      
      if (plan && plan.checkpoints && plan.checkpoints.length > 0) {
        toast.success('Video plan generated successfully!');
        onPlanGenerated(plan);
      } else {
        console.error('Invalid plan structure:', plan);
        toast.error('Invalid response from server. Check console for details.');
      }
    } catch (error) {
      console.error('Error generating plan:', error);
      toast.error(`Failed: ${error.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const loadSample = (sampleKey) => {
    setScriptText(SAMPLE_SCRIPTS[sampleKey]);
    setShowSamples(false);
    toast.success(`Loaded ${sampleKey} sample script`);
  };

  return (
    <div className="script-input">
      <div className="script-header">
        <div className="header-icon">
          <FileText size={32} />
        </div>
        <h2>Movie Script Input</h2>
        <p>Enter your movie script to generate a FIBO video production plan</p>
      </div>

      <form onSubmit={handleSubmit} className="script-form">
        <div className="form-group">
          <label htmlFor="script">Movie Script</label>
          <textarea
            id="script"
            value={scriptText}
            onChange={(e) => setScriptText(e.target.value)}
            placeholder="FADE IN:

EXT. LOCATION - TIME

Your movie script here...

FADE OUT."
            rows={15}
            className="script-textarea"
            disabled={loading}
          />
          <div className="textarea-footer">
            <span className="char-count">
              {scriptText.length} characters
            </span>
            <button
              type="button"
              className="samples-btn"
              onClick={() => setShowSamples(!showSamples)}
              disabled={loading}
            >
              Load Sample
            </button>
          </div>
        </div>

        {showSamples && (
          <div className="samples-panel fade-in">
            <h3>Sample Scripts</h3>
            <div className="samples-grid">
              <button
                type="button"
                className="sample-btn"
                onClick={() => loadSample('cyberpunk')}
              >
                <strong>Cyberpunk Heist</strong>
                <span>Neon-lit city, hacker infiltration</span>
              </button>
              <button
                type="button"
                className="sample-btn"
                onClick={() => loadSample('space')}
              >
                <strong>Space Adventure</strong>
                <span>Spaceship under alien attack</span>
              </button>
              <button
                type="button"
                className="sample-btn"
                onClick={() => loadSample('fantasy')}
              >
                <strong>Fantasy Quest</strong>
                <span>Enchanted forest, dragon encounter</span>
              </button>
            </div>
          </div>
        )}

        <button
          type="submit"
          className="generate-btn"
          disabled={loading || !scriptText.trim()}
        >
          {loading ? (
            <>
              <Loader2 className="spin" size={20} />
              Generating Plan...
            </>
          ) : (
            <>
              <Wand2 size={20} />
              Generate Video Plan
            </>
          )}
        </button>
      </form>
    </div>
  );
}

export default ScriptInput;
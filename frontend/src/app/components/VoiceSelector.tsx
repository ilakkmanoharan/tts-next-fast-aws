"use client";

import React from "react";

interface VoiceSelectorProps {
  voices: string[];
  selectedVoice: string;
  onSelect: (voice: string) => void;
}

export default function VoiceSelector({ voices, selectedVoice, onSelect }: VoiceSelectorProps) {
  return (
    <div className="voice-selector">
      <label>Select Voice:</label>
      <select
        value={selectedVoice}
        onChange={(e) => onSelect(e.target.value)}
      >
        <option value="">-- Choose a voice --</option>
        {voices.map((voice) => (
          <option key={voice} value={voice}>
            {voice}
          </option>
        ))}
      </select>
    </div>
  );
}

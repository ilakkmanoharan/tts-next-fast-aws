"use client";

import { useState, useEffect, useRef } from "react";

export default function Home() {
  const [text, setText] = useState("");
  const [selectedVoice, setSelectedVoice] = useState("");
  const [selectedEngine, setSelectedEngine] = useState("neural");
  const [voices, setVoices] = useState<{ id: string; name: string; engines: string[] }[]>([]);
  const [audioUrl, setAudioUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const audioRef = useRef<HTMLAudioElement>(null);

  // Fetch voices dynamically from backend
  useEffect(() => {
    const fetchVoices = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/voices`);
        if (!res.ok) throw new Error("Failed to fetch voices");
        const data = await res.json();
        setVoices(data.voices);
        if (data.voices.length > 0) {
          setSelectedVoice(data.voices[0].id);
          setSelectedEngine(data.voices[0].engines.includes("neural") ? "neural" : data.voices[0].engines[0]);
        }
      } catch (err) {
        console.error(err);
        setError("Failed to load available voices");
      }
    };
    fetchVoices();
  }, []);

  const generateAudio = async () => {
    if (!text.trim()) {
      setError("Please enter some text");
      return;
    }
    if (!selectedVoice) {
      setError("Please select a voice");
      return;
    }
    setError("");
    setLoading(true);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/generate-audio`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, voice: selectedVoice, engine: selectedEngine }),
      });

      if (!res.ok) throw new Error("Failed to generate audio");

      const data = await res.json();
      setAudioUrl(data.url);

      if (audioRef.current) {
        audioRef.current.src = data.url;
        audioRef.current.play();
      }
    } catch (err: unknown) {
      let message = "Something went wrong";
      if (err instanceof Error) message = err.message;
      console.error(err);
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  // Update engine when voice changes
  const handleVoiceChange = (voiceId: string) => {
    setSelectedVoice(voiceId);
    const voice = voices.find((v) => v.id === voiceId);
    if (voice) {
      setSelectedEngine(voice.engines.includes("neural") ? "neural" : voice.engines[0]);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.heading}>Text-to-Speech Generator</h1>

        <textarea
          placeholder="Type your text here..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          style={styles.textarea}
        />

        <div style={styles.controls}>
          <label style={styles.label}>Select Voice:</label>
          <select
            value={selectedVoice}
            onChange={(e) => handleVoiceChange(e.target.value)}
            style={styles.select}
          >
            {voices.map((v) => (
              <option key={v.id} value={v.id}>
                {v.name} ({v.engines.join(", ")})
              </option>
            ))}
          </select>
        </div>

        <div style={styles.controls}>
          <label style={styles.label}>Select Engine:</label>
          <select
            value={selectedEngine}
            onChange={(e) => setSelectedEngine(e.target.value)}
            style={styles.select}
          >
            {voices.find((v) => v.id === selectedVoice)?.engines.map((engine) => (
              <option key={engine} value={engine}>
                {engine}
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={generateAudio}
          disabled={loading}
          style={styles.button}
        >
          {loading ? "Generating..." : "Generate Audio"}
        </button>

        {error && <p style={styles.error}>{error}</p>}

        {audioUrl && (
          <div style={{ marginTop: "20px" }}>
            <audio ref={audioRef} controls src={audioUrl} style={{ width: "100%" }} />
          </div>
        )}
      </div>
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    minHeight: "100vh",
    background: "linear-gradient(to right, #8360c3, #2ebf91)",
  },
  card: {
    background: "white",
    padding: "40px",
    borderRadius: "16px",
    width: "90%",
    maxWidth: "600px",
    textAlign: "center",
    boxShadow: "0 8px 20px rgba(0,0,0,0.15)",
  },
  heading: {
    fontSize: "28px",
    fontWeight: "bold",
    marginBottom: "20px",
  },
  textarea: {
    width: "100%",
    height: "150px",
    padding: "10px",
    fontSize: "16px",
    borderRadius: "8px",
    border: "1px solid #ccc",
    resize: "vertical",
    marginBottom: "15px",
  },
  controls: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    gap: "10px",
    marginBottom: "15px",
  },
  label: {
    fontSize: "16px",
    fontWeight: "500",
  },
  select: {
    padding: "6px 10px",
    fontSize: "16px",
    borderRadius: "6px",
    border: "1px solid #ccc",
  },
  button: {
    padding: "10px 20px",
    fontSize: "16px",
    fontWeight: "bold",
    color: "#fff",
    background: "linear-gradient(to right, #ff416c, #ff4b2b)",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
  },
  error: {
    color: "red",
    marginTop: "10px",
  },
};


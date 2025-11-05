# Voice Interface Implementation Plan

## Overview
This document outlines where and how to implement voice interface functionality in the application, replacing the "Audio Overview" feature with an interactive "Voice Interface".

---

## ✅ Changes Made

### 1. **StudioGrid.tsx** - Updated Labels
- Changed "Audio Overview" → "Voice Interface"
- Updated tooltip: "Voice Interface - Coming soon"
- Updated description: "Voice Interface - Interact in:"
- Updated instructions text

---

## 🎯 Places to Add Voice Interface Functionality

### **1. Frontend - Voice Input Component**

#### Location: `frontend/components/VoiceInput.tsx` (NEW FILE)
**Purpose:** Capture user voice input and convert to text

**Features to implement:**
```tsx
- Speech-to-Text (STT) using Web Speech API or external service
- Microphone button with recording indicator
- Real-time transcription display
- Language selection support (matching the UI languages)
- Error handling for microphone permissions
```

**Integration points:**
- Add to Query tool in Chat panel
- Add to Notes chat interface in Studio panel
- Optional: Add floating voice button for global access

---

### **2. Frontend - Voice Output Component**

#### Location: `frontend/components/VoiceOutput.tsx` (NEW FILE)
**Purpose:** Convert text responses to speech

**Features to implement:**
```tsx
- Text-to-Speech (TTS) using Web Speech API or external service
- Play/Pause/Stop controls
- Voice selection (male/female, different accents)
- Speed control (0.5x to 2x)
- Multi-language support
```

**Integration points:**
- Add to query responses in Chat panel
- Add to all Studio tool outputs (Summarize, FAQ, etc.)
- Add "Listen" button next to each response

---

### **3. Frontend - Chat Panel Enhancement**

#### Location: `frontend/app/page.tsx`
**Current Query Input:** Text-only input field

**Add voice features:**
```tsx
// In handleQuery function
const handleVoiceQuery = async (audioBlob: Blob) => {
  // 1. Convert speech to text (STT)
  const transcription = await speechToText(audioBlob);
  
  // 2. Set query text
  setQueryText(transcription);
  
  // 3. Execute query
  await handleQuery();
  
  // 4. Convert response to speech (TTS)
  if (enableVoiceResponse) {
    await textToSpeech(toolResults.answer);
  }
};
```

**UI additions:**
- Microphone icon button next to query input
- Voice recording indicator (waveform animation)
- "Listen to response" toggle option

---

### **4. Backend - Voice API Endpoints**

#### Location: `src/server.py` or new `src/voiceServer.py`

**New endpoints to create:**

#### A. Speech-to-Text Endpoint
```python
@app.post("/api/stt")
async def speech_to_text(audio: UploadFile):
    """
    Convert audio to text
    Input: Audio file (WAV, MP3, OGG)
    Output: { "text": "transcribed text", "language": "en" }
    """
    # Use OpenAI Whisper, Google Speech-to-Text, or similar
    pass
```

#### B. Text-to-Speech Endpoint
```python
@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech
    Input: { "text": "...", "language": "en", "voice": "male" }
    Output: Audio stream or file URL
    """
    # Use Google TTS, Amazon Polly, or similar
    pass
```

#### C. Voice Query Endpoint (Combined)
```python
@app.post("/api/voice-query")
async def voice_query(audio: UploadFile, top_k: int = 5):
    """
    End-to-end voice query: STT → Query → TTS
    Input: Audio file
    Output: { "answer": "...", "audio_url": "...", "context": [...] }
    """
    # 1. Transcribe audio
    # 2. Query knowledge base
    # 3. Generate speech response
    pass
```

---

### **5. Frontend API Library**

#### Location: `frontend/lib/api.ts`

**Add new functions:**

```typescript
// Speech-to-Text
export async function speechToText(audioBlob: Blob): Promise<string> {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.webm');
  
  const response = await fetch(`${API_BASE_URL}/api/stt`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) throw new Error('STT failed');
  const data = await response.json();
  return data.text;
}

// Text-to-Speech
export async function textToSpeech(
  text: string, 
  language: string = 'en',
  voice: string = 'default'
): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/api/tts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, language, voice }),
  });
  
  if (!response.ok) throw new Error('TTS failed');
  const data = await response.json();
  return data.audio_url; // or return blob
}

// Voice Query (combined)
export async function voiceQuery(
  audioBlob: Blob,
  topK: number = 5
): Promise<VoiceQueryResponse> {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'query.webm');
  formData.append('top_k', topK.toString());
  
  const response = await fetch(`${API_BASE_URL}/api/voice-query`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) throw new Error('Voice query failed');
  return await response.json();
}
```

---

### **6. Studio Panel - Voice Interface Section**

#### Location: `frontend/components/StudioGrid.tsx`

**Current state:** Disabled language selector with "Coming soon"

**Make it functional:**

```tsx
// Remove cursor-not-allowed and opacity-50
// Add onClick handler
<div 
  className="border border-emerald-600/30 rounded-lg p-4 bg-emerald-900/10 cursor-pointer hover:bg-emerald-900/20 transition-colors"
  onClick={() => setShowVoiceInterface(true)}
>
  <p className="text-sm text-gray-300 mb-3">Voice Interface - Interact in:</p>
  <div className="flex flex-wrap gap-2">
    {languages.map((lang) => (
      <button
        key={lang.code}
        onClick={(e) => {
          e.stopPropagation();
          setSelectedLanguage(lang.code);
        }}
        className={`text-xs px-2 py-1 rounded ${
          selectedLanguage === lang.code 
            ? 'bg-emerald-600 text-white' 
            : 'text-gray-400 hover:text-gray-200'
        }`}
      >
        {lang.name}
      </button>
    ))}
  </div>
  <p className="text-xs text-emerald-500 mt-2">Click to start voice interaction</p>
</div>
```

---

### **7. Notes Section - Voice Note Support**

#### Location: `frontend/components/StudioGrid.tsx` (Notes tab)

**Add voice note recording:**

```tsx
// In the chat input section
<div className="flex items-end gap-2">
  <button
    onClick={isRecording ? stopRecording : startRecording}
    className={`shrink-0 p-2.5 rounded-lg transition-colors ${
      isRecording 
        ? 'bg-red-600 hover:bg-red-700 text-white animate-pulse' 
        : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
    }`}
    title={isRecording ? "Stop recording" : "Record voice note"}
  >
    <FiMic className="w-4 h-4" />
  </button>
  
  <textarea
    ref={inputRef}
    value={newNote}
    onChange={handleTextareaChange}
    onKeyDown={handleKeyDown}
    placeholder="Type a note or record voice... (Enter to send)"
    className="flex-1 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg..."
    rows={1}
  />
  
  <button
    onClick={handleAddNote}
    disabled={!newNote.trim()}
    className="shrink-0 p-2.5 bg-emerald-600..."
  >
    <FiSend className="w-4 h-4" />
  </button>
</div>

{/* Recording indicator */}
{isRecording && (
  <div className="flex items-center gap-2 text-red-400 text-xs mt-2">
    <span className="animate-pulse">●</span>
    Recording... {recordingTime}s
  </div>
)}
```

---

## 📦 Required Dependencies

### Frontend (package.json)
```json
{
  "dependencies": {
    "wavesurfer.js": "^7.0.0",  // For audio waveform visualization
    "recordrtc": "^5.6.2",       // For audio recording
    "react-use-audio-player": "^2.0.0"  // For audio playback
  }
}
```

### Backend (requirements.txt)
```txt
openai-whisper==20231117  # For STT (or use OpenAI API)
gtts==2.4.0               # For TTS (basic, or use better services)
pydub==0.25.1             # For audio processing
soundfile==0.12.1         # For audio file handling
```

**Better alternatives for production:**
- **STT:** OpenAI Whisper API, Google Speech-to-Text, Azure Speech
- **TTS:** Google Cloud TTS, Amazon Polly, ElevenLabs

---

## 🎨 UI/UX Considerations

### 1. **Microphone Permission Handling**
- Request permission on first use
- Show clear error messages if denied
- Provide instructions to enable in browser settings

### 2. **Visual Feedback**
- Animated microphone icon when recording
- Waveform visualization during recording
- Loading indicator during transcription
- Audio player controls for playback

### 3. **Language Support**
- Match the 9 Indian languages shown in UI
- Auto-detect input language
- Allow language switching
- Preserve language preference

### 4. **Accessibility**
- Keyboard shortcuts (e.g., Alt+V to toggle voice)
- Screen reader announcements
- High contrast mode support
- Clear labels for all buttons

---

## 🚀 Implementation Priority

### Phase 1: Basic Voice Input (Query Tool)
1. Add microphone button to query input
2. Implement browser Web Speech API (STT)
3. Display transcription before sending query
4. Test with English only

### Phase 2: Voice Output
1. Add "Listen" button to query responses
2. Implement browser Speech Synthesis API (TTS)
3. Add playback controls
4. Test with English only

### Phase 3: Multi-language Support
1. Add language selector
2. Integrate with better STT/TTS services
3. Test with all supported languages
4. Handle language-specific quirks

### Phase 4: Voice Notes
1. Add voice recording to Notes tab
2. Store audio files or transcriptions
3. Add playback for voice notes
4. Implement voice note search

### Phase 5: Advanced Features
1. Continuous conversation mode
2. Voice commands ("summarize this", "create quiz")
3. Interrupt/cancel during playback
4. Voice activity detection (auto-start/stop)

---

## 🔧 Technical Notes

### Browser API Option (Quick Start)
```typescript
// Simple Web Speech API implementation
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();

recognition.continuous = false;
recognition.lang = 'en-US';
recognition.interimResults = false;

recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
  setQueryText(transcript);
};

// Start recording
recognition.start();
```

**Pros:** No backend needed, free, fast
**Cons:** Limited language support, requires internet, inconsistent across browsers

### Backend Service Option (Production)
Use OpenAI Whisper or Google Speech-to-Text for better accuracy and language support.

---

## 📝 Configuration

Add to `frontend/.env`:
```env
NEXT_PUBLIC_ENABLE_VOICE=true
NEXT_PUBLIC_VOICE_PROVIDER=browser  # or 'openai', 'google', 'azure'
NEXT_PUBLIC_VOICE_API_KEY=your_api_key_here
```

Add to backend `.env`:
```env
OPENAI_API_KEY=your_openai_key
GOOGLE_CLOUD_KEY_PATH=/path/to/service-account.json
TTS_PROVIDER=google  # or 'elevenlabs', 'polly'
```

---

## ✅ Testing Checklist

- [ ] Microphone permission request works
- [ ] Audio recording captures correctly
- [ ] STT transcription is accurate
- [ ] Query with voice input works
- [ ] TTS playback is clear
- [ ] Multi-language support works
- [ ] Mobile device compatibility
- [ ] Error handling for network issues
- [ ] Fallback to text if voice fails
- [ ] Performance (no lag during recording)

---

## 📚 Resources

### APIs & Services
- [OpenAI Whisper](https://platform.openai.com/docs/guides/speech-to-text)
- [Google Cloud Speech-to-Text](https://cloud.google.com/speech-to-text)
- [ElevenLabs TTS](https://elevenlabs.io/docs)
- [Web Speech API MDN](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)

### Libraries
- [RecordRTC](https://recordrtc.org/)
- [WaveSurfer.js](https://wavesurfer-js.org/)
- [Howler.js](https://howlerjs.com/) - Audio playback

---

## 🎯 Summary

**Key locations to add voice interface:**
1. ✅ `frontend/components/StudioGrid.tsx` - Labels updated
2. 🔜 `frontend/components/VoiceInput.tsx` - NEW component for recording
3. 🔜 `frontend/components/VoiceOutput.tsx` - NEW component for playback
4. 🔜 `frontend/app/page.tsx` - Integrate with Query tool
5. 🔜 `frontend/lib/api.ts` - Add voice API functions
6. 🔜 `src/server.py` - Add backend endpoints
7. 🔜 Notes chat input - Add voice note recording

Start with Phase 1 (basic voice input) and progressively add features!

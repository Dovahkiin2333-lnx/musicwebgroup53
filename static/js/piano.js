const pianoKeys = [
    { note: 'C', key: 'a', type: 'white', octave: 4 },
    { note: 'C#', key: 'w', type: 'black', octave: 4 },
    { note: 'D', key: 's', type: 'white', octave: 4 },
    { note: 'D#', key: 'e', type: 'black', octave: 4 },
    { note: 'E', key: 'd', type: 'white', octave: 4 },
    { note: 'F', key: 'f', type: 'white', octave: 4 },
    { note: 'F#', key: 't', type: 'black', octave: 4 },
    { note: 'G', key: 'g', type: 'white', octave: 4 },
    { note: 'G#', key: 'y', type: 'black', octave: 4 },
    { note: 'A', key: 'h', type: 'white', octave: 4 },
    { note: 'A#', key: 'u', type: 'black', octave: 4 },
    { note: 'B', key: 'j', type: 'white', octave: 4 },
    { note: 'C', key: 'k', type: 'white', octave: 5 }  
];



let isRecording = false;
let recordedNotes = [];
let recordingStartTime;
let audioContext;
const oscillators = {};

function initPiano() {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    
    const pianoElement = document.getElementById('piano');
    document.getElementById('startRecording').addEventListener('click', startRecording);
    document.getElementById('stopRecording').addEventListener('click', stopRecording);
    document.getElementById('downloadRecording').addEventListener('click', downloadRecording);
    
    pianoKeys.forEach(keyConfig => {
        const keyElement = document.createElement('div');
        keyElement.className = `key ${keyConfig.type}-key`;
        keyElement.dataset.note = `${keyConfig.note}${keyConfig.octave}`;
        keyElement.dataset.key = keyConfig.key;
        
        const labelElement = document.createElement('div');
        labelElement.className = 'key-label';
        labelElement.textContent = `${keyConfig.note} (${keyConfig.key.toUpperCase()})`;
        keyElement.appendChild(labelElement);
        
        keyElement.addEventListener('mousedown', () => playNote(keyConfig));
        keyElement.addEventListener('mouseup', () => stopNote(keyConfig));
        keyElement.addEventListener('mouseleave', () => stopNote(keyConfig));
        
        keyElement.addEventListener('touchstart', (e) => {
            e.preventDefault();
            playNote(keyConfig);
        });
        
        keyElement.addEventListener('touchend', (e) => {
            e.preventDefault();
            stopNote(keyConfig);
        });
        
        pianoElement.appendChild(keyElement);
    });
    
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);
}

function startRecording() {
    if (isRecording) return;
    
    isRecording = true;
    recordedNotes = [];
    recordingStartTime = Date.now();
    
    document.getElementById('recordingStatus').textContent = 'recording...';
    document.getElementById('startRecording').disabled = true;
    document.getElementById('stopRecording').disabled = false;
    document.getElementById('downloadRecording').disabled = true;
}

function stopRecording() {
    if (!isRecording) return;
    
    isRecording = false;
    
    document.getElementById('recordingStatus').textContent = 'stop';
    document.getElementById('startRecording').disabled = false;
    document.getElementById('stopRecording').disabled = true;
    document.getElementById('downloadRecording').disabled = false;
}

function downloadRecording() {
    if (recordedNotes.length === 0) {
        alert('no content can be download');
        return;
    }
    
    const midiBlob = createMidiFile(recordedNotes);
    const url = URL.createObjectURL(midiBlob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `piano_recording_${new Date().toISOString().slice(0, 10)}.mid`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function createMidiFile(notes) {
    const header = new Uint8Array([
        0x4D, 0x54, 0x68, 0x64, 0x00, 0x00, 0x00, 0x06,
        0x00, 0x01, 0x00, 0x01, 0x00, 0x78
    ]);
    
    let trackData = [];
    
    notes.forEach(note => {
        trackData.push(0x00, 0x90, note.pitch, 0x7F);
        
        const durationTicks = Math.round(note.duration * 480); 
        trackData.push(durationTicks >> 8, durationTicks & 0xFF, 0x80, note.pitch, 0x00);
    });
    
    trackData.push(0x00, 0xFF, 0x2F, 0x00);
    
    const trackChunk = new Uint8Array([
        0x4D, 0x54, 0x72, 0x6B, 
        (trackData.length >> 24) & 0xFF,
        (trackData.length >> 16) & 0xFF,
        (trackData.length >> 8) & 0xFF,
        trackData.length & 0xFF,
        ...trackData
    ]);
    
    const midiData = new Uint8Array(header.length + trackChunk.length);
    midiData.set(header, 0);
    midiData.set(trackChunk, header.length);
    
    return new Blob([midiData], { type: 'audio/midi' });
}

function playNote(keyConfig) {
    const noteId = `${keyConfig.note}${keyConfig.octave}`;
    const keyElement = document.querySelector(`.key[data-note="${noteId}"]`);
    
    if (keyElement) {
        keyElement.classList.add('active');
    }
    
    if (oscillators[noteId]) return; 
    
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    const frequency = calculateFrequency(keyConfig.note, keyConfig.octave);
    oscillator.frequency.value = frequency;
    
    oscillator.type = 'sine';
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    gainNode.gain.setValueAtTime(0, audioContext.currentTime);
    gainNode.gain.linearRampToValueAtTime(1, audioContext.currentTime + 0.02);
    
    oscillator.start();
    
    if (isRecording) {
        oscillators[noteId] = { 
            oscillator, 
            gainNode,
            startTime: Date.now() - recordingStartTime,
            pitch: getMidiPitch(keyConfig.note, keyConfig.octave)
        };
    } else {
        oscillators[noteId] = { oscillator, gainNode };
    }
}

function stopNote(keyConfig) {
    const noteId = `${keyConfig.note}${keyConfig.octave}`;
    const keyElement = document.querySelector(`.key[data-note="${noteId}"]`);
    
    if (keyElement) {
        keyElement.classList.remove('active');
    }
    
    if (!oscillators[noteId]) return;
    
    if (isRecording && oscillators[noteId].startTime !== undefined) {
        const duration = (Date.now() - recordingStartTime - oscillators[noteId].startTime) / 1000;
        recordedNotes.push({
            pitch: oscillators[noteId].pitch,
            startTime: oscillators[noteId].startTime / 1000,
            duration: duration
        });
    }
    
    oscillators[noteId].gainNode.gain.linearRampToValueAtTime(
        0, audioContext.currentTime + 0.05
    );
    
    setTimeout(() => {
        oscillators[noteId].oscillator.stop();
        delete oscillators[noteId];
    }, 50);
}
function getMidiPitch(note, octave) {
    const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    const noteIndex = notes.indexOf(note);
    return 12 + (octave * 12) + noteIndex;
}

function calculateFrequency(note, octave) {
    const notes = {
        'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 
        'E': 4, 'F': 5, 'F#': 6, 'G': 7, 
        'G#': 8, 'A': 9, 'A#': 10, 'B': 11
    };
    

    const semitoneOffset = notes[note] - 9; 
    const semitonesFromA4 = semitoneOffset + (octave - 4) * 12;
    
    return 440 * Math.pow(2, semitonesFromA4 / 12);
}


function handleKeyDown(e) {
    if (e.repeat) return; 
    
    const keyConfig = pianoKeys.find(k => k.key === e.key.toLowerCase());
    if (keyConfig) {
        playNote(keyConfig);
    }
}


function handleKeyUp(e) {
    const keyConfig = pianoKeys.find(k => k.key === e.key.toLowerCase());
    if (keyConfig) {
        stopNote(keyConfig);
    }
}


document.addEventListener('DOMContentLoaded', initPiano);

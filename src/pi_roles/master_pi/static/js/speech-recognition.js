function submitAnnouncement(form) {
    const title = document.getElementById('announcementTitle').value;
    const type = document.getElementById('announcementType').value;
    const message = document.getElementById('announcementText').value;

    const formData = new FormData();
    formData.append('announcementTitle', title);
    formData.append('announcementType', type);
    formData.append('announcementMessage', message);
    console.log('Submitting announcement:', title, type, message);

    fetch('/publish_announcement', {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        if (response.ok) {
            alert('Announcement published successfully!');
            form.reset();
        } else {
            alert('Failed to publish announcement.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while publishing the announcement.');
    });
}

(function () {
    const textarea = document.getElementById('announcementText');
    const voiceBtn = document.getElementById('voiceBtn');
    const voiceStatus = document.getElementById('voiceStatus');
    const clearBtn = document.getElementById('clearBtn');

    // New elements for title voice input
    const titleInput = document.getElementById('announcementTitle');
    const voiceTitleBtn = document.getElementById('voiceTitleBtn');
    const voiceTitleStatus = document.getElementById('voiceTitleStatus');

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        voiceBtn.disabled = true;
        if (voiceTitleBtn) voiceTitleBtn.disabled = true;
        voiceStatus.textContent = 'Voice input not supported in this browser.';
        if (voiceTitleStatus) voiceTitleStatus.textContent = 'Voice input not supported in this browser.';
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = navigator.language || 'en-US';
    recognition.interimResults = true;
    recognition.continuous = false;

    let isListening = false;
    let currentTarget = null; // 'text' or 'title'
    let finalTranscriptText = '';
    let finalTranscriptTitle = '';

    function updateUI() {
        // Text button UI
        const textActive = isListening && currentTarget === 'text';
        voiceBtn.textContent = textActive ? '⏹ Stop voice' : '🎤 Start voice';
        voiceBtn.classList.toggle('btn-danger', textActive);
        voiceBtn.classList.toggle('btn-outline-secondary', !textActive);
        voiceStatus.textContent = textActive ? 'Listening for announcement text...' : 'Voice input inactive';

        // Title button UI
        if (voiceTitleBtn) {
            const titleActive = isListening && currentTarget === 'title';
            voiceTitleBtn.textContent = titleActive ? '⏹' : '🎤';
            voiceTitleBtn.classList.toggle('btn-danger', titleActive);
            voiceTitleBtn.classList.toggle('btn-outline-secondary', !titleActive);
            if (voiceTitleStatus) voiceTitleStatus.textContent = titleActive ? 'Listening for title...' : 'Voice: not supported or inactive';
        }
    }

    // Start/stop for announcement text
    voiceBtn.addEventListener('click', () => {
        if (isListening && currentTarget === 'text') {
            recognition.stop();
            return;
        }
        // If another target is listening, stop it first
        if (isListening && currentTarget === 'title') {
            recognition.stop();
            // recognition.end event will handle starting again if needed, but keep it simple:
            // small timeout to ensure previous instance ended
            setTimeout(() => {
                currentTarget = 'text';
                finalTranscriptText = textarea.value || '';
                recognition.start();
            }, 200);
            return;
        }
        currentTarget = 'text';
        finalTranscriptText = textarea.value || '';
        recognition.start();
    });

    // Start/stop for title
    if (voiceTitleBtn) {
        voiceTitleBtn.addEventListener('click', () => {
            if (isListening && currentTarget === 'title') {
                recognition.stop();
                return;
            }
            if (isListening && currentTarget === 'text') {
                recognition.stop();
                setTimeout(() => {
                    currentTarget = 'title';
                    finalTranscriptTitle = titleInput.value || '';
                    recognition.start();
                }, 200);
                return;
            }
            currentTarget = 'title';
            finalTranscriptTitle = titleInput.value || '';
            recognition.start();
        });
    }

    recognition.addEventListener('start', () => {
        isListening = true;
        updateUI();
    });

    recognition.addEventListener('end', () => {
        isListening = false;
        // keep currentTarget until UI updated; then clear to indicate no active target
        updateUI();
        currentTarget = null;
    });

    recognition.addEventListener('error', (e) => {
        console.error('Speech recognition error', e);
        const message = 'Voice input error: ' + (e.error || 'unknown');
        if (currentTarget === 'title' && voiceTitleStatus) {
            voiceTitleStatus.textContent = message;
        } else {
            voiceStatus.textContent = message;
        }
    });

    recognition.addEventListener('result', (e) => {
        let interim = '';
        for (let i = e.resultIndex; i < e.results.length; ++i) {
            const transcript = e.results[i][0].transcript;
            if (e.results[i].isFinal) {
                if (currentTarget === 'title') {
                    finalTranscriptTitle += (finalTranscriptTitle ? ' ' : '') + transcript;
                } else {
                    finalTranscriptText += (finalTranscriptText ? ' ' : '') + transcript;
                }
            } else {
                interim += transcript;
            }
        }

        if (currentTarget === 'title') {
            // Show combined final + interim in title input
            titleInput.value = finalTranscriptTitle + (interim ? ' ' + interim : '');
        } else {
            // Default to text area
            textarea.value = finalTranscriptText + (interim ? ' ' + interim : '');
        }
    });

    clearBtn.addEventListener('click', () => {
        textarea.value = '';
        if (titleInput) titleInput.value = '';
        const typeInput = document.getElementById('announcementType');
        if (typeInput) typeInput.value = '';
        // Reset transcripts and statuses
        finalTranscriptText = '';
        finalTranscriptTitle = '';
        currentTarget = null;
        isListening = false;
        updateUI();
    });

    // Initialize UI state
    updateUI();
})();
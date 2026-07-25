/**
 * AI Multi-Agent Hub for Gaming - Frontend Controller
 * Built using pure Vanilla JavaScript and Fetch API.
 */

// 1. Configurable Backend URL Constant
const API_BASE_URL = 'http://127.0.0.1:8000';

// Application State
const state = {
    activeJobId: localStorage.getItem('active_job_id') || null,
    selectedFile: null,
    isUploading: false,
    results: null
};

// DOM Elements
const elements = {
    // Status
    statusDot: document.getElementById('status-dot'),
    statusText: document.getElementById('status-text'),
    // Job Badge
    activeJobBadge: document.getElementById('active-job-badge'),
    jobIdDisplay: document.getElementById('job-id-display'),
    btnCopyJob: document.getElementById('btn-copy-job'),
    btnResetJob: document.getElementById('btn-reset-job'),
    // Upload
    uploadForm: document.getElementById('upload-form'),
    dropZone: document.getElementById('drop-zone'),
    videoFileInput: document.getElementById('video-file-input'),
    selectedFileInfo: document.getElementById('selected-file-info'),
    fileNameText: document.getElementById('file-name-text'),
    fileSizeText: document.getElementById('file-size-text'),
    btnClearFile: document.getElementById('btn-clear-file'),
    btnUpload: document.getElementById('btn-upload'),
    uploadProgressContainer: document.getElementById('upload-progress-container'),
    uploadProgressBar: document.getElementById('upload-progress-bar'),
    uploadProgressText: document.getElementById('upload-progress-text'),
    // Agent Buttons
    agentButtons: document.querySelectorAll('.agent-btn'),
    // Status Section
    btnCheckStatus: document.getElementById('btn-check-status'),
    statusPercentage: document.getElementById('status-percentage'),
    statusProgressBar: document.getElementById('status-progress-bar'),
    steps: {
        upload: document.getElementById('step-upload'),
        analysis: document.getElementById('step-analysis'),
        highlights: document.getElementById('step-highlights'),
        seo: document.getElementById('step-seo'),
        thumbnails: document.getElementById('step-thumbnails'),
        creator_brief: document.getElementById('step-creator_brief')
    },
    // Results Section
    btnFetchResults: document.getElementById('btn-fetch-results'),
    tabButtons: document.querySelectorAll('.tab-btn'),
    tabPanes: document.querySelectorAll('.tab-pane'),
    // Results Panes
    briefEmpty: document.getElementById('brief-empty'),
    briefContent: document.getElementById('brief-content'),
    briefSummaryText: document.getElementById('brief-summary-text'),

    analysisEmpty: document.getElementById('analysis-empty'),
    analysisContent: document.getElementById('analysis-content'),
    valDuration: document.getElementById('val-duration'),
    valResolution: document.getElementById('val-resolution'),
    valFps: document.getElementById('val-fps'),
    valFrames: document.getElementById('val-frames'),
    valFormat: document.getElementById('val-format'),
    valSize: document.getElementById('val-size'),

    highlightsEmpty: document.getElementById('highlights-empty'),
    highlightsContent: document.getElementById('highlights-content'),

    seoEmpty: document.getElementById('seo-empty'),
    seoContent: document.getElementById('seo-content'),
    seoTitleText: document.getElementById('seo-title-text'),
    seoDescText: document.getElementById('seo-desc-text'),
    seoTagsPills: document.getElementById('seo-tags-pills'),
    seoHashtagsPills: document.getElementById('seo-hashtags-pills'),

    thumbnailsEmpty: document.getElementById('thumbnails-empty'),
    thumbnailsContent: document.getElementById('thumbnails-content'),

    rawJsonBox: document.getElementById('raw-json-box'),
    btnCopyJson: document.getElementById('btn-copy-json'),
    btnCopyTitle: document.getElementById('copy-title-btn'),
    btnCopyDesc: document.getElementById('copy-desc-btn')
};

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    checkServerHealth();
    initUploadEvents();
    initAgentButtons();
    initTabs();
    initCopyButtons();
    updateJobIdUI();

    // If job ID exists in state, fetch its status and results automatically
    if (state.activeJobId) {
        fetchJobStatus();
        fetchAllResults();
    }
});

// Toast Notification Helper
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Check Backend Health
async function checkServerHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        if (response.ok) {
            elements.statusDot.className = 'status-dot online';
            elements.statusText.textContent = 'Backend Online';
        } else {
            throw new Error('Server returned error status');
        }
    } catch (error) {
        elements.statusDot.className = 'status-dot offline';
        elements.statusText.textContent = 'Backend Offline';
    }
}

// Update Active Job UI
function updateJobIdUI() {
    if (state.activeJobId) {
        elements.activeJobBadge.className = 'badge badge-active';
        elements.activeJobBadge.textContent = 'Active Job';
        elements.jobIdDisplay.textContent = state.activeJobId;
        elements.btnCopyJob.disabled = false;
        enableAgentButtons(true);
    } else {
        elements.activeJobBadge.className = 'badge badge-inactive';
        elements.activeJobBadge.textContent = 'No Active Job';
        elements.jobIdDisplay.textContent = 'None (Upload a video to start)';
        elements.btnCopyJob.disabled = true;
        enableAgentButtons(false);
    }
}

function enableAgentButtons(enabled) {
    elements.agentButtons.forEach(btn => {
        btn.disabled = !enabled;
    });
}

function setActiveJobId(jobId) {
    state.activeJobId = jobId;
    if (jobId) {
        localStorage.setItem('active_job_id', jobId);
    } else {
        localStorage.removeItem('active_job_id');
    }
    updateJobIdUI();
}

// File Upload Event Listeners
function initUploadEvents() {
    // Drop Zone Click
    elements.dropZone.addEventListener('click', () => {
        elements.videoFileInput.click();
    });

    // File Input Change
    elements.videoFileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    // Drag & Drop
    ['dragenter', 'dragover'].forEach(eventName => {
        elements.dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            elements.dropZone.classList.add('drag-over');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        elements.dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            elements.dropZone.classList.remove('drag-over');
        });
    });

    elements.dropZone.addEventListener('drop', (e) => {
        if (e.dataTransfer.files.length > 0) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    // Clear Selected File
    elements.btnClearFile.addEventListener('click', (e) => {
        e.stopPropagation();
        clearFileSelection();
    });

    // Form Submit (Upload)
    elements.uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!state.selectedFile || state.isUploading) return;
        await uploadVideo();
    });

    // Job Reset Button
    elements.btnResetJob.addEventListener('click', () => {
        setActiveJobId(null);
        resetResultsUI();
        resetStatusUI();
        showToast('Active job cleared. Upload a new video.', 'info');
    });

    // Copy Job ID
    elements.btnCopyJob.addEventListener('click', () => {
        if (state.activeJobId) {
            navigator.clipboard.writeText(state.activeJobId);
            showToast('Job ID copied to clipboard!', 'success');
        }
    });
}

function handleFileSelect(file) {
    state.selectedFile = file;
    elements.fileNameText.textContent = file.name;
    elements.fileSizeText.textContent = formatBytes(file.size);
    elements.selectedFileInfo.classList.remove('hidden');
    elements.btnUpload.disabled = false;
}

function clearFileSelection() {
    state.selectedFile = null;
    elements.videoFileInput.value = '';
    elements.selectedFileInfo.classList.add('hidden');
    elements.btnUpload.disabled = true;
}

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Upload Video via Fetch API
async function uploadVideo() {
    state.isUploading = true;
    elements.btnUpload.disabled = true;
    elements.uploadProgressContainer.classList.remove('hidden');
    elements.uploadProgressBar.style.width = '30%';
    elements.uploadProgressText.textContent = '30%';

    const formData = new FormData();
    formData.append('file', state.selectedFile);

    try {
        elements.uploadProgressBar.style.width = '60%';
        elements.uploadProgressText.textContent = '60%';

        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Upload failed');
        }

        elements.uploadProgressBar.style.width = '100%';
        elements.uploadProgressText.textContent = '100%';

        // Store returned job_id automatically
        setActiveJobId(data.job_id);

        showToast('Video uploaded successfully!', 'success');
        clearFileSelection();
        
        // Fetch status and results for the newly created job
        await fetchJobStatus();
        await fetchAllResults();

    } catch (error) {
        showToast(`Upload Error: ${error.message}`, 'error');
    } finally {
        state.isUploading = false;
        setTimeout(() => {
            elements.uploadProgressContainer.classList.add('hidden');
            elements.uploadProgressBar.style.width = '0%';
        }, 1000);
    }
}

// Agent Control Center Actions
function initAgentButtons() {
    elements.agentButtons.forEach(button => {
        button.addEventListener('click', async () => {
            const agent = button.getAttribute('data-agent');
            if (!state.activeJobId) {
                showToast('Please upload a video or select an active job first.', 'error');
                return;
            }
            await runAgent(agent, button);
        });
    });

    elements.btnCheckStatus.addEventListener('click', fetchJobStatus);
    elements.btnFetchResults.addEventListener('click', fetchAllResults);
}

// Generic Agent Caller using Fetch API
async function runAgent(agentName, buttonElement) {
    const originalText = buttonElement.querySelector('.agent-name').textContent;
    buttonElement.querySelector('.agent-name').textContent = 'Processing...';
    buttonElement.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/${agentName}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ job_id: state.activeJobId })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || `${agentName} processing failed`);
        }

        showToast(`${originalText} executed successfully!`, 'success');
        
        // Refresh status and results view
        await fetchJobStatus();
        await fetchAllResults();

    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        buttonElement.querySelector('.agent-name').textContent = originalText;
        buttonElement.disabled = false;
    }
}

// Fetch Job Progress Status
async function fetchJobStatus() {
    if (!state.activeJobId) return;

    try {
        const response = await fetch(`${API_BASE_URL}/status/${state.activeJobId}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to fetch status');
        }

        // Update progress bar
        const percent = data.progress_percentage || 0;
        elements.statusPercentage.textContent = `${percent}%`;
        elements.statusProgressBar.style.width = `${percent}%`;

        // Update Step Badges
        const statusMap = data.status || {};
        Object.keys(elements.steps).forEach(stepKey => {
            const stepElement = elements.steps[stepKey];
            if (stepElement) {
                if (statusMap[stepKey]) {
                    stepElement.classList.add('completed');
                } else {
                    stepElement.classList.remove('completed');
                }
            }
        });

    } catch (error) {
        console.error('Status fetch error:', error);
    }
}

// Fetch Aggregated Results
async function fetchAllResults() {
    if (!state.activeJobId) return;

    try {
        const response = await fetch(`${API_BASE_URL}/results/${state.activeJobId}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to fetch results');
        }

        state.results = data.results;
        elements.rawJsonBox.textContent = JSON.stringify(data, null, 4);

        // Render sections
        renderAnalysis(data.results.analysis);
        renderHighlights(data.results.highlights);
        renderSEO(data.results.seo);
        renderThumbnails(data.results.thumbnails);
        renderCreatorBrief(data.results.creator_brief);

    } catch (error) {
        console.error('Results fetch error:', error);
    }
}

// Render Results Views
function renderAnalysis(analysis) {
    if (!analysis) {
        elements.analysisEmpty.classList.remove('hidden');
        elements.analysisContent.classList.add('hidden');
        return;
    }

    elements.analysisEmpty.classList.add('hidden');
    elements.analysisContent.classList.remove('hidden');

    elements.valDuration.textContent = `${analysis.duration || 0}s`;
    elements.valResolution.textContent = analysis.resolution || 'Unknown';
    elements.valFps.textContent = analysis.fps || 0;
    elements.valFrames.textContent = analysis.frame_count || 0;
    elements.valFormat.textContent = analysis.video_format || '-';
    elements.valSize.textContent = formatBytes(analysis.file_size || 0);
}

function renderHighlights(highlights) {
    if (!highlights || highlights.length === 0) {
        elements.highlightsEmpty.classList.remove('hidden');
        elements.highlightsContent.classList.add('hidden');
        return;
    }

    elements.highlightsEmpty.classList.add('hidden');
    elements.highlightsContent.classList.remove('hidden');
    elements.highlightsContent.innerHTML = '';

    highlights.forEach(h => {
        const item = document.createElement('div');
        item.className = 'highlight-item';
        item.innerHTML = `
            <span class="highlight-timestamp">⏱️ ${h.timestamp}</span>
            <div class="highlight-meta">
                <span>Frame: ${h.frame_index}</span> | 
                <span>Motion: ${h.motion_intensity ? h.motion_intensity.toFixed(2) : '-'}</span>
            </div>
        `;
        elements.highlightsContent.appendChild(item);
    });
}

function renderSEO(seo) {
    if (!seo) {
        elements.seoEmpty.classList.remove('hidden');
        elements.seoContent.classList.add('hidden');
        return;
    }

    elements.seoEmpty.classList.add('hidden');
    elements.seoContent.classList.remove('hidden');

    elements.seoTitleText.textContent = seo.title || '';
    elements.seoDescText.textContent = seo.description || '';

    // Render Tags
    elements.seoTagsPills.innerHTML = '';
    (seo.tags || []).forEach(tag => {
        const pill = document.createElement('span');
        pill.className = 'pill';
        pill.textContent = tag;
        elements.seoTagsPills.appendChild(pill);
    });

    // Render Hashtags
    elements.seoHashtagsPills.innerHTML = '';
    (seo.hashtags || []).forEach(tag => {
        const pill = document.createElement('span');
        pill.className = 'pill';
        pill.textContent = tag;
        elements.seoHashtagsPills.appendChild(pill);
    });
}

function renderThumbnails(thumbnails) {
    if (!thumbnails || thumbnails.length === 0) {
        elements.thumbnailsEmpty.classList.remove('hidden');
        elements.thumbnailsContent.classList.add('hidden');
        return;
    }

    elements.thumbnailsEmpty.classList.add('hidden');
    elements.thumbnailsContent.classList.remove('hidden');
    elements.thumbnailsContent.innerHTML = '';

    thumbnails.forEach((t, idx) => {
        const card = document.createElement('div');
        card.className = 'thumbnail-card';
        // Format full image URL using API_BASE_URL
        const imgUrl = `${API_BASE_URL}/${t.image_path}`;
        
        card.innerHTML = `
            <img src="${imgUrl}" alt="Thumbnail ${idx + 1}" onerror="this.onerror=null; this.src='https://via.placeholder.com/300x180?text=Thumbnail+Image';">
            <div class="thumbnail-overlay">
                <span class="thumb-time">⏱️ ${t.timestamp}</span>
                <a href="${imgUrl}" target="_blank" class="btn-copy-small">View Full</a>
            </div>
        `;
        elements.thumbnailsContent.appendChild(card);
    });
}

function renderCreatorBrief(brief) {
    if (!brief) {
        elements.briefEmpty.classList.remove('hidden');
        elements.briefContent.classList.add('hidden');
        return;
    }

    elements.briefEmpty.classList.add('hidden');
    elements.briefContent.classList.remove('hidden');
    elements.briefSummaryText.textContent = brief.summary || '';
}

// Reset UI States
function resetResultsUI() {
    elements.briefEmpty.classList.remove('hidden');
    elements.briefContent.classList.add('hidden');

    elements.analysisEmpty.classList.remove('hidden');
    elements.analysisContent.classList.add('hidden');

    elements.highlightsEmpty.classList.remove('hidden');
    elements.highlightsContent.classList.add('hidden');

    elements.seoEmpty.classList.remove('hidden');
    elements.seoContent.classList.add('hidden');

    elements.thumbnailsEmpty.classList.remove('hidden');
    elements.thumbnailsContent.classList.add('hidden');

    elements.rawJsonBox.textContent = '{}';
}

function resetStatusUI() {
    elements.statusPercentage.textContent = '0%';
    elements.statusProgressBar.style.width = '0%';
    Object.values(elements.steps).forEach(chip => {
        if (chip) chip.classList.remove('completed');
    });
}

// Tab Switching
function initTabs() {
    elements.tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            elements.tabButtons.forEach(b => b.classList.remove('active'));
            elements.tabPanes.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            const targetPaneId = btn.getAttribute('data-tab');
            document.getElementById(targetPaneId).classList.add('active');
        });
    });
}

// Copy Handlers
function initCopyButtons() {
    elements.btnCopyTitle.addEventListener('click', () => {
        const title = elements.seoTitleText.textContent;
        if (title) {
            navigator.clipboard.writeText(title);
            showToast('SEO Title copied!', 'success');
        }
    });

    elements.btnCopyDesc.addEventListener('click', () => {
        const desc = elements.seoDescText.textContent;
        if (desc) {
            navigator.clipboard.writeText(desc);
            showToast('SEO Description copied!', 'success');
        }
    });

    elements.btnCopyJson.addEventListener('click', () => {
        const json = elements.rawJsonBox.textContent;
        if (json) {
            navigator.clipboard.writeText(json);
            showToast('Raw JSON copied!', 'success');
        }
    });
}

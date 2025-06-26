/**
 * LightBox Web GUI - Modern JavaScript Application
 * Handles all interactive functionality for the LED matrix control interface
 */

class LightBoxApp {
    constructor() {
        this.config = {};
        this.status = {};
        this.programs = [];
        this.presets = {};
        this.isConnected = false;
        this.updateInterval = null;
        this.userIsEditing = false;
        this.editTimeout = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadInitialData();
        this.startStatusUpdates();
        this.hideLoadingOverlay();
    }
    
    setupEventListeners() {
        // Animation controls
        document.getElementById('startBtn').addEventListener('click', () => this.controlAnimation('start'));
        document.getElementById('stopBtn').addEventListener('click', () => this.controlAnimation('stop'));
        
        // Program selection
        document.getElementById('programSelect').addEventListener('change', (e) => this.loadProgram(e.target.value));
        
        // Palette selection
        document.getElementById('paletteSelect').addEventListener('change', (e) => this.loadPalette(e.target.value));
        
        // Configuration sliders
        const sliders = [
            'brightnessSlider', 'speedSlider', 'scaleSlider', 'fpsSlider', 'hueSlider', 
            'saturationSlider', 'gammaSlider'
        ];
        
        sliders.forEach(id => {
            const slider = document.getElementById(id);
            if (slider) {
                slider.addEventListener('input', (e) => this.handleSliderChange(id, e.target.value));
                slider.addEventListener('focus', () => this.pauseUpdates());
                slider.addEventListener('blur', () => this.resumeUpdates());
            }
        });
        
        // File upload
        this.setupFileUpload();
        
        // Preset controls
        document.getElementById('savePresetBtn').addEventListener('click', () => this.savePreset());
        
        // Window events
        window.addEventListener('beforeunload', () => this.cleanup());
    }
    
    setupFileUpload() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        
        // Click to browse
        uploadArea.addEventListener('click', () => fileInput.click());
        
        // File selection
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.uploadFile(e.target.files[0]);
            }
        });
        
        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            if (e.dataTransfer.files.length > 0) {
                this.uploadFile(e.dataTransfer.files[0]);
            }
        });
    }
    
    async loadInitialData() {
        try {
            await this.updateStatus();
            await this.loadPresets();
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.showNotification('Failed to connect to LightBox', 'error');
        }
    }
    
    startStatusUpdates() {
        this.updateInterval = setInterval(() => {
            if (!this.userIsEditing) {
                this.updateStatus();
            }
        }, 2000);
    }
    
    pauseUpdates() {
        this.userIsEditing = true;
        if (this.editTimeout) {
            clearTimeout(this.editTimeout);
        }
    }
    
    resumeUpdates() {
        this.editTimeout = setTimeout(() => {
            this.userIsEditing = false;
        }, 3000);
    }
    
    async updateStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.status = data;
            this.config = data.config || {};
            this.programs = data.programs || [];
            
            this.updateUI();
            this.updateConnectionStatus(true);
            
        } catch (error) {
            console.error('Status update failed:', error);
            this.updateConnectionStatus(false);
        }
    }
    
    updateUI() {
        this.updateStatusDisplay();
        this.updateProgramsList();
        this.updateConfigurationForm();
        this.updateSystemStats();
    }
    
    updateStatusDisplay() {
        // Update status indicator
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        
        if (this.status.running) {
            statusDot.className = 'status-dot connected';
            statusText.textContent = 'Running';
        } else {
            statusDot.className = 'status-dot';
            statusText.textContent = 'Stopped';
        }
        
        // Update current program
        document.getElementById('currentProgram').textContent = this.status.current_program || '-';
        document.getElementById('statusProgram').textContent = this.status.current_program || '-';
    }
    
    updateProgramsList() {
        const select = document.getElementById('programSelect');
        const grid = document.getElementById('programsGrid');
        
        // Update select dropdown
        select.innerHTML = '<option value="">Select a program...</option>';
        this.programs.forEach(program => {
            const option = document.createElement('option');
            option.value = program.name;
            option.textContent = program.name === 'cosmic' ? 'Cosmic (Built-in)' : program.name;
            if (program.name === this.status.current_program) {
                option.selected = true;
            }
            select.appendChild(option);
        });
        
        // Update programs grid
        grid.innerHTML = '';
        this.programs.forEach(program => {
            const card = this.createProgramCard(program);
            grid.appendChild(card);
        });
    }
    
    createProgramCard(program) {
        const card = document.createElement('div');
        card.className = 'program-card';
        
        const isCurrent = program.name === this.status.current_program;
        const isBuiltin = program.name === 'cosmic';
        const metadata = program.metadata || {};
        
        // Format program name with version
        const displayName = metadata.name || program.name;
        const version = metadata.version ? ` v${metadata.version}` : '';
        
        card.innerHTML = `
            <div class="program-info">
                <div class="program-name">
                    ${displayName}${version}
                    ${isBuiltin ? '<span style="color: var(--primary-color); font-size: 0.8em;">(Built-in)</span>' : ''}
                    ${isCurrent ? '<span style="color: var(--success-color); font-size: 0.8em;">(Active)</span>' : ''}
                </div>
                ${metadata.description ? `<div class="program-description">${metadata.description}</div>` : ''}
                <div class="program-meta">
                    ${program.size ? `${(program.size / 1024).toFixed(1)} KB` : 'Built-in'}
                    ${program.modified ? `• Modified: ${new Date(program.modified).toLocaleDateString()}` : ''}
                    ${metadata.author ? `• by ${metadata.author}` : ''}
                </div>
                ${metadata.features ? `
                    <div class="program-features">
                        <details>
                            <summary>Features</summary>
                            <ul>
                                ${metadata.features.map(feature => `<li>${feature}</li>`).join('')}
                            </ul>
                        </details>
                    </div>
                ` : ''}
                ${metadata.cycle_info ? `
                    <div class="program-timing">
                        <small>⏱️ ${metadata.cycle_info.total_sequence || metadata.cycle_info.total_cycle || 'Continuous'}</small>
                    </div>
                ` : ''}
            </div>
            <div class="program-actions">
                ${!isCurrent ? `<button class="btn btn-primary btn-sm" onclick="app.loadProgram('${program.name}')">
                    <i class="fas fa-play"></i>
                </button>` : ''}
                <button class="btn btn-secondary btn-sm" onclick="app.showProgramInfo('${program.name}')" title="Show Details">
                    <i class="fas fa-info-circle"></i>
                </button>
                ${!isBuiltin && !isCurrent ? `<button class="btn btn-danger btn-sm" onclick="app.deleteProgram('${program.name}')">
                    <i class="fas fa-trash"></i>
                </button>` : ''}
            </div>
        `;
        
        return card;
    }
    
    async showProgramInfo(programName) {
        try {
            const response = await fetch(`/api/program/${programName}/info`);
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.displayProgramInfoModal(data);
            
        } catch (error) {
            console.error('Failed to load program info:', error);
            this.showNotification(`Failed to load program info: ${error.message}`, 'error');
        }
    }
    
    displayProgramInfoModal(programInfo) {
        const metadata = programInfo.metadata || {};
        
        // Create modal content
        const modalContent = `
            <div class="modal-overlay" onclick="this.remove()">
                <div class="modal-content" onclick="event.stopPropagation()">
                    <div class="modal-header">
                        <h3>${metadata.name || programInfo.name} ${metadata.version ? `v${metadata.version}` : ''}</h3>
                        <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
                    </div>
                    <div class="modal-body">
                        ${metadata.description ? `<p class="program-description">${metadata.description}</p>` : ''}
                        
                        ${metadata.author ? `<p><strong>Author:</strong> ${metadata.author}</p>` : ''}
                        
                        <div class="program-details">
                            <p><strong>File:</strong> ${programInfo.name}.py (${(programInfo.size / 1024).toFixed(1)} KB)</p>
                            <p><strong>Modified:</strong> ${new Date(programInfo.modified).toLocaleString()}</p>
                            <p><strong>Status:</strong> ${programInfo.is_current ? 'Currently Active' : 'Available'}</p>
                        </div>
                        
                        ${metadata.parameters && Object.keys(metadata.parameters).length > 0 ? `
                            <div class="parameters-section">
                                <h4>Adjustable Parameters</h4>
                                <ul class="parameters-list">
                                    ${Object.entries(metadata.parameters).map(([param, description]) => 
                                        `<li><strong>${param}:</strong> ${description}</li>`
                                    ).join('')}
                                </ul>
                            </div>
                        ` : ''}
                        
                        ${metadata.features ? `
                            <div class="features-section">
                                <h4>Features</h4>
                                <ul class="features-list">
                                    ${metadata.features.map(feature => `<li>${feature}</li>`).join('')}
                                </ul>
                            </div>
                        ` : ''}
                        
                        ${metadata.cycle_info ? `
                            <div class="timing-section">
                                <h4>Timing Information</h4>
                                <ul class="timing-list">
                                    ${Object.entries(metadata.cycle_info).map(([key, value]) => 
                                        `<li><strong>${key.replace('_', ' ')}:</strong> ${value}</li>`
                                    ).join('')}
                                </ul>
                            </div>
                        ` : ''}
                    </div>
                    <div class="modal-footer">
                        ${!programInfo.is_current ? `
                            <button class="btn btn-primary" onclick="app.loadProgram('${programInfo.name}'); this.closest('.modal-overlay').remove();">
                                Load Program
                            </button>
                        ` : ''}
                        <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove();">
                            Close
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalContent);
    }
    
    updateConfigurationForm() {
        if (this.userIsEditing) return;
        
        const config = this.config;
        
        // Update sliders
        this.updateSlider('brightnessSlider', 'brightnessValue', config.brightness, (v) => `${(v * 100).toFixed(0)}%`);
        this.updateSlider('speedSlider', 'speedValue', config.speed, (v) => `${v}x`);
        this.updateSlider('scaleSlider', 'scaleValue', config.scale, (v) => `${v}x`);
        this.updateSlider('fpsSlider', 'fpsValue', config.fps, (v) => `${v} FPS`);
        this.updateSlider('hueSlider', 'hueValue', config.hue_offset, (v) => `${v}°`);
        this.updateSlider('saturationSlider', 'saturationValue', config.saturation, (v) => `${(v * 100).toFixed(0)}%`);
        this.updateSlider('gammaSlider', 'gammaValue', config.gamma, (v) => v.toFixed(1));
        
        // Update palette selection
        const paletteSelect = document.getElementById('paletteSelect');
        if (paletteSelect && config.current_palette) {
            paletteSelect.value = config.current_palette;
        }
    }
    
    updateSlider(sliderId, valueId, value, formatter) {
        const slider = document.getElementById(sliderId);
        const valueElement = document.getElementById(valueId);
        
        if (slider && valueElement && value !== undefined) {
            slider.value = value;
            valueElement.textContent = formatter ? formatter(value) : value;
        }
    }
    
    updateSystemStats() {
        document.getElementById('currentFps').textContent = this.status.fps || 0;
        document.getElementById('frameCount').textContent = this.status.frame_count || 0;
        document.getElementById('uptime').textContent = this.status.uptime_formatted || '0m 0s';
    }
    
    updateConnectionStatus(connected) {
        this.isConnected = connected;
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        
        if (connected) {
            statusDot.className = 'status-dot connected';
            statusText.textContent = 'Connected';
        } else {
            statusDot.className = 'status-dot error';
            statusText.textContent = 'Disconnected';
        }
    }
    
    async controlAnimation(action) {
        try {
            const response = await fetch('/api/control', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action })
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.showNotification(data.message, 'success');
            await this.updateStatus();
            
        } catch (error) {
            console.error('Animation control failed:', error);
            this.showNotification(`Failed to ${action} animation: ${error.message}`, 'error');
        }
    }
    
    async loadProgram(programName) {
        if (!programName) return;
        
        try {
            const response = await fetch('/api/program', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ program: programName })
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.showNotification(data.message, 'success');
            await this.updateStatus();
            
        } catch (error) {
            console.error('Program load failed:', error);
            this.showNotification(`Failed to load program: ${error.message}`, 'error');
        }
    }
    
    async loadPalette(paletteName) {
        if (!paletteName) return;
        
        try {
            const response = await fetch('/api/palette', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ palette: paletteName })
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.showNotification(`Switched to ${paletteName} palette`, 'success');
            await this.updateStatus();
            
        } catch (error) {
            console.error('Palette load failed:', error);
            this.showNotification(`Failed to load palette: ${error.message}`, 'error');
        }
    }
    
    async deleteProgram(programName) {
        if (!confirm(`Are you sure you want to delete "${programName}"?`)) {
            return;
        }
        
        try {
            const response = await fetch(`/api/delete/${programName}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.showNotification(data.message, 'success');
            await this.updateStatus();
            
        } catch (error) {
            console.error('Program deletion failed:', error);
            this.showNotification(`Failed to delete program: ${error.message}`, 'error');
        }
    }
    
    async uploadFile(file) {
        if (!file.name.endsWith('.py')) {
            this.showNotification('Only Python (.py) files are allowed', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        // Show progress
        const progress = document.getElementById('uploadProgress');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        
        progress.style.display = 'block';
        progressFill.style.width = '0%';
        progressText.textContent = 'Uploading...';
        
        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            progressFill.style.width = '100%';
            progressText.textContent = 'Upload complete!';
            
            setTimeout(() => {
                progress.style.display = 'none';
            }, 2000);
            
            this.showNotification(data.message, 'success');
            await this.updateStatus();
            
        } catch (error) {
            console.error('Upload failed:', error);
            progressText.textContent = 'Upload failed';
            progressFill.style.width = '0%';
            
            setTimeout(() => {
                progress.style.display = 'none';
            }, 3000);
            
            this.showNotification(`Upload failed: ${error.message}`, 'error');
        }
    }
    
    async handleSliderChange(sliderId, value) {
        const configMap = {
            'brightnessSlider': 'brightness',
            'speedSlider': 'speed',
            'scaleSlider': 'scale',
            'fpsSlider': 'fps',
            'hueSlider': 'hue_offset',
            'saturationSlider': 'saturation',
            'gammaSlider': 'gamma'
        };
        
        const configKey = configMap[sliderId];
        if (!configKey) return;
        
        const numValue = parseFloat(value);
        
        try {
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ [configKey]: numValue })
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Update local config
            this.config = data.config;
            
        } catch (error) {
            console.error('Config update failed:', error);
            this.showNotification(`Failed to update ${configKey}: ${error.message}`, 'error');
        }
    }
    
    async loadPresets() {
        try {
            const response = await fetch('/api/presets');
            const data = await response.json();
            
            this.presets = data;
            this.updatePresetsList();
            
        } catch (error) {
            console.error('Failed to load presets:', error);
        }
    }
    
    updatePresetsList() {
        const list = document.getElementById('presetsList');
        list.innerHTML = '';
        
        Object.entries(this.presets).forEach(([name, preset]) => {
            const item = this.createPresetItem(name, preset);
            list.appendChild(item);
        });
    }
    
    createPresetItem(name, preset) {
        const item = document.createElement('div');
        item.className = 'preset-item';
        
        item.innerHTML = `
            <div class="preset-name">${name}</div>
            <div class="preset-actions">
                <button class="btn btn-primary btn-sm" onclick="app.loadPreset('${name}')">
                    <i class="fas fa-download"></i> Load
                </button>
                <button class="btn btn-danger btn-sm" onclick="app.deletePreset('${name}')">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        
        return item;
    }
    
    async savePreset() {
        const nameInput = document.getElementById('presetName');
        const name = nameInput.value.trim();
        
        if (!name) {
            this.showNotification('Please enter a preset name', 'warning');
            return;
        }
        
        try {
            const response = await fetch('/api/presets', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: name,
                    config: this.config
                })
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            nameInput.value = '';
            this.showNotification(`Preset "${name}" saved successfully`, 'success');
            await this.loadPresets();
            
        } catch (error) {
            console.error('Preset save failed:', error);
            this.showNotification(`Failed to save preset: ${error.message}`, 'error');
        }
    }
    
    async loadPreset(presetName) {
        try {
            const response = await fetch(`/api/preset/${presetName}`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.config = data.config;
            this.showNotification(`Preset "${presetName}" loaded successfully`, 'success');
            this.updateConfigurationForm();
            
        } catch (error) {
            console.error('Preset load failed:', error);
            this.showNotification(`Failed to load preset: ${error.message}`, 'error');
        }
    }
    
    async deletePreset(presetName) {
        if (!confirm(`Are you sure you want to delete preset "${presetName}"?`)) {
            return;
        }
        
        try {
            const response = await fetch(`/api/preset/${presetName}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.showNotification(data.message, 'success');
            await this.loadPresets();
            
        } catch (error) {
            console.error('Preset deletion failed:', error);
            this.showNotification(`Failed to delete preset: ${error.message}`, 'error');
        }
    }
    
    showNotification(message, type = 'info') {
        const notifications = document.getElementById('notifications');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        notification.innerHTML = `
            <i class="notification-icon ${icons[type]}"></i>
            <div class="notification-content">
                <div class="notification-title">${type.charAt(0).toUpperCase() + type.slice(1)}</div>
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        notifications.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
    
    showLoadingOverlay() {
        document.getElementById('loadingOverlay').style.display = 'flex';
    }
    
    hideLoadingOverlay() {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
    
    cleanup() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        if (this.editTimeout) {
            clearTimeout(this.editTimeout);
        }
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new LightBoxApp();
});

// Export for global access
window.LightBoxApp = LightBoxApp; 
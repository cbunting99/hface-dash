class ModelDashboard {
    constructor() {
        this.init();
        this.refreshData();
        setInterval(() => this.refreshData(), 5000);
    }

    init() {
        document.getElementById('download-form').addEventListener('submit', (e) => this.handleDownload(e));
        document.getElementById('generate-form').addEventListener('submit', (e) => this.handleGenerate(e));
    }

    async refreshData() {
        await Promise.all([
            this.loadModels(),
            this.loadSystemInfo()
        ]);
    }

    async loadModels() {
        try {
            const response = await fetch('/api/models');
            const data = await response.json();
            this.renderModels(data.models);
            this.updateGenerateModelSelect(data.models);
        } catch (error) {
            console.error('Error loading models:', error);
        }
    }

    async loadSystemInfo() {
        try {
            const response = await fetch('/api/system');
            const data = await response.json();
            this.renderSystemInfo(data);
        } catch (error) {
            console.error('Error loading system info:', error);
        }
    }

    renderModels(models) {
        const container = document.getElementById('models-container');
        
        if (models.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center py-5">
                    <i class="fas fa-brain fa-3x text-muted mb-3"></i>
                    <p class="text-muted">No models downloaded yet</p>
                </div>
            `;
            return;
        }

        container.innerHTML = models.map(model => `
            <div class="col-md-6 mb-3">
                <div class="card model-card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="card-title mb-0">${model.name}</h6>
                            <span class="badge ${model.loaded ? 'bg-success' : 'bg-secondary'} status-badge">
                                ${model.loaded ? 'Loaded' : 'Unloaded'}
                            </span>
                        </div>
                        <p class="card-text small text-muted mb-2">${model.hf_model_id}</p>
                        <p class="card-text small">Size: ${this.formatBytes(model.size)}</p>
                        
                        <div class="btn-group w-100" role="group">
                            ${model.loaded ? 
                                `<button class="btn btn-outline-warning btn-sm" onclick="dashboard.unloadModel('${model.name}')">
                                    <i class="fas fa-pause"></i> Unload
                                </button>` :
                                `<button class="btn btn-outline-success btn-sm" onclick="dashboard.loadModel('${model.name}')">
                                    <i class="fas fa-play"></i> Load
                                </button>`
                            }
                            <button class="btn btn-outline-danger btn-sm" onclick="dashboard.deleteModel('${model.name}')">
                                <i class="fas fa-trash"></i> Delete
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    renderSystemInfo(info) {
        document.getElementById('memory-bar').style.width = `${info.memory.percent}%`;
        document.getElementById('disk-bar').style.width = `${info.disk.percent}%`;
        document.getElementById('cpu-usage').textContent = `${info.cpu_percent}%`;
    }

    updateGenerateModelSelect(models) {
        const select = document.getElementById('generate-model');
        const loadedModels = models.filter(m => m.loaded);
        
        select.innerHTML = '<option value="">Select a loaded model</option>' +
            loadedModels.map(model => `<option value="${model.name}">${model.name}</option>`).join('');
    }

    async handleDownload(e) {
        e.preventDefault();
        
        const modelName = document.getElementById('model-name').value;
        const hfModelId = document.getElementById('hf-model-id').value;
        
        const progressContainer = document.getElementById('download-progress-container');
        const progressBar = document.getElementById('download-progress');
        const progressText = document.getElementById('progress-text');
        const progressPercent = document.getElementById('progress-percent');
        const currentFile = document.getElementById('current-file');
        
        progressContainer.style.display = 'block';
        
        try {
            const response = await fetch('/api/models/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    model_name: modelName,
                    hf_model_id: hfModelId
                })
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = JSON.parse(line.slice(6));
                        
                        progressBar.style.width = `${data.progress}%`;
                        progressPercent.textContent = `${data.progress}%`;
                        
                        if (data.status === 'downloading') {
                            progressText.textContent = 'Downloading...';
                            currentFile.textContent = data.current_file;
                        } else if (data.status === 'completed') {
                            progressText.textContent = 'Download completed!';
                            currentFile.textContent = '';
                            setTimeout(() => {
                                progressContainer.style.display = 'none';
                                document.getElementById('download-form').reset();
                                this.loadModels();
                            }, 2000);
                        } else if (data.status === 'error') {
                            progressText.textContent = 'Error: ' + data.error;
                            progressBar.classList.add('bg-danger');
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Download error:', error);
            progressText.textContent = 'Download failed';
            progressBar.classList.add('bg-danger');
        }
    }

    async loadModel(modelName) {
        try {
            const response = await fetch(`/api/models/${modelName}/load`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showToast('Model loaded successfully', 'success');
                this.loadModels();
            } else {
                this.showToast('Failed to load model', 'error');
            }
        } catch (error) {
            console.error('Load error:', error);
            this.showToast('Failed to load model', 'error');
        }
    }

    async unloadModel(modelName) {
        try {
            const response = await fetch(`/api/models/${modelName}/unload`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showToast('Model unloaded successfully', 'success');
                this.loadModels();
            } else {
                this.showToast('Failed to unload model', 'error');
            }
        } catch (error) {
            console.error('Unload error:', error);
            this.showToast('Failed to unload model', 'error');
        }
    }

    async deleteModel(modelName) {
        if (!confirm(`Are you sure you want to delete model "${modelName}"?`)) {
            return;
        }

        try {
            const response = await fetch(`/api/models/${modelName}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.showToast('Model deleted successfully', 'success');
                this.loadModels();
            } else {
                this.showToast('Failed to delete model', 'error');
            }
        } catch (error) {
            console.error('Delete error:', error);
            this.showToast('Failed to delete model', 'error');
        }
    }

    async handleGenerate(e) {
        e.preventDefault();
        
        const modelName = document.getElementById('generate-model').value;
        const prompt = document.getElementById('prompt').value;
        const maxTokens = parseInt(document.getElementById('max-tokens').value);
        const temperature = parseFloat(document.getElementById('temperature').value);
        
        const resultDiv = document.getElementById('generation-result');
        const generatedText = document.getElementById('generated-text');
        
        generatedText.textContent = 'Generating...';
        resultDiv.style.display = 'block';
        
        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    model_name: modelName,
                    prompt: prompt,
                    max_tokens: maxTokens,
                    temperature: temperature
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                generatedText.textContent = data.generated_text;
            } else {
                generatedText.textContent = 'Error: ' + data.detail;
            }
        } catch (error) {
            console.error('Generation error:', error);
            generatedText.textContent = 'Generation failed';
        }
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    showToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }
}

const dashboard = new ModelDashboard();

function refreshData() {
    dashboard.refreshData();
}
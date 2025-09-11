// SEO Description Generator App
const app = {
    // Configuration
    apiUrl: window.location.origin,
    pollingInterval: null,
    productCounter: 1,

    // Initialize app
    init() {
        this.addProduct(); // Add first product item
        this.testConnection(); // Test connection on load
    },

    // Get API headers
    getHeaders() {
        const apiKey = document.getElementById('apiKey').value;
        return {
            'Content-Type': 'application/json',
            'X-API-Key': apiKey || 'default-api-key'
        };
    },

    // Show/hide loading overlay
    setLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (show) {
            overlay.classList.add('show');
        } else {
            overlay.classList.remove('show');
        }
    },

    // Switch tabs
    switchTab(tabName) {
        // Stop polling if switching away from status tab
        if (tabName !== 'status' && this.pollingInterval) {
            this.stopPolling();
        }

        // Update tab buttons
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.id === `${tabName}-tab`);
        });
    },

    // Test API connection
    async testConnection() {
        const statusIndicator = document.getElementById('connectionStatus');
        const btnText = document.getElementById('testBtnText');

        btnText.textContent = 'Testing...';

        try {
            const response = await fetch(`${this.apiUrl}/health`, {
                headers: this.getHeaders()
            });

            if (response.ok) {
                statusIndicator.classList.add('connected');
                this.showNotification('Connection successful!', 'success');
            } else {
                statusIndicator.classList.remove('connected');
                this.showNotification('Connection failed. Check your API key.', 'error');
            }
        } catch (error) {
            statusIndicator.classList.remove('connected');
            this.showNotification(`Connection error: ${error.message}`, 'error');
        } finally {
            btnText.textContent = 'Test Connection';
        }
    },

    // Generate single description
    async generateDescription(event) {
        event.preventDefault();

        const productId = document.getElementById('productId').value;
        const keywords = document.getElementById('keywords').value;
        const basicInfo = document.getElementById('basicInfo').value;

        const btnText = document.getElementById('genBtnText');
        const resultBox = document.getElementById('generateResult');

        btnText.innerHTML = '<span class="spinner" style="width: 16px; height: 16px; border-width: 2px;"></span> Generating...';
        this.setLoading(true);

        const requestBody = {
            items: [{
                product_id: productId,
                keywords: keywords ? keywords.split(',').map(k => k.trim()) : null,
                basic_info: basicInfo || null
            }]
        };

        try {
            const response = await fetch(`${this.apiUrl}/v1/generate`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(requestBody)
            });

            const data = await response.json();

            if (response.ok && data.summary && data.summary.enqueued > 0) {
                resultBox.innerHTML = `
                    <h3>✅ Request Enqueued Successfully</h3>
                    <div class="summary-stats">
                        <div class="stat-card">
                            <div class="stat-value">${data.summary.enqueued}</div>
                            <div class="stat-label">Enqueued</div>
                        </div>
                    </div>
                    <p style="margin-top: 15px; color: #6b7280;">
                        Product ID: <strong>${productId}</strong> has been queued for processing.
                    </p>
                    <details style="margin-top: 15px;">
                        <summary style="cursor: pointer; color: var(--primary);">View Response</summary>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    </details>
                `;
                this.showNotification('Description generation started!', 'success');
            } else {
                resultBox.innerHTML = `
                    <h3 style="color: var(--warning);">⚠️ Request Issue</h3>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                `;
                this.showNotification('Request issue. Check the details.', 'warning');
            }
            resultBox.classList.add('show');
        } catch (error) {
            resultBox.innerHTML = `
                <h3 style="color: var(--danger);">❌ Error</h3>
                <p>${error.message}</p>
            `;
            resultBox.classList.add('show');
            this.showNotification('Error generating description', 'error');
        } finally {
            btnText.textContent = 'Generate Description';
            this.setLoading(false);
        }
    },

    // Check status
    async checkStatus(event) {
        if (event) event.preventDefault();

        const productId = document.getElementById('statusProductId').value;
        if (!productId) return;

        const resultBox = document.getElementById('statusResult');

        try {
            const response = await fetch(`${this.apiUrl}/v1/status/${productId}`, {
                headers: this.getHeaders()
            });

            const data = await response.json();

            let statusBadge = '';
            let statusIcon = '';

            switch (data.status) {
                case 'completed':
                    statusBadge = '<span class="status-badge status-success">Completed</span>';
                    statusIcon = '✅';
                    break;
                case 'processing':
                    statusBadge = '<span class="status-badge status-processing">Processing</span>';
                    statusIcon = '⚙️';
                    break;
                case 'pending':
                    statusBadge = '<span class="status-badge status-pending">Pending</span>';
                    statusIcon = '⏳';
                    break;
                case 'failed':
                    statusBadge = '<span class="status-badge status-error">Failed</span>';
                    statusIcon = '❌';
                    break;
                default:
                    statusBadge = '<span class="status-badge status-error">Not Found</span>';
                    statusIcon = '❓';
            }

            let progressBar = '';
            if (data.progress !== undefined) {
                progressBar = `
                    <div class="progress-bar">
                        <div class="progress-bar-bg">
                            <div class="progress-bar-fill" style="width: ${data.progress}%"></div>
                        </div>
                        <div class="progress-text">${data.progress}% Complete</div>
                    </div>
                `;
            }

            resultBox.innerHTML = `
                <h3>${statusIcon} Status ${statusBadge}</h3>
                ${progressBar}
                <p style="margin: 15px 0; color: #4b5563;">
                    <strong>Message:</strong> ${data.message || 'No message'}
                </p>
                ${data.completed_at ? `<p style="color: #6b7280;">Completed: ${new Date(data.completed_at).toLocaleString()}</p>` : ''}
                <details style="margin-top: 15px;">
                    <summary style="cursor: pointer; color: var(--primary);">View Response</summary>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                </details>
            `;
            resultBox.classList.add('show');
        } catch (error) {
            resultBox.innerHTML = `
                <h3 style="color: var(--danger);">❌ Error</h3>
                <p>${error.message}</p>
            `;
            resultBox.classList.add('show');
        }
    },

    // Toggle polling
    togglePolling() {
        const btn = document.getElementById('pollBtn');

        if (this.pollingInterval) {
            this.stopPolling();
        } else {
            this.pollingInterval = setInterval(() => this.checkStatus(), 3000);
            btn.textContent = 'Stop Auto-Refresh';
            btn.classList.remove('btn-secondary');
            btn.classList.add('btn-danger');
            this.checkStatus(); // Check immediately
        }
    },

    // Stop polling
    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
            const btn = document.getElementById('pollBtn');
            btn.textContent = 'Start Auto-Refresh';
            btn.classList.remove('btn-danger');
            btn.classList.add('btn-secondary');
        }
    },

    // Retrieve description
    async retrieveDescription(event) {
        event.preventDefault();

        const productId = document.getElementById('retrieveProductId').value;
        const contentType = document.getElementById('contentType').value;

        const resultBox = document.getElementById('retrieveResult');
        this.setLoading(true);

        try {
            let url = `${this.apiUrl}/v1/description/${productId}`;
            if (contentType) {
                url += `?only=${contentType}`;
            }

            const response = await fetch(url, {
                headers: this.getHeaders()
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }

            const data = await response.json();

            // Create nice display
            let displayContent = `<h3>📄 Generated Content</h3>`;
            displayContent += '<div class="description-display">';

            if (data.description) {
                displayContent += `
                    <div class="description-section">
                        <h4>📝 Product Description</h4>
                        <div class="description-text">${data.description.replace(/\n/g, '<br>')}</div>
                    </div>
                `;
            }

            if (data.features) {
                const featureLines = data.features.split('\n').filter(line => line.trim());
                displayContent += `
                    <div class="description-section">
                        <h4>✨ Features & Specifications</h4>
                        <ul class="features-list">
                `;

                featureLines.forEach(feature => {
                    const cleanFeature = feature.replace(/^[\d\-\*\•\.]+\s*/, '').trim();
                    if (cleanFeature) {
                        displayContent += `<li>${cleanFeature}</li>`;
                    }
                });

                displayContent += `</ul></div>`;
            }

            displayContent += '</div>';

            if (data.generated_at) {
                displayContent += `
                    <p style="margin-top: 15px; color: #6b7280;">
                        Generated: ${new Date(data.generated_at).toLocaleString()}
                    </p>
                `;
            }

            displayContent += `
                <details style="margin-top: 15px;">
                    <summary style="cursor: pointer; color: var(--primary);">View JSON</summary>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                </details>
            `;

            resultBox.innerHTML = displayContent;
            resultBox.classList.add('show');
            this.showNotification('Description retrieved successfully!', 'success');
        } catch (error) {
            resultBox.innerHTML = `
                <h3 style="color: var(--danger);">❌ Error</h3>
                <p>${error.message}</p>
                <p style="color: #6b7280; margin-top: 10px;">
                    Make sure the product exists and description has been generated.
                </p>
            `;
            resultBox.classList.add('show');
            this.showNotification('Error retrieving description', 'error');
        } finally {
            this.setLoading(false);
        }
    },

    // Add product for batch
    addProduct() {
        const container = document.getElementById('batchProducts');
        const productNumber = container.children.length + 1;

        const productItem = document.createElement('div');
        productItem.className = 'product-item';
        productItem.innerHTML = `
            <div class="product-item-header">
                <div class="product-number">${productNumber}</div>
                <button class="btn btn-danger btn-small" onclick="app.removeProduct(this)">
                    Remove
                </button>
            </div>
            <div class="product-fields">
                <div class="form-group">
                    <label>Product ID *</label>
                    <input type="text" class="batch-product-id" 
                           placeholder="e.g., PROD-${String(this.productCounter++).padStart(3, '0')}">
                </div>
                <div class="form-group">
                    <label>Keywords (optional)</label>
                    <input type="text" class="batch-keywords" 
                           placeholder="e.g., LED, energy-saving">
                </div>
                <div class="form-group">
                    <label>Basic Info (optional)</label>
                    <textarea class="batch-basic-info" rows="3" 
                              placeholder="Product details..."></textarea>
                </div>
            </div>
        `;

        container.appendChild(productItem);
        this.updateProductNumbers();
    },

    // Remove product from batch
    removeProduct(button) {
        button.closest('.product-item').remove();
        this.updateProductNumbers();
    },

    // Update product numbers
    updateProductNumbers() {
        const items = document.querySelectorAll('#batchProducts .product-item');
        items.forEach((item, index) => {
            const numberElement = item.querySelector('.product-number');
            if (numberElement) {
                numberElement.textContent = index + 1;
            }
        });
    },

    // Clear batch
    clearBatch() {
        if (confirm('Clear all products?')) {
            document.getElementById('batchProducts').innerHTML = '';
            this.addProduct();
        }
    },

    // Batch generate
    async batchGenerate() {
        const productItems = document.querySelectorAll('#batchProducts .product-item');
        const items = [];

        productItems.forEach(item => {
            const productId = item.querySelector('.batch-product-id').value;
            const keywords = item.querySelector('.batch-keywords').value;
            const basicInfo = item.querySelector('.batch-basic-info').value;

            if (productId) {
                items.push({
                    product_id: productId,
                    keywords: keywords ? keywords.split(',').map(k => k.trim()) : null,
                    basic_info: basicInfo || null
                });
            }
        });

        if (items.length === 0) {
            this.showNotification('Please add at least one product with ID', 'warning');
            return;
        }

        const resultBox = document.getElementById('batchResult');
        this.setLoading(true);

        try {
            const response = await fetch(`${this.apiUrl}/v1/generate`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify({items})
            });

            const data = await response.json();

            let summaryHtml = `
                <h3>📦 Batch Results</h3>
                <div class="summary-stats">
                    <div class="stat-card">
                        <div class="stat-value">${data.summary.requested}</div>
                        <div class="stat-label">Requested</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" style="color: var(--success);">
                            ${data.summary.enqueued}
                        </div>
                        <div class="stat-label">Enqueued</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" style="color: var(--warning);">
                            ${data.summary.conflicted}
                        </div>
                        <div class="stat-label">Conflicted</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" style="color: var(--danger);">
                            ${data.summary.failed}
                        </div>
                        <div class="stat-label">Failed</div>
                    </div>
                </div>
            `;

            if (data.items && data.items.length > 0) {
                summaryHtml += '<div style="margin-top: 20px;"><h4>Details:</h4>';
                data.items.forEach(item => {
                    const statusColor = item.http_status === 200 ? 'var(--success)' : 'var(--danger)';
                    summaryHtml += `
                        <div style="padding: 10px; margin: 5px 0; background: #f9fafb; 
                                    border-radius: 6px; border-left: 3px solid ${statusColor};">
                            <strong>${item.product_id}</strong> - 
                            ${item.status || item.error || 'Unknown'}
                            ${item.message ? `<br><small style="color: #6b7280;">${item.message}</small>` : ''}
                        </div>
                    `;
                });
                summaryHtml += '</div>';
            }

            summaryHtml += `
                <details style="margin-top: 20px;">
                    <summary style="cursor: pointer; color: var(--primary);">View Response</summary>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                </details>
            `;

            resultBox.innerHTML = summaryHtml;
            resultBox.classList.add('show');
            this.showNotification(`Batch generation: ${data.summary.enqueued} enqueued`, 'success');
        } catch (error) {
            resultBox.innerHTML = `
                <h3 style="color: var(--danger);">❌ Error</h3>
                <p>${error.message}</p>
            `;
            resultBox.classList.add('show');
            this.showNotification('Batch generation failed', 'error');
        } finally {
            this.setLoading(false);
        }
    },

    // Show notification
    showNotification(message, type = 'info') {
        // Simple console log for now, can be replaced with toast notifications
        console.log(`[${type.toUpperCase()}] ${message}`);

        // You can implement a toast notification system here
        // For now, we'll use alert for errors
        if (type === 'error' && !message.includes('Connection')) {
            alert(message);
        }
    }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});
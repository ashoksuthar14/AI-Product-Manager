// Initialize Socket.IO connection
const socket = io();

// Real-time analysis updates
socket.on('analysis_progress', function(data) {
    updateProgressBar(data.progress, data.message);
    console.log(`Progress: ${data.progress}% - ${data.message}`);
});

socket.on('agent_update', function(data) {
    addAgentMessage(data);
    console.log(`Agent Update: ${data.agent} - ${data.type}`);
});

socket.on('analysis_complete', function(data) {
    hideLoading();
    if (data.success) {
        displayFinalAnalysisResults(data);
        showNotification('Analysis completed successfully!', 'success');
    } else {
        showNotification('Analysis failed: ' + data.error, 'error');
    }
});

socket.on('analysis_error', function(data) {
    hideLoading();
    showNotification('Analysis failed: ' + data.error, 'error');
});

socket.on('analysis_started', function(data) {
    showNotification(data.message, 'info');
});

// Main JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize form handling
    initFormHandling();
    
    // Initialize animations
    initAnimations();
}

function initFormHandling() {
    const projectForm = document.getElementById('project-form');
    if (projectForm) {
        projectForm.addEventListener('submit', handleProjectSubmission);
    }
}

async function handleProjectSubmission(e) {
    e.preventDefault();
    
    // Show loading overlay with progress
    showLoadingWithProgress();
    
    // Clear previous results
    clearPreviousResults();
    
    // Get form data
    const formData = new FormData(e.target);
    const projectData = {
        title: formData.get('title'),
        description: formData.get('description'),
        requirements: formData.get('requirements'),
        timeline: formData.get('timeline'),
        budget: formData.get('budget'),
        constraints: formData.get('constraints')
    };
    
    // Start real-time analysis via WebSocket
    socket.emit('start_analysis', { project_data: projectData });
}

function displayFinalAnalysisResults(result) {
    // Show results section
    const resultsSection = document.getElementById('analysis-results');
    if (resultsSection) {
        resultsSection.classList.remove('hidden');
        
        // Display final summary based on actual analysis
        displayActualSummary(result.analysis);
        
        // Display workflow based on actual analysis (including PM overview)
        displayActualWorkflow(result.analysis);
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
}

function displayConversation(conversationLog) {
    // Real-time conversation is now handled by addAgentMessage()
    // This is only called for final conversation summary if needed
    const container = document.getElementById('conversation-container');
    if (!container) return;
    
    // The real conversation is already displayed via real-time updates
    // No need to replace it with static data
}

function createAgentMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'agent-message';
    
    messageDiv.innerHTML = `
        <div class="agent-header">
            <div class="agent-avatar ${message.class}">
                <i class="${message.avatar}"></i>
            </div>
            <div>
                <div class="agent-name">${message.agent}</div>
                <div class="agent-role">${message.type}</div>
            </div>
        </div>
        <div class="agent-content">
            ${message.content}
        </div>
    `;
    
    return messageDiv;
}

function displayActualSummary(analysis) {
    const container = document.getElementById('analysis-summary');
    if (!container || !analysis) return;
    
    // Only show summary if we have actual completed analysis
    const pmData = analysis.product_management || {};
    const devData = analysis.technical_development || {};
    const qaData = analysis.quality_assurance || {};
    const aiData = analysis.ai_engineering || {};
    const pmOverview = analysis.pm_overview;
    
    // Only display summary if we have the final PM overview (meaning analysis is complete)
    if (!pmOverview) {
        container.innerHTML = '<p class="text-center" style="opacity: 0.7;">📊 Analysis summary will appear after all agents complete their work...</p>';
        return;
    }
    
    // Create summary cards based on actual analysis completion
    const summaryCards = [
        {
            icon: 'fas fa-chart-line',
            title: 'Market Analysis',
            value: Object.keys(pmData).length > 0 ? '✅ Completed' : '⏳ Processing',
            color: Object.keys(pmData).length > 0 ? 'var(--primary-blue)' : 'var(--text-secondary)'
        },
        {
            icon: 'fas fa-code',
            title: 'Technical Analysis',
            value: Object.keys(devData).length > 0 ? '✅ Completed' : '⏳ Processing',
            color: Object.keys(devData).length > 0 ? 'var(--primary-blue)' : 'var(--text-secondary)'
        },
        {
            icon: 'fas fa-bug',
            title: 'Quality Analysis',
            value: Object.keys(qaData).length > 0 ? '✅ Completed' : '⏳ Processing',
            color: Object.keys(qaData).length > 0 ? 'var(--primary-blue)' : 'var(--text-secondary)'
        },
        {
            icon: 'fas fa-brain',
            title: 'AI Integration',
            value: Object.keys(aiData).length > 0 ? '✅ Completed' : '⏳ Processing',
            color: Object.keys(aiData).length > 0 ? 'var(--primary-blue)' : 'var(--text-secondary)'
        }
    ];
    
    container.innerHTML = summaryCards.map(card => `
        <div class="summary-card">
            <div class="summary-icon" style="color: ${card.color}">
                <i class="${card.icon}"></i>
            </div>
            <div class="summary-title">${card.title}</div>
            <div class="summary-value" style="color: ${card.color}">${card.value}</div>
        </div>
    `).join('');
}

function displayActualWorkflow(analysis) {
    const container = document.getElementById('project-workflow');
    if (!container || !analysis) return;
    
    // Check if we have PM overview (which means analysis is complete)
    const pmOverview = analysis.pm_overview;
    
    // Only show workflow if we have the final PM overview
    if (!pmOverview) {
        container.innerHTML = '<p class="text-center">Workflow will be generated after Product Manager overview is complete...</p>';
        return;
    }
    
    // Display the PM overview first
    container.innerHTML = `
        <div class="pm-overview-section">
            <h3 style="color: var(--primary-blue); margin-bottom: 1rem;">
                <i class="fas fa-user-tie"></i> Product Manager Overview
            </h3>
            <div class="glass-card" style="margin-bottom: 2rem;">
                <div style="white-space: pre-wrap; line-height: 1.6;">
                    ${pmOverview}
                </div>
            </div>
        </div>
        
        <div class="workflow-section">
            <h3 style="color: var(--primary-blue); margin-bottom: 1rem;">
                <i class="fas fa-tasks"></i> Recommended Project Workflow
            </h3>
            <p class="text-center" style="margin-bottom: 2rem; opacity: 0.8;">
                Based on the comprehensive analysis and team collaboration above
            </p>
        </div>
    `;
    
    // Extract timeline and workflow recommendations from PM overview if available
    // This would be based on the actual content of the PM overview
    // For now, show that the workflow is based on the complete analysis
}

function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.remove('hidden');
    }
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('hidden');
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `flash-message flash-${type}`;
    notification.innerHTML = `
        <i class="fas fa-info-circle"></i>
        <span>${message}</span>
        <button class="flash-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    let container = document.querySelector('.flash-messages');
    if (!container) {
        container = document.createElement('div');
        container.className = 'flash-messages';
        document.body.appendChild(container);
    }
    
    container.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

function initAnimations() {
    // Simple animation initialization
    const cards = document.querySelectorAll('.glass-card, .agent-card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// Real-time analysis functions
function showLoadingWithProgress() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.remove('hidden');
        
        // Add progress bar if not exists
        let progressContainer = overlay.querySelector('.progress-container');
        if (!progressContainer) {
            progressContainer = document.createElement('div');
            progressContainer.className = 'progress-container';
            progressContainer.innerHTML = `
                <div class="progress-bar">
                    <div class="progress-fill" id="progress-fill"></div>
                </div>
                <div class="progress-text" id="progress-text">Starting analysis...</div>
            `;
            overlay.querySelector('.loading-content').appendChild(progressContainer);
        }
    }
}

function updateProgressBar(progress, message) {
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    
    if (progressFill) {
        progressFill.style.width = `${progress}%`;
    }
    
    if (progressText) {
        progressText.textContent = message;
    }
}

function addAgentMessage(data) {
    const container = document.getElementById('conversation-container');
    if (!container) return;
    
    // Show conversation section if hidden
    const resultsSection = document.getElementById('analysis-results');
    if (resultsSection && resultsSection.classList.contains('hidden')) {
        resultsSection.classList.remove('hidden');
    }
    
    const agentClasses = {
        'Product Manager': 'agent-product-manager',
        'Developer': 'agent-developer',
        'QA Engineer': 'agent-qa',
        'AI Engineer': 'agent-ai-engineer'
    };
    
    const agentIcons = {
        'Product Manager': 'fas fa-user-tie',
        'Developer': 'fas fa-code',
        'QA Engineer': 'fas fa-bug',
        'AI Engineer': 'fas fa-brain'
    };
    
    const message = {
        agent: data.agent,
        type: data.type,
        content: data.content,
        avatar: agentIcons[data.agent] || 'fas fa-user',
        class: agentClasses[data.agent] || 'agent-default'
    };
    
    const messageElement = createAgentMessage(message);
    container.appendChild(messageElement);
    
    // Scroll to latest message
    messageElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function clearPreviousResults() {
    const conversationContainer = document.getElementById('conversation-container');
    if (conversationContainer) {
        conversationContainer.innerHTML = '';
    }
    
    const resultsSection = document.getElementById('analysis-results');
    if (resultsSection) {
        resultsSection.classList.add('hidden');
    }
}

// Export functions for global access
window.showNotification = showNotification;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.showLoadingWithProgress = showLoadingWithProgress;
window.updateProgressBar = updateProgressBar;
window.addAgentMessage = addAgentMessage;
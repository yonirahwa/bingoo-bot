// Global state
window.currentUser = {};
window.currentRoom = null;
window.selectedCards = [];
window.wsConnected = false;

// Initialize app
function initApp() {
    setupEventListeners();
    updateBalanceDisplay();
}

function setupEventListeners() {
    // Modal close buttons
    document.querySelectorAll('.close-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const modal = e.target.closest('.modal');
            if (modal) modal.classList.remove('active');
        });
    });
    
    // Click outside modal to close
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });
}

function updateBalanceDisplay() {
    const balance = (window.currentUser.balance || 0).toFixed(2);
    document.getElementById('balanceAmount').textContent = `${balance} ETB`;
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        bottom: 90px;
        left: 50%;
        transform: translateX(-50%);
        background: ${type === 'success' ? '#2ed573' : type === 'error' ? '#ff4757' : '#6c5ce7'};
        color: ${type === 'success' || type === 'error' ? '#fff' : '#fff'};
        padding: 12px 20px;
        border-radius: 8px;
        z-index: 999;
        font-size: 13px;
        max-width: 90%;
        text-align: center;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function showWinnerNotification(won, pattern, amount) {
    const modal = document.createElement('div');
    modal.className = 'winner-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 2000;
    `;
    
    const content = document.createElement('div');
    content.style.cssText = `
        background: ${won ? '#2ed573' : '#ff4757'};
        padding: 40px 20px;
        border-radius: 16px;
        text-align: center;
        color: #fff;
        animation: bounce 0.6s ease;
    `;
    content.innerHTML = `
        <h2 style="font-size: 32px; margin-bottom: 16px;">
            ${won ? '🎉 BINGO! 🎉' : '😢 Game Over'}
        </h2>
        ${won ? `
            <p style="font-size: 18px; margin-bottom: 12px;">You Won!</p>
            <p style="font-size: 14px; margin-bottom: 20px;">Pattern: ${pattern}</p>
            <p style="font-size: 24px; font-weight: bold; margin-bottom: 20px;">+${amount.toFixed(2)} ETB</p>
        ` : `
            <p style="font-size: 16px;">Try again next time!</p>
        `}
        <button style="
            background: #fff;
            color: ${won ? '#2ed573' : '#ff4757'};
            border: none;
            padding: 12px 32px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        " onclick="document.querySelector('.winner-modal').remove(); navigateTo('gamesPage');">
            Continue
        </button>
    `;
    
    modal.appendChild(content);
    document.body.appendChild(modal);
}

// Add animations to style
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(-50%) translateY(20px); opacity: 0; }
        to { transform: translateX(-50%) translateY(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(-50%) translateY(0); opacity: 1; }
        to { transform: translateX(-50%) translateY(20px); opacity: 0; }
    }
    
    @keyframes bounce {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
`;
document.head.appendChild(style);

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', initApp);

// Handle page visibility
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // App went to background
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.close();
        }
    } else {
        // App came to foreground
        if (window.currentRoom && !wsConnected) {
            connectWebSocket(window.currentRoom.id, window.currentUser.id);
        }
    }
});

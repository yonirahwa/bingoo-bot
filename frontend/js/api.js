const API_BASE_URL = 'https://bingoo-bot.onrender.com/api';

// API helper function
async function apiCall(endpoint, method = 'GET', data = null, isFormData = false) {
    const options = {
        method,
        headers: {}
    };
    
    if (!isFormData && data) {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(data);
    } else if (data) {
        options.body = data;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API error');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showNotification(error.message, 'error');
        throw error;
    }
}

// Auth APIs
async function loginUser() {
    try {
        const response = await apiCall('/auth/login', 'POST', {
            telegram_id: window.currentUser.telegram_id,
            first_name: window.currentUser.first_name,
            last_name: window.currentUser.last_name,
            username: window.currentUser.username
        });
        
        window.currentUser.id = response.id;
        window.currentUser.balance = response.balance;
        window.currentUser.bonus_balance = response.bonus_balance;
        
        updateBalanceDisplay();
        loadGameRooms();
    } catch (error) {
        console.error('Login failed:', error);
    }
}

// Games APIs
async function loadGameRooms() {
    try {
        const rooms = await apiCall('/games/rooms');
        displayGameRooms(rooms);
    } catch (error) {
        console.error('Failed to load game rooms:', error);
    }
}

async function generateCards(count = 2) {
    try {
        const response = await apiCall(
            `/games/generate-cards?user_id=${window.currentUser.id}&count=${count}`,
            'POST'
        );
        return response.cards;
    } catch (error) {
        console.error('Failed to generate cards:', error);
    }
}

async function getMyCards() {
    try {
        const cards = await apiCall(`/games/my-cards?user_id=${window.currentUser.id}`);
        return cards;
    } catch (error) {
        console.error('Failed to get cards:', error);
    }
}

async function joinGame(roomId, cardIds) {
    try {
        const response = await apiCall(
            `/games/join-game?user_id=${window.currentUser.id}&room_id=${roomId}`,
            'POST',
            { card_ids: cardIds }
        );
        return response;
    } catch (error) {
        console.error('Failed to join game:', error);
        throw error;
    }
}

async function startGame(roomId) {
    try {
        const response = await apiCall(`/games/start-game/${roomId}`, 'POST');
        return response;
    } catch (error) {
        console.error('Failed to start game:', error);
    }
}

async function markNumber(roomId, number, cardIndex) {
    try {
        const response = await apiCall(
            `/games/mark-number?user_id=${window.currentUser.id}&room_id=${window.currentRoom.id}&number=${number}&card_index=${cardIndex}`,
            'POST'
        );
        return response;
    } catch (error) {
        console.error('Failed to mark number:', error);
    }
}

async function checkWin(roomId, cardIndex) {
    try {
        const response = await apiCall(
            `/games/check-win?user_id=${window.currentUser.id}&room_id=${roomId}&card_index=${cardIndex}`,
            'POST'
        );
        return response;
    } catch (error) {
        console.error('Failed to check win:', error);
    }
}

// Wallet APIs
async function getBalance() {
    try {
        const response = await apiCall(`/wallet/balance?user_id=${window.currentUser.id}`);
        return response;
    } catch (error) {
        console.error('Failed to get balance:', error);
    }
}

async function depositFunds(method, amount, phoneOrAccount) {
    try {
        const response = await apiCall(
            `/wallet/deposit?user_id=${window.currentUser.id}`,
            'POST',
            {
                method,
                amount: parseFloat(amount),
                phone_or_account: phoneOrAccount
            }
        );
        return response;
    } catch (error) {
        console.error('Deposit failed:', error);
        throw error;
    }
}

async function withdrawFunds(amount, method, accountInfo) {
    try {
        const response = await apiCall(
            `/wallet/withdraw?user_id=${window.currentUser.id}`,
            'POST',
            {
                amount: parseFloat(amount),
                method,
                account_info: accountInfo
            }
        );
        return response;
    } catch (error) {
        console.error('Withdrawal failed:', error);
        throw error;
    }
}

async function transferFunds(recipientId, amount) {
    try {
        const response = await apiCall(
            `/wallet/transfer?user_id=${window.currentUser.id}`,
            'POST',
            {
                recipient_id: parseInt(recipientId),
                amount: parseFloat(amount)
            }
        );
        return response;
    } catch (error) {
        console.error('Transfer failed:', error);
        throw error;
    }
}

async function getTransactions(limit = 20) {
    try {
        const response = await apiCall(
            `/wallet/transactions?user_id=${window.currentUser.id}&limit=${limit}`
        );
        return response;
    } catch (error) {
        console.error('Failed to get transactions:', error);
    }
}

// Profile APIs
async function getProfile() {
    try {
        const response = await apiCall(`/profile/?user_id=${window.currentUser.id}`);
        return response;
    } catch (error) {
        console.error('Failed to get profile:', error);
    }
}

async function uploadProfilePhoto(file) {
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await apiCall(
            `/profile/upload-photo?user_id=${window.currentUser.id}`,
            'POST',
            formData,
            true
        );
        return response;
    } catch (error) {
        console.error('Failed to upload photo:', error);
        throw error;
    }
}

async function updateLanguage(language) {
    try {
        const response = await apiCall(
            `/profile/language?user_id=${window.currentUser.id}&language=${language}`,
            'PUT'
        );
        return response;
    } catch (error) {
        console.error('Failed to update language:', error);
    }
}


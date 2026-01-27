// Page navigation
function navigateTo(pageName) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Remove active class from nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Show selected page
    const page = document.getElementById(pageName);
    if (page) {
        page.classList.add('active');
    }
    
    // Add active class to nav item
    const navItem = document.querySelector(`[data-page="${pageName}"]`);
    if (navItem) {
        navItem.classList.add('active');
    }
    
    // Load page-specific data
    switch (pageName) {
        case 'walletPage':
            loadWalletData();
            break;
        case 'profilePage':
            loadProfileData();
            break;
        case 'gamesPage':
            loadGameRooms();
            break;
    }
}

function backToGames() {
    navigateTo('gamesPage');
}

function goToPlayBingo() {
    navigateTo('playBingoPage');
    loadCardsForSelection();
}

async function loadCardsForSelection() {
    try {
        let cards = await getMyCards();
        
        if (!cards || cards.length === 0) {
            cards = await generateCards(2);
        }
        
        displayCardsForSelection(cards);
    } catch (error) {
        console.error('Failed to load cards:', error);
    }
}

function displayCardsForSelection(cards) {
    const grid = document.getElementById('cardsGrid');
    grid.innerHTML = '';
    
    window.selectedCards = [];
    
    cards.forEach((card, index) => {
        const cardDiv = document.createElement('div');
        cardDiv.className = 'card-item';
        cardDiv.textContent = index + 1;
        cardDiv.dataset.cardId = card.id;
        cardDiv.onclick = () => toggleCardSelection(cardDiv);
        grid.appendChild(cardDiv);
    });
    
    updateJoinButton();
}

function toggleCardSelection(cardDiv) {
    const cardId = parseInt(cardDiv.dataset.cardId);
    
    if (cardDiv.classList.contains('selected')) {
        cardDiv.classList.remove('selected');
        window.selectedCards = window.selectedCards.filter(id => id !== cardId);
    } else {
        if (window.selectedCards.length < 2) {
            cardDiv.classList.add('selected');
            window.selectedCards.push(cardId);
        } else {
            showNotification('Maximum 2 cards allowed', 'warning');
        }
    }
    
    updateJoinButton();
}

function updateJoinButton() {
    const joinBtn = document.getElementById('joinBtn');
    joinBtn.disabled = window.selectedCards.length === 0;
}

async function joinRoom() {
    if (!window.currentRoom) {
        showNotification('Please select a room first', 'warning');
        return;
    }
    
    try {
        await joinGame(window.currentRoom.id, window.selectedCards);
        window.currentRoom.current_players++;
        displayGame();
        connectWebSocket(window.currentRoom.id, window.currentUser.id);
    } catch (error) {
        showNotification('Failed to join game', 'error');
    }
}

function displayGameRooms(rooms) {
    const roomsList = document.getElementById('roomsList');
    roomsList.innerHTML = '';
    
    rooms.forEach(room => {
        const roomDiv = document.createElement('div');
        roomDiv.className = 'room-card';
        roomDiv.innerHTML = `
            <div class="room-info">
                <div class="room-name">
                    <span class="stake-badge">${room.stake_amount} ETB</span>
                    ${room.name}
                </div>
                <div class="room-details">
                    <div class="room-detail">
                        <span class="room-detail-icon">👥</span>
                        <span>${room.current_players}/${room.max_players}</span>
                    </div>
                    <div class="room-detail">
                        <span class="room-detail-icon">⏱️</span>
                        <span>${room.status}</span>
                    </div>
                </div>
            </div>
            <button class="btn btn-primary" onclick="selectRoom(${room.id}, '${room.name}', ${room.stake_amount})">Join</button>
        `;
        roomsList.appendChild(roomDiv);
    });
}

function selectRoom(roomId, roomName, stakeAmount) {
    window.currentRoom = { id: roomId, name: roomName, stake_amount: stakeAmount, current_players: 0 };
    goToPlayBingo();
}

function displayGame() {
    navigateTo('gamePage');
    document.getElementById('roomNumber').textContent = window.currentRoom.id;
    document.getElementById('stakeAmount').textContent = window.currentRoom.stake_amount;
    updatePlayerCount(window.currentRoom.current_players);
    startGameTimer();
}

function leaveGame() {
    disconnectWebSocket();
    navigateTo('gamesPage');
}

function startGameTimer() {
    let seconds = 10;
    const timerDiv = document.getElementById('gameTimer');
    
    const interval = setInterval(() => {
        seconds--;
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        timerDiv.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
        
        if (seconds <= 0) {
            clearInterval(interval);
            startCallingNumbers();
        }
    }, 1000);
}

function startCallingNumbers() {
    // Numbers will be called via WebSocket
    showNotification('Game started!', 'success');
}

function markNumberOnAllCards(number) {
    const cardNumbers = document.querySelectorAll('.card-number');
    cardNumbers.forEach(element => {
        if (parseInt(element.textContent) === number) {
            element.classList.add('marked');
        }
    });
}

function displayBingoCards() {
    // This will be called when game starts
    const cardsSection = document.getElementById('bingoCards');
    
    if (window.selectedCards && window.selectedCards.length > 0) {
        // Display selected cards
        generateAndDisplayBingoCards();
    }
}

function generateAndDisplayBingoCards() {
    const cardsSection = document.getElementById('bingoCards');
    cardsSection.innerHTML = '';
    
    // Create sample cards (in real app, fetch from API)
    for (let cardNum = 0; cardNum < window.selectedCards.length; cardNum++) {
        const card = generateBingoCardGrid();
        const cardDiv = document.createElement('div');
        cardDiv.className = 'bingo-card';
        cardDiv.innerHTML = `
            <div style="text-align: center; margin-bottom: 8px; font-size: 12px; color: var(--text-secondary);">
                Card ${cardNum + 1}
            </div>
            <div class="card-numbers">
                ${card.map((num, idx) => `
                    <div class="card-number${num === 0 ? ' free' : ''}" data-number="${num}">
                        ${num === 0 ? 'FREE' : num}
                    </div>
                `).join('')}
            </div>
        `;
        cardsSection.appendChild(cardDiv);
        
        // Add click handlers
        cardDiv.querySelectorAll('.card-number').forEach(element => {
            element.addEventListener('click', function() {
                if (!this.classList.contains('free')) {
                    this.classList.toggle('marked');
                    markNumber(window.currentRoom.id, parseInt(this.textContent), cardNum);
                }
            });
        });
    }
}

function generateBingoCardGrid() {
    const card = [];
    const ranges = [[1, 15], [16, 30], [31, 45], [46, 60], [61, 75]];
    
    for (let col = 0; col < 5; col++) {
        const [min, max] = ranges[col];
        const numbers = [];
        while (numbers.length < 5) {
            const num = Math.floor(Math.random() * (max - min + 1)) + min;
            if (!numbers.includes(num)) numbers.push(num);
        }
        
        for (let row = 0; row < 5; row++) {
            card[row * 5 + col] = numbers[row];
        }
    }
    
    card[12] = 0; // Center free space
    return card;
}

function updatePlayerCount(count) {
    document.getElementById('playerCount').textContent = count;
}

async function checkBingo() {
    if (!window.currentRoom) return;
    
    for (let i = 0; i < window.selectedCards.length; i++) {
        const result = await checkWin(window.currentRoom.id, i);
        
        if (result.has_won) {
            showWinnerNotification(true, result.pattern, 1000);
            return;
        }
    }
    
    showNotification('No bingo yet!', 'info');
}

async function loadWalletData() {
    try {
        const balance = await getBalance();
        const transactions = await getTransactions();
        
        document.getElementById('walletBalance').textContent = `${balance.balance.toFixed(2)} ETB`;
        document.getElementById('bonusBalance').textContent = balance.bonus_balance.toFixed(2);
        
        displayTransactions(transactions);
    } catch (error) {
        console.error('Failed to load wallet:', error);
    }
}

function displayTransactions(transactions) {
    const list = document.getElementById('transactionsList');
    list.innerHTML = '';
    
    if (!transactions || transactions.length === 0) {
        list.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No transactions yet</p>';
        return;
    }
    
    transactions.forEach(tx => {
        const txDiv = document.createElement('div');
        txDiv.className = 'transaction-item';
        
        const amountClass = tx.type === 'withdraw' ? 'withdraw' : '';
        const amountPrefix = tx.type === 'withdraw' || tx.type === 'game_loss' ? '-' : '+';
        
        txDiv.innerHTML = `
            <div class="transaction-left">
                <div class="transaction-type">${tx.type}</div>
                <div class="transaction-date">${new Date(tx.created_at).toLocaleDateString()}</div>
            </div>
            <div class="transaction-amount ${amountClass}">${amountPrefix}${tx.amount.toFixed(2)} ETB</div>
        `;
        list.appendChild(txDiv);
    });
}

// Wallet functions
function openDeposit() {
    document.getElementById('depositModal').classList.add('active');
}

function closeDeposit() {
    document.getElementById('depositModal').classList.remove('active');
}

function openWithdraw() {
    document.getElementById('withdrawModal').classList.add('active');
}

function closeWithdraw() {
    document.getElementById('withdrawModal').classList.remove('active');
}

function openTransfer() {
    document.getElementById('transferModal').classList.add('active');
}

function closeTransfer() {
    document.getElementById('transferModal').classList.remove('active');
}

function selectPaymentMethod(method) {
    // Store selected method and show input
    window.selectedPaymentMethod = method;
}

async function submitDeposit() {
    const amount = document.getElementById('depositAmount').value;
    const phone = document.getElementById('depositPhone').value;
    
    if (!amount || !phone) {
        showNotification('Please fill all fields', 'warning');
        return;
    }
    
    try {
        const result = await depositFunds(window.selectedPaymentMethod, amount, phone);
        showNotification('Deposit initiated', 'success');
        closeDeposit();
        setTimeout(() => loadWalletData(), 1000);
    } catch (error) {
        showNotification('Deposit failed', 'error');
    }
}

async function submitWithdraw() {
    const amount = document.getElementById('withdrawAmount').value;
    const method = document.getElementById('withdrawMethod').value;
    const account = document.getElementById('withdrawAccount').value;
    
    if (!amount || !method || !account) {
        showNotification('Please fill all fields', 'warning');
        return;
    }
    
    try {
        const result = await withdrawFunds(amount, method, { account });
        showNotification('Withdrawal request submitted', 'success');
        closeWithdraw();
        setTimeout(() => loadWalletData(), 1000);
    } catch (error) {
        showNotification('Withdrawal failed', 'error');
    }
}

async function submitTransfer() {
    const recipientId = document.getElementById('recipientId').value;
    const amount = document.getElementById('transferAmount').value;
    
    if (!recipientId || !amount) {
        showNotification('Please fill all fields', 'warning');
        return;
    }
    
    try {
        const result = await transferFunds(recipientId, amount);
        showNotification('Transfer successful', 'success');
        closeTransfer();
        setTimeout(() => {
            loadWalletData();
            updateBalanceDisplay();
        }, 1000);
    } catch (error) {
        showNotification('Transfer failed', 'error');
    }
}

// Profile functions
async function loadProfileData() {
    try {
        const profile = await getProfile();
        displayProfile(profile);
    } catch (error) {
        console.error('Failed to load profile:', error);
    }
}

function displayProfile(profile) {
    document.getElementById('profileName').textContent = `${profile.first_name || ''} ${profile.last_name || ''}`.trim();
    document.getElementById('profileUsername').textContent = profile.username || '-';
    document.getElementById('profileJoined').textContent = new Date(profile.created_at).toLocaleDateString();
    document.getElementById('languageSelect').value = profile.language;
    
    if (profile.photo_url) {
        document.getElementById('profilePhoto').src = profile.photo_url;
    }
}

function triggerPhotoUpload() {
    document.getElementById('photoUpload').click();
}

async function uploadPhoto(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    try {
        const result = await uploadProfilePhoto(file);
        showNotification('Photo uploaded', 'success');
        document.getElementById('profilePhoto').src = result.photo_url;
    } catch (error) {
        showNotification('Photo upload failed', 'error');
    }
}

async function changeLanguage() {
    const language = document.getElementById('languageSelect').value;
    try {
        await updateLanguage(language);
        showNotification('Language updated', 'success');
    } catch (error) {
        showNotification('Failed to update language', 'error');
    }
}

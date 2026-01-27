// Telegram Web App integration
let tg = window.Telegram.WebApp;

// Initialize Telegram Web App
function initTelegram() {
    tg.ready();
    tg.expand();
    
    // Get user data
    const user = tg.initDataUnsafe.user;
    if (user) {
        window.currentUser = {
            telegram_id: user.id.toString(),
            first_name: user.first_name,
            last_name: user.last_name,
            username: user.username,
            is_premium: user.is_premium
        };
        
        loginUser();
    }
}

// Request user to close bot
function closeApp() {
    tg.close();
}

// Share referral
function shareReferral() {
    const shareText = `🎉 Join me on Bingo Bot and win ETB! Get +10 ETB bonus on signup!`;
    tg.openTelegramLink(`https://t.me/share/url?url=${window.location.href}&text=${encodeURIComponent(shareText)}`);
}

// Open external links
function openSupport() {
    tg.openTelegramLink('https://t.me/bingobot_support');
}

function joinChannel() {
    tg.openTelegramLink('https://t.me/bingobot_channel');
}

// Initialize on load
window.addEventListener('load', initTelegram);

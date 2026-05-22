async function sendMessage() {

    const input = document.getElementById('chatInput');
    const messages = document.getElementById('chatMessages');

    const question = input.value.trim();

    if (!question) {
        return;
    }

    // Add user message
    const userDiv = document.createElement('div');
    userDiv.className = 'user-message';
    userDiv.innerText = question;

    messages.appendChild(userDiv);

    // Clear input
    input.value = '';

    // Scroll
    messages.scrollTop = messages.scrollHeight;

    // Add loading message
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'bot-message';
    loadingDiv.innerText = 'Typing...';

    messages.appendChild(loadingDiv);

    try {

        const response = await fetch('/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: question
            })
        });

        const data = await response.json();

        // Remove loading
        loadingDiv.remove();

        const botDiv = document.createElement('div');
        botDiv.className = 'bot-message';

        botDiv.innerText = data.reply;

        messages.appendChild(botDiv);

        messages.scrollTop = messages.scrollHeight;

    } catch (error) {

        loadingDiv.remove();

        const errorDiv = document.createElement('div');
        errorDiv.className = 'bot-message';

        errorDiv.innerText = 'Chatbot unavailable right now.';

        messages.appendChild(errorDiv);
    }
}


function handleChatEnter(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}
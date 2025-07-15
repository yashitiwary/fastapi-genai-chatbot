// Chat functionality with multiple endpoint options
let isLoading = false;

async function sendMessage() {
    const userInput = document.getElementById("user-input").value.trim();
    const chatBox = document.getElementById("chat-box");
    
    // Check if input is empty
    if (!userInput) {
        return;
    }
    
    // Check if already loading
    if (isLoading) {
        return;
    }
    
    // Add user message to chat
    addMessage("You", userInput, "user");
    
    // Clear input and disable it
    document.getElementById("user-input").value = "";
    document.getElementById("user-input").disabled = true;
    isLoading = true;
    
    // Show loading indicator
    const loadingId = addMessage("Bot", "Thinking...", "bot loading");
    
    try {
        // Try Hugging Face endpoint first
        let response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userInput })
        });
        
        let data = await response.json();
        
        // If Hugging Face fails, try simple chatbot
        if (!response.ok || data.response.includes("Error:")) {
            console.log("Hugging Face failed, trying simple chatbot...");
            response = await fetch("/chat-simple", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: userInput })
            });
            data = await response.json();
        }
        
        // Remove loading message
        removeMessage(loadingId);
        
        // Add bot response
        addMessage("Bot", data.response, "bot");
        
    } catch (error) {
        console.error("Error:", error);
        
        // Remove loading message
        removeMessage(loadingId);
        
        // Add error message
        addMessage("Bot", "Sorry, I'm having trouble responding right now. Please try again.", "bot error");
    }
    
    // Re-enable input
    document.getElementById("user-input").disabled = false;
    document.getElementById("user-input").focus();
    isLoading = false;
}

function addMessage(sender, message, className = "") {
    const chatBox = document.getElementById("chat-box");
    const messageId = "msg-" + Date.now();
    
    const messageDiv = document.createElement("div");
    messageDiv.id = messageId;
    messageDiv.className = `message ${className}`;
    messageDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
    
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    
    return messageId;
}

function removeMessage(messageId) {
    const message = document.getElementById(messageId);
    if (message) {
        message.remove();
    }
}

// Handle Enter key press
document.getElementById("user-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});

// Auto-focus on input when page loads
document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("user-input").focus();
});

// Optional: Add some welcome message
document.addEventListener("DOMContentLoaded", function() {
    setTimeout(() => {
        addMessage("Bot", "Hello! I'm your chatbot. How can I help you today?", "bot welcome");
    }, 500);
});

// Optional: Test endpoints function (can be called from console)
async function testEndpoints() {
    console.log("Testing endpoints...");
    
    // Test debug endpoint
    try {
        const debugResponse = await fetch("/debug");
        const debugData = await debugResponse.json();
        console.log("Debug endpoint:", debugData);
    } catch (error) {
        console.error("Debug endpoint error:", error);
    }
    
    // Test Hugging Face endpoint
    try {
        const hfResponse = await fetch("/test-hf");
        const hfData = await hfResponse.json();
        console.log("Hugging Face test:", hfData);
    } catch (error) {
        console.error("Hugging Face test error:", error);
    }
    
    // Test simple chatbot
    try {
        const simpleResponse = await fetch("/chat-simple", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: "Hello test" })
        });
        const simpleData = await simpleResponse.json();
        console.log("Simple chatbot test:", simpleData);
    } catch (error) {
        console.error("Simple chatbot test error:", error);
    }
}
<!DOCTYPE html>
<meta name="viewport" content="width=device-width, initial-scale=1">
<html lang="en">
<head>
    <meta charset="UTF-8">
	<meta name="description" content="Engage with our advanced AI chat platform. Interactive, intelligent conversations with our AI models for a seamless user experience." />
	<meta name="robots" content="index, follow" />
	<meta name="keywords" content="AI, artificial intelligence, chat platform, conversational AI, chatbots, chat with coding models, 7b, 13b, ai models, chat with ai for free, Hugging Face, HuggingFace models chat, remotely chat with huggingface models" />
	<link rel="canonical" href="https://lollms-unreal.com/ai-chat.php" />	

	<meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat UI</title>
    <style>
        /* Your CSS styles here */
    </style>
</head>


<body>
    <img src="chat-interface.png" alt="Interactive AI chat interface" class="seo-image">
    <div id="sidebar">
        <div class="logo">
            <a href="#"><img src="logo.png" alt="Logo"></a> <!-- Replace logo.png with your actual logo path -->
        </div>
		
	<ul class="session-links">
		<li><a href="#session1">Chat Sessions</a></li>
		<!-- More sessions can be added here -->
	</ul>

	<button id="newVocalButton" onclick="speak()">Speak</button>
	<button id="newSessionButton" onclick="saveContent()">Save Session</button>
	<!-- Somewhere in your ai-chat.php or a relevant HTML file -->
	
	<select id="voice-selector" onchange="updateVoiceId()">
		<option value="21m00Tcm4TlvDq8ikWAM">Rachel</option>
		<option value="U5lEpYCOIlBn1qclWNEQ">Selena Voice</option>
		<option value="PEaM0YGA7URKoynVgX77">Kat's Voice</option>
		<option value="huP6KjQlkl0lTxjHoUZS">Sarah Silverman Voice</option>
		<option value="7iGRurZMcszUlmze8MFc">My Real Voice Cloned</option>
		
		<!-- more voices -->
	</select>

<script>
function updateVoiceId() {
    var voiceId = document.getElementById('voice-selector').value;
    document.getElementById('voice-id-input').value = voiceId;
}

</script>

<?php
include 'db_connection.php'; // Ensure this points to your actual database connection script

try {
    $stmt = $pdo->query("SELECT session_id, created_at FROM sessions ORDER BY created_at DESC");
    echo "<ul class='session-list'>";
    while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
        echo "<li><a href='#' data-session-id='{$row['session_id']}'>Session from {$row['created_at']}</a></li>";
    }
    echo "</ul>";
} catch (PDOException $e) {
    echo "Error: " . $e->getMessage();
}
?>

<script>
document.getElementById('newSessionButton').addEventListener('click', function() {
    // Get the conversation data from your application
    var conversationData = document.getElementById('conversation').innerText; // or .innerHTML if you have HTML content

    // Prepare the data to send in a POST request
    var formData = new FormData();
    formData.append('save_session', true);
    formData.append('conversation_data', conversationData);

    // Create the AJAX request to the PHP script
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'saveSession.php', true);
    xhr.onload = function () {
        // Check if the request was successful
        if (xhr.status >= 200 && xhr.status < 300) {
            // Handle success, perhaps alerting the user or updating the UI
            console.log('Session saved:', this.responseText);
            alert('New session saved successfully!');
        } else {
            // Handle errors here
            console.error('The request failed!');
        }
    };
    xhr.onerror = function () {
        console.error('The request failed!');
    };

    // Send the request with the form data
    xhr.send(formData);
});

</script>

	<div class="dropdown">
	  <button class="dropbtn">Model Selection (Exllama2)</button>
	  <div class="dropdown-content">
		<a href="#">Dolphin 7B GPTQ</a>
		<a href="#" class="colorText">XwinCoder 13B GPTQ</a>
		<a href="#" class="colorText">Mistral 7B GPTQ</a>
		<a href="#" class="colorText">WizardCoder 15B GPTQ</a>
	  </div>
	</div>


        <!-- Additional sidebar content here -->
    </div>
    <div id="main">

		<button id="sidebarToggle" class="hamburger-button" onclick="toggleSidebar()">&#9776;</button>

        <div class="content">
            <!-- Main content goes here -->
            <div id="loading-overlay" style="display: none;">
    <div class="loading-circle"></div>
</div>

<div id="chat-container">
<div id="conversation">
		<!-- Your conversation data will be here -->
    <div id="message-container"></div>
	
</div>
    <input type="text" id="message-input">
    <input type="text" id="temperature-input" placeholder="Temperature" value="0.1">
	<input type="number" id="n-predicts-input" placeholder="Number of Predictions" value="1">
    <button id="send-button">Send</button>
</div>
<form>
<label>Select a file:</label>
<input type="file" id="fileInput" accept=".txt, .js, .py">
</form>
        </div>
    </div>
</body>
</html>


<script>
        document.getElementById('fileInput').addEventListener('change', function () {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (event) {
                    // Process the file content (event.target.result) or send it to your AI model
                    console.log(event.target.result);
                };
                reader.readAsText(file);
            }
        });
		
var content = document.getElementById('message-container').innerHTML;

function applyInlineStyles(element) {
    const computedStyle = window.getComputedStyle(element);
    for (let i = 0; i < computedStyle.length; i++) {
        const propName = computedStyle[i];
        element.style[propName] = computedStyle.getPropertyValue(propName);
    }
}

// Example usage

function saveContent() {
    var htmlContent = document.getElementById('message-container').innerHTML; // or other input fields
    console.log(htmlContent); // Check what's being sent

    fetch('saveContent.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'html_content=' + encodeURIComponent(htmlContent)
    })
    .then(response => response.text())
    .then(data => {
        console.log('Server response:', data);
    })
    .catch(error => console.error('Error:', error));
}


		
    </script> 
		
</body>
</html>
<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $content = $_POST['content'] ?? '';

    // Sanitize the HTML content
    $sanitizedContent = htmlspecialchars($content, ENT_QUOTES, 'UTF-8');

    // Optionally, if you want to allow certain HTML tags, use a library like HTMLPurifier
    // http://htmlpurifier.org/

    // Assuming PDO is used for database connection
    $sql = "INSERT INTO your_table (html_content) VALUES (:content)";
    $stmt = $pdo->prepare($sql);
    $stmt->execute(['content' => $sanitizedContent]);

    echo "Content saved successfully!";
}
?>

</div>
<style type="text/css">


select#voice-selector {
    background-color: #23395d;
    color: white;
    padding: 5px;
	position: relative;
    bottom: 10px;
    top: -5px;
	left: 16px;
}

.seo-image {
    position: absolute;
    width: 1px;
    height: 1px;
    margin: -1px;
    padding: 0;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    border: 0;
}

/* Hide sidebar by default in portrait orientation */
@media (orientation: portrait) {
    #sidebar {
        left: -375px; /* Adjust as per your sidebar's width */
    }
    #main {
        margin-left: 0;
    }
}

/* Show sidebar in landscape orientation */
@media (orientation: landscape) {
    #sidebar {
        left: 0;
    }
    #main {
        margin-left: 375px; /* Adjust as per your sidebar's width */
    }
}

.session-list, .session-links {
    list-style: none; /* Removes bullet points */
    padding: 0; /* Removes padding */
    margin: 0; /* Removes margin */
    background-color: #f8f8f8; /* Sets a light background for the list */
    width: 100%; /* Sets the width of the list to full container width */
    box-shadow: 0 2px 5px rgba(0,0,0,0.1); /* Optional: adds a subtle shadow for depth */
}

.session-list li, .session-links li {
    border-bottom: 1px solid #ddd; /* Adds a separator between items */
}

.session-list a, .session-links a {
    display: block; /* Makes the link fill the entire list item */
    color: #333; /* Sets text color */
    padding: 10px 20px; /* Adds padding for touch friendliness */
    text-decoration: none; /* Removes underline from links */
    transition: background-color 0.3s; /* Smooth transition for hover effect */
}

.session-list a:hover, .session-list a:focus, .session-links a:hover, .session-links a:focus {
    background-color: #e9e9e9; /* Changes background on hover/focus */
}

#newSessionButton, #newVocalButton {
  background-color: #23395d;
  color: white;
  border: none;
  padding: 10px 20px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
  margin: 4px 2px;
  cursor: pointer;
  position: relative;
  left: 16px;
  bottom: 5px;
}

.colorText a
{
	color: black !important;
}

/* Style The Dropdown Button */
.dropbtn {
  background-color: #23395d;
  color: white;
  padding: 16px;
  font-size: 16px;
  border: none;
  cursor: pointer;
  left: 16px;
  position: relative;
  top: 10px;
}

/* The Container <div> - Needed To Position The Dropdown Content */
.dropdown {
  position: relative;
  display: inline-block;
}

/* Dropdown Content (Hidden By Default) */
.dropdown-content {
  display: none;
  position: absolute;
  background-color: #23395d;
  min-width: 160px;
  box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
  z-index: 1;
  left: 16px;
}

/* Links Inside The Dropdown */
.dropdown-content a {
  color: grey;
  padding: 12px 16px;
  text-decoration: none;
  display: block;
}

/* Change Color Of Dropdown Links On Hover */
.dropdown-content a:hover {background-color: #152238}

/* Show The Dropdown Menu On Hover */
.dropdown:hover .dropdown-content {
  display: block;
}

/* Change The Background Color Of The Dropdown Button When The Dropdown Content Is Shown */
.dropdown:hover .dropbtn {
  background-color: #23395d;
}



.session-links {
    list-style: none;
    padding: 0;
    margin: 10px 0;
}

.session-links li a {
    display: block;
    padding: 10px;
    color: white;
    text-decoration: none;
    background-color: #555;
    border-bottom: 1px solid #777;
}

.session-links li a:hover, .session-links li a:focus {
    background-color: #777;
}


.hamburger-button {
    position: fixed;
    top: 20px;
    left: 20px;
    z-index: 1001;
    cursor: pointer;
    padding: 10px 12px;
    border: none;
    background-color: #333;
    color: white;
    font-size: 24px;
}

    /* styles.css */
body, html {
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;
}

/* Horizontal */
@media (max-width: 768px) {
    #sidebar {
        width: 375px !important;
        position: fixed;
        height: 100%;
        background: #333;
        color: white;
        transition: left 0.3s ease;
        overflow: auto;
        left: -375px !important;
    }
	
	.hamburger-button{
	display: block;
	}
}

/* Vertical */
@media (max-width: 480px) {
	.hamburger-button{
	display: none;
	}
}

#sidebar {
    width: 260px;
    position: fixed;
    left: -260px; /* Start offscreen */
    height: 100%;
    background: #333;
    color: white;
    transition: left 0.3s ease;
    overflow: auto;
}

#hamburger {
    cursor: pointer;
    padding: 15px 20px;
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    height: 30px;
    background: transparent;
    border: none;
    z-index: 1000;
}

#hamburger div {
    height: 3px;
    background: black;
    margin: 2px 0;
    transition: all 0.3s ease;
}


#main {
    transition: margin-left 0.3s ease;
    padding: 1em;
    margin-left: 0;
}

.logo img {
    display: block;
    padding: 10px;
    width: 100%;
    height: auto;
}

.content {
    margin-top: 20px;
}


#loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000; /* Ensure it's above other content */
}

.loading-circle {
    border: 5px solid #f3f3f3;
    border-top: 5px solid #3498db; /* Blue */
    border-radius: 50%;
    width: 50px;
    height: 50px;
    animation: spin 2s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

body {
    background-color: #1a1a1a; /* Dark background */
    color: #fff;
    font-family: 'Arial', sans-serif;
    margin: 0;
    padding: 0;
}

#chat-container {
    display: flex;
    flex-direction: column;
    max-width: 800px;
    margin: auto;
    height: 90vh;
}

#message-container, #conversation {
    flex-grow: 1;
    padding: 20px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

#chat-container {
    display: flex;
    flex-direction: column;
    padding: 10px;
    height: 90vh; /* Adjust based on your design */
    overflow-y: auto; /* Allows scrolling within the container */
}

#conversation {
    flex-grow: 1;
}

.message {
    max-width: 70%;
    padding: 10px;
    border-radius: 20px;
    color: #fff;
    margin-bottom: 8px; /* Ensures spacing between messages */
}

.user-message {
    background-color: #1c2e4a; /* Dark blue */
    align-self: flex-end; /* Aligns user messages to the right */
    margin-left: auto; /* Ensures alignment to the right */
}

.ai-message {
    background-color: #152238; /* Even darker blue */
    align-self: flex-start; /* Aligns AI messages to the left */
}



#message-input {
    padding: 10px;
    margin: 10px;
    border-radius: 20px;
    border: none;
    outline: none;
    font-size: 1em;
}

#send-button {
    padding: 10px 20px;
    border-radius: 20px;
    border: none;
    background-color: #23395d; /* blue */
    color: #fff;
    font-size: 1em;
    cursor: pointer;
    margin: 10px;
}

</style>

<script src="https://cdn.socket.io/4.3.2/socket.io.min.js" crossorigin="anonymous"></script>

<script>

document.addEventListener('DOMContentLoaded', function() {
    var sidebar = document.getElementById('sidebar');
    var main = document.getElementById('main');

    function handleOrientationChange() {
        if (window.matchMedia("(orientation: portrait)").matches) {
            // If the orientation is portrait, hide the sidebar
            sidebar.style.left = '-375px'; // Adjust as per your sidebar's width
            main.style.marginLeft = '0';
        } else {
            // If the orientation is landscape, you can show the sidebar or leave it as is
            // Uncomment below code if you want to automatically show the sidebar in landscape
            // sidebar.style.left = '0';
            // main.style.marginLeft = '375px'; // Adjust as per your sidebar's width
        }
    }

    // Listen for orientation change
    window.addEventListener('orientationchange', handleOrientationChange);
    // Also listen for window resize events
    window.addEventListener('resize', handleOrientationChange);

    // Initial check
    handleOrientationChange();
});

// script.js
document.addEventListener('click', function(e) {
    const isDropdownButton = e.target.matches("[data-dropdown-button]");
    if (!isDropdownButton && e.target.closest('[data-dropdown]') != null) return;

    let currentDropdown;
    if (isDropdownButton) {
        currentDropdown = e.target.closest('[data-dropdown]');
        currentDropdown.classList.toggle('active');
    }

    document.querySelectorAll("[data-dropdown].active").forEach(dropdown => {
        if (dropdown === currentDropdown) return;
        dropdown.classList.remove('active');
    });
});

function toggleSidebar() {
    if (window.innerWidth <= 768) { // Checks if the viewport width is 768px or less
        var sidebar = document.getElementById('sidebar');
		var main = document.getElementById('main');

        if (sidebar.style.left === '-375px') {
            sidebar.style.left = '0px';  // Show sidebar
			main.style.marginLeft = '0'; 
        } else {
            sidebar.style.left = '-375px';  // Hide sidebar
			main.style.marginLeft = '260px'; 
        }
    } else {
        // Optionally, handle the case for wider screens or do nothing
        console.log("Sidebar toggle is disabled for wider screens.");
    }
}

function toggleSidebar() {
    var sidebar = document.getElementById('sidebar');
	var main = document.getElementById('main');

	if (sidebar.style.left === '-375px') {
		sidebar.style.left = '0px';  // Show sidebar
		main.style.marginLeft = '375px'; // Make sure this matches the sidebar's width
	} else {
		sidebar.style.left = '-375px';  // Hide sidebar
		main.style.marginLeft = '0'; // Reset main content margin
	}

}

// Establish a WebSocket connection with the server
const socket = io.connect('https://lollms.a.pinggy.link');

// Utilize the Send button and message input
const sendButton = document.getElementById('send-button');
const messageInput = document.getElementById('message-input');
const temperatureInput = document.getElementById('temperature-input');
const nPredictsInput = document.getElementById('n-predicts-input'); // Get the n_predicts input
const messageContainer = document.getElementById('message-container');

// Personality Management System
function applyPersona(text) {
    // Define rules for the persona
    const rules = [
        { pattern: /\b(I'm)\b/g, replacement: "I am" },
        { pattern: /\b(can't)\b/g, replacement: "cannot" },
        // Add more rules to fit the persona
    ];

    // Apply each rule to the text
    rules.forEach(rule => {
        text = text.replace(rule.pattern, rule.replacement);
    });

    return text;
}

// Function to append messages to the UI
function appendMessage(text, sender = 'user') {
    // Show the loading overlay
    document.getElementById('loading-overlay').style.display = 'flex';

    // Process the message here (e.g., sending it to the server, waiting for a response)

    // After processing is done (you might need this in a callback or promise resolution)
  

    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    if (sender === 'user') {
        messageDiv.classList.add('user-message');
    } else {
        messageDiv.classList.add('ai-message');
    }
    messageDiv.textContent = text;
    messageContainer.appendChild(messageDiv);
}

sendButton.addEventListener('click', () => {
    const messageText = messageInput.value;
    const temperature = parseFloat(temperatureInput.value);
    const nPredicts = parseInt(nPredictsInput.value, 100);
    const validNPredicts = isNaN(nPredicts) ? 100 : nPredicts;

    // Add a check for empty input
if (messageText.trim() === '') {
        alert('Please enter a message before sending.');
        return;
    }

    appendMessage(messageText, 'user');
    socket.emit('generate_text', {
        prompt: messageText,
        temperature: temperature,
        n_predicts: validNPredicts
    });
    messageInput.value = '';
});

function addPositiveSpin(text) {
    // Simple rules to tweak phrases for a positive spin
    const positivityRules = [
        { pattern: /a bit down/g, replacement: "looking forward to brighter days" },
        { pattern: /pretty down/g, replacement: "getting ready for some good times ahead" },
        { pattern: /\bdown\b/g, replacement: "hopeful" },
        // Add more rules as needed
    ];

    // Apply each rule to the text
    positivityRules.forEach(rule => {
        text = text.replace(rule.pattern, rule.replacement);
    });

    return text;
}

function parisHiltonify(text) {
    // Define basic rules and phrases to inject Paris Hilton's personality
    const phrases = [
        "That's hot. 💃✨",
        "Loves it. 😄",
        "Fabulous!",
        // Add more phrases or sentences that fit Paris Hilton's style
    ];

    // Randomly insert Paris Hilton phrases for a fun touch
    if (Math.random() < 0.5) { // Adjust probability as needed
        const randomPhrase = phrases[Math.floor(Math.random() * phrases.length)];
        text += " " + randomPhrase;
    }

    // Specific word replacements for glamour and confidence
    text = text.replace(/\bcool\b/g, "fabulous");
    text = text.replace(/\bfriends\b/g, "besties");
    text = text.replace(/\bparty\b/g, "fabulous party");
    
    // Add more replacements and modifications here based on the personality traits

    return text;
}


// Existing socket event handlers...

let accumulatedText = '';
let timeoutId = null;

socket.on('text_chunk', (data) => {
  clearTimeout(timeoutId);  // Clear existing timeout
  accumulatedText += data.chunk;  // Accumulate the chunk

  
// Set a new timeout
// When receiving the complete AI response
// Assuming this is where you finalize and display the AI response
timeoutId = setTimeout(() => {
    const personalizedText = applyPersona(accumulatedText); // Existing personalization
    const parisText = parisHiltonify(personalizedText); // Paris Hilton personality
    appendMessage(parisText, 'ai'); // Display the modified text
    document.getElementById('loading-overlay').style.display = 'none';
    accumulatedText = '';  // Reset for the next message
}, 5000);

});

document.querySelectorAll('.session-links a').forEach(link => {
    link.addEventListener('click', function(event) {
        event.preventDefault();
        const sessionId = this.getAttribute('href').substring(1); // Remove '#' from href
        loadSessionData(sessionId);
    });
});

function loadSessionData(sessionId) {
    console.log("Loading data for session", sessionId);
    // Implementation depends on how you store and retrieve session data
}


// Additional socket events (connect, disconnect) as needed
socket.on('connect', () => {
    console.log('Connected to the server');
});

socket.on('disconnect', () => {
    console.log('Disconnected from the server');
});


document.addEventListener('DOMContentLoaded', function() {
    const sessionLinks = document.querySelectorAll('.session-list a');

    sessionLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            var sessionId = this.getAttribute('data-session-id');
            fetchSessionData(sessionId);
        });
    });
});

function fetchSessionData(sessionId) {
    fetch('loadSession.php?session_id=' + sessionId)
    .then(response => response.text())
    .then(data => {
        // Assuming that 'data' is already sanitized HTML content from the server
        document.getElementById('message-container').innerHTML = data; // Display the session data in your message container
		//document.getElementById('message-container').innerHTML = '<div class="message user-message">Static test message</div>';

	})
    .catch(error => console.error('Error loading the session:', error));
}

</script>

<?php
// Database configuration
$dbHost = "localhost";
$dbUsername = "waynecoo_Ai_framework";
$dbPassword = "asdf123";
$dbName = "waynecoo_ai_db";

// Create connection using PDO
try {
    $db = new PDO("mysql:host=$dbHost;dbname=$dbName", $dbUsername, $dbPassword);
    // set the PDO error mode to exception
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    echo "Connected successfully"; 
	//echo 'Server IP Address: ' . $_SERVER['SERVER_ADDR'];

} catch(PDOException $e) {
    echo "Connection failed: " . $e->getMessage();
}
?>

<style>
.audioStuff, #status
{
display: none;
}
</style>

<label class="audioStuff" for="api-key-input">API Key:</label><br>
<input class="audioStuff" type="password" id="azk-data-input" value="bc3f6fab1c2fb9c92c55ae23a66adadb"><br>  <!-- replace with your api key -->

<label class="audioStuff" for="voice-id-input">Voice ID:</label><br>
<input class="audioStuff" type="text" id="voice-id-input" value="21m00Tcm4TlvDq8ikWAM"><br>

<label class="audioStuff" for="text-input">Text:</label><br>
<input class="audioStuff" type="text" id="text-input" value="Hello" placeholder="Type something..."><br>
<p id="status"></p>
<script>
function copyLastAIMessageToTextbox() {
    // Get all elements with the class 'ai-message'
    var aiMessages = document.querySelectorAll('.message.ai-message');
    if (aiMessages.length > 0) {
        // Get the last message
        var lastMessage = aiMessages[aiMessages.length - 1].textContent;

        // Set the text of the textbox
        document.getElementById('text-input').value = lastMessage;
    }
}


function speak() {

	copyLastAIMessageToTextbox();

    const status = document.getElementById('status');
    status.innerText = "Speak Pressed: ";

    const text = document.getElementById('text-input').value;
    const voiceId = document.getElementById('voice-id-input').value;
    const arkonster = document.getElementById('azk-data-input').value;

    status.innerText += "\n"+text;

    const headers = new Headers();
    headers.append('Accept', 'audio/mpeg');
    headers.append('xi-api-key', arkonster);
    headers.append('Content-Type', 'application/json');

    const body = JSON.stringify({
        text: text,
        model_id: 'eleven_monolingual_v1',
        voice_settings: {
            stability: 0.5,
            similarity_boost: 0.5
        }
    });

    document.getElementById('status').innerText += '\nProcessing...';

    fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voiceId}/stream`, {
        method: 'POST',
        headers: headers,
        body: body
    })
    .then(response => {
        if (response.ok) {
            status.innerText += '\nSpeech successfully generated!';
            return response.blob();
        } else {
            throw new Error('Error: ' + response.statusText);
        }
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const audio = new Audio(url);
        audio.play();
        audio.onended = () => {
            status.innerText += '\nAudio has finished playing!';
        };
    })
    .catch(error => {
        console.error('Error:', error);
        status.innerText += '\nError: ' + error.message;
    });
}
</script>

</body>
</html>

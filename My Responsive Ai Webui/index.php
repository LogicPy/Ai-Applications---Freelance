<!DOCTYPE html>
<meta name="viewport" content="width=device-width, initial-scale=1">
<html lang="en">
<head>
    <meta charset="UTF-8">
	<meta name="description" content="Engage with our advanced AI chat platform. Interactive, intelligent conversations with our AI models for a seamless user experience." />
	<meta name="robots" content="index, follow" />
	<meta name="keywords" content="AI, artificial intelligence, chat platform, conversational AI, chatbots, chat with coding models, 7b, 13b, ai models, chat with ai for free, Hugging Face, HuggingFace models chat, remotely chat with huggingface models" />
	<link rel="canonical" href="https://lollms-unreal.com/ai-chat.php" />	

	<!-- Bootstrap -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>

	<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">

	<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css" integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp" crossorigin="anonymous">

	<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>

	<link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Share+Tech&display=swap" rel="stylesheet">

	<meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat UI</title>
    <style>
        /* Your CSS styles here */
    </style>
</head>
<!-- Tab links -->
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

//alert("Ai Web-ui server currently offline and under construction. Come back tomorrow morning and it'll be online again, thank you!\n\n I apologize for the inconvenience.");

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
	
	<label style="position: relative; left: 16px;">Model Selection (Exllama2)</label>
<select id="model-selector">
		<option value="">Dolphin 7B GPTQ</option>
		<option value="">XwinCoder 13B GPTQ</option>
		<option value="">Mistral 7B GPTQ</option>
		<option value="">WizardCoder 15B GPTQ</option>
</select>

        <!-- Additional sidebar content here -->
    </div>
    <div id="main">

		<button id="sidebarToggle" class="hamburger-button" onclick="toggleSidebar()">&#9776;</button>

        <div class="content">
            <!-- Main content goes here -->
            <div id="loading-overlay" style="display: none;">
    <div class="loading-circle"></div>
</div>


<div class="tab">
  <button class="tablinks" onclick="openTab(event, 'Home')" id="defaultOpen">Home</button><!--
  <button class="tablinks" onclick="openTab(event, 'News')">News</button>
  <button class="tablinks" onclick="openTab(event, 'Contact')">Contact</button>-->
  <button class="tablinks" onclick="openTab(event, 'About')">About</button>
</div>

<!-- Tab content -->
<div id="Home" class="tabcontent">
  <h3>Home</h3>
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
<!--		
<div id="News" class="tabcontent">
  <h3>News</h3>
  <p>Some news this fine day!</p> 
</div>

<div id="Contact" class="tabcontent">
  <h3>Contact</h3>
  <p>Get in touch, or swing by for a cup of coffee.</p>
</div>
-->
<div id="About" class="tabcontent">
  <h3>About</h3>
  
     <div class="header">
        <h1>Welcome to my Light-weight Lollms powered Ai Chat-Ui</h1>
        <p>Use ai to write stories or code your projects with this beautiful ui.</p>
    </div>

<div class="container-fluid">
    <div class="row">
        <div class="col-md-6 col-sm-12">
            <div class="tab-content">
                <img src="ai-image-left.jpg" alt="AI Image Left" class="img-fluid">
                <p>This UI has session management/saving capabilities within the UI to continue your chat with your selected AI chat-bot at any time.</p>
            </div>
        </div>
        <div class="col-md-6 col-sm-12">
            <div class="tab-content">
                <img src="ai-image-right.jpg" alt="AI Image Right" class="img-fluid">
                <p>Talk to your AI chat-bot and use vocal output with the voice of some of my favorite celebrities...</p>
            </div>
        </div>
    </div>
</div>


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

h3 {
	font-family: "Share Tech", sans-serif !important;
}

img.img-fluid {
    width: 50%;
    margin-left: auto;
    margin-right: auto;
    display: block;
}

.col-md-2
{
	
}

select#voice-selector {
    background-color: #23395d;
    color: white;
    padding: 5px;
	position: relative;
    bottom: 10px;
    top: -5px;
	left: 16px;
}

select#model-selector {
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
        margin-left: 300px; /* Adjust as per your sidebar's width */
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

.tablinks
{
color: black;
font-weight: 800;
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
	.content{
	margin-top: 20px !important;
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
    margin-top: 65px;
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

#fileInput {
	color: white;
}

input, select, textarea {
    font-family: inherit;
    font-size: inherit;
    line-height: inherit;
    color: black;
}

#message-input {
    padding: 10px;
    margin: 10px;
    border-radius: 20px;
    border: none;
    outline: none;
    font-size: 1em;
	color: black;
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

/* Style the tab */
.tab {
  overflow: hidden;
  border: 1px solid #ccc;
  background-color: #f1f1f1;
}

/* Style the buttons that are used to open the tab content */
.tab button {
  background-color: inherit;
  float: left;
  border: none;
  outline: none;
  cursor: pointer;
  padding: 14px 16px;
  transition: 0.3s;
}

/* Change background color of buttons on hover */
.tab button:hover {
  background-color: #ddd;
}

/* Create an active/current tablink class */
.tab button.active {
  background-color: #ccc;
}

/* Style the tab content */
.tabcontent {
  padding: 6px 12px;
  border: 1px solid #ccc;
  border-top: none;
}

h1, p {
	text-align: center;
  font-family: "Share Tech", sans-serif !important;
  font-weight: 400;
  font-style: normal;
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
		main.style.marginLeft = '300px'; // Make sure this matches the sidebar's width
	} else {
		sidebar.style.left = '-375px';  // Hide sidebar
		main.style.marginLeft = '0'; // Reset main content margin
	}

}

/*
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

});*/

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
/*socket.on('connect', () => {
    console.log('Connected to the server');
});

socket.on('disconnect', () => {
    console.log('Disconnected from the server');
});
*/

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

document.getElementById('send-button').addEventListener('click', function() {
    const promptText = document.getElementById('message-input').value;
    fetch('/generate-text', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt: promptText })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('response').innerText = data.choices[0].text;
    })
    .catch(error => console.error('Error:', error));
});

const express = require('express');
const axios = require('axios');
require('dotenv').config();

const app = express();
app.use(express.json());

app.post('/generate-text', async (req, res) => {
    const { prompt } = req.body;
    try {
        const response = await axios.post('https://api.openai.com/v1/completions', {
            prompt: prompt,
            max_tokens: 150,
            model: "text-davinci-003",
        }, {
            headers: {
                'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
            }
        });
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

const port = 3000;
app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});

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
    
	//echo 'Server IP Address: ' . $_SERVER['SERVER_ADDR'];

} catch(PDOException $e) {
    
}
?>

<style>
.audioStuff, #status
{
display: none;
}
</style>

<label class="audioStuff" for="api-key-input">API Key:</label>
<input class="audioStuff" type="password" id="azk-data-input" value="bc3f6fab1c2fb9c92c55ae23a66adadb">  <!-- replace with your api key -->

<label class="audioStuff" for="voice-id-input">Voice ID:</label>
<input class="audioStuff" type="text" id="voice-id-input" value="21m00Tcm4TlvDq8ikWAM">

<label class="audioStuff" for="text-input">Text:</label>
<input class="audioStuff" type="text" id="text-input" value="Hello" placeholder="Type something...">
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

function openTab(evt, cityName) {
  var i, tabcontent, tablinks;
  
  // Get all elements with class="tabcontent" and hide them
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  
  // Get all elements with class="tablinks" and remove the class "active"
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  
  // Show the current tab, and add an "active" class to the button that opened the tab
  document.getElementById(cityName).style.display = "block";
  evt.currentTarget.className += " active";
}

// Get the element with id="defaultOpen" and click on it
document.getElementById("defaultOpen").click();

</script>

</div>



<style>
body, h1, p {
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    text-align: center;
    color: white;
}

.header {
    margin-bottom: 50px;
}

.main-content {
    display: flex;
    justify-content: space-between;
}

.tab-content {
    background: #333;
    padding: 20px;
}

.ai-image {
    max-width: 100%;
    height: auto;
    margin-bottom: 20px;
}

/* If you have a solid color background */
body {
}

/* If you want a gradient background */
/*
body {
}
*/

/* For the title styling */
.header h1 {
    font-size: 2.5em;
    color: #ffffff;
    margin-bottom: 0.5em;
}

.header p {
    font-size: 1.2em;
    color: #cccccc;
}

</style>

</body>
</html>

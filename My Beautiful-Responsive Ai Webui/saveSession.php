<?php
include 'db_connection.php'; // Ensure proper connection

// Check if the request is POST and the necessary data is available
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['conversation_data'])) {
    $session_id = uniqid(); // Generate a unique session ID
    $user_id = 1; // Example user ID, adjust as necessary
    $conversation_data = $_POST['conversation_data']; // Directly taking HTML content

    // Optionally sanitize the HTML here if needed
    $conversation_data = htmlspecialchars($conversation_data, ENT_QUOTES, 'UTF-8');

    // Insert the HTML content into the database
    $sql = "INSERT INTO sessions (session_id, user_id, conversation_data) VALUES (?, ?, ?)";
    $stmt = $pdo->prepare($sql);

}
?>

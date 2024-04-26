<?php
// renameSession.php
require 'db_connection.php'; // Your PDO connection file

// Only proceed if the request is a POST request
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Assume $sessionId and $newName are passed from a form or an AJAX call
    $sessionId = $_POST['session_id'] ?? null;
    $newName = $_POST['new_name'] ?? null;
    
    // Validate inputs here...

    if ($sessionId && $newName) {
        $stmt = $pdo->prepare("UPDATE sessions SET session_name = :new_name WHERE session_id = :session_id");
        $stmt->execute([
            'new_name' => $newName,
            'session_id' => $sessionId
        ]);
        echo "Session renamed successfully.";
    } else {
        echo "Invalid session ID or name.";
    }
} else {
    // Not a POST request
    echo "Invalid request method.";
}
?>

<?php

// Include your database connection details and functions here
// At the top of your api.php
ini_set('display_errors', 0); // Turn off error printing
header('Content-Type: application/json'); // Set the content type so JS knows to expect JSON

// Then, at the point where you're echoing out the response:
echo json_encode(['error' => $e->getMessage()]);

// Switch based on the type of request
switch($_SERVER['REQUEST_METHOD']) {
    case 'POST':
        // Handle creating new sessions or adding messages
        $data = json_decode(file_get_contents('php://input'), true);
        if(isset($data['action'])) {
            if($data['action'] == 'create_session') {
                $sessionId = createNewSession($pdo);
                echo json_encode(['session_id' => $sessionId]);
            } elseif($data['action'] == 'send_message') {
                $sessionId = $data['session_id'];
                $userId = $data['user_id']; // This would come from your session management system
                $text = $data['text'];
                $messageId = addMessageToSession($pdo, $sessionId, $userId, $text);
                echo json_encode(['message_id' => $messageId]);
            }
        }
        break;

    case 'GET':
        // Handle retrieving messages for a session
        $sessionId = $_GET['session_id'];
        $messages = getSessionMessages($pdo, $sessionId);
        echo json_encode($messages);
        break;
}
?>

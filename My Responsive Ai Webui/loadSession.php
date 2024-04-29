<?php
include 'db_connection.php';  // Includes the PDO connection setup
require_once 'HTMLPurifier.auto.php';

function fetchSessionDataFromDatabase($sessionId) {
    global $pdo;  // Ensure that $pdo is the PDO connection object and is accessible
    try {
        $stmt = $pdo->prepare("SELECT conversation_data FROM sessions WHERE session_id = ?");
        $stmt->execute([$sessionId]);
        return $stmt->fetchColumn();  // Fetches data from the 'conversation_data' column
    } catch (PDOException $e) {
        die("Database error: " . $e->getMessage());  // Proper error handling
    }
}


$sessionId = $_GET['session_id'] ?? '';
$dirty_html = fetchSessionDataFromDatabase($sessionId);

$config = HTMLPurifier_Config::createDefault();
$purifier = new HTMLPurifier($config);
$clean_html = $purifier->purify($dirty_html);

echo $clean_html;
?>

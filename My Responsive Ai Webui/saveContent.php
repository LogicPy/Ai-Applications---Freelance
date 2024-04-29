<?php
require_once 'db_connection.php';
require_once 'HTMLPurifier.auto.php';

$session_id = uniqid(); // Assuming you want a new session ID every time
$html_content = $_POST['html_content'] ?? 'No content received'; // Default message if nothing is received

echo "Received content: $html_content"; // Debug output

$config = HTMLPurifier_Config::createDefault();
$purifier = new HTMLPurifier($config);
$clean_html = $purifier->purify($html_content);

$stmt = $pdo->prepare("INSERT INTO sessions (session_id, conversation_data) VALUES (?, ?)");
$stmt->execute([$session_id, $clean_html]);

echo "Content saved successfully with Session ID: $session_id";
?>
<?php
$dbHost = "localhost";
$dbUsername = "waynecoo_Ai_framework";
$dbPassword = "asdf123";
$dbName = "waynecoo_ai_db";

try {
    $pdo = new PDO("mysql:host=$dbHost;dbname=$dbName", $dbUsername, $dbPassword);
    // set the PDO error mode to exception
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch(PDOException $e) {
    echo "Connection failed: " . $e->getMessage();
}
?>

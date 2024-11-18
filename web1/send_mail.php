<?php
// Enable error reporting for debugging
ini_set('display_errors', 1);
error_reporting(E_ALL);

header('Content-Type: application/json');

// Check if POST request
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Get input JSON and decode
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);

    if (!isset($data['email']) || !isset($data['subject']) || !isset($data['message'])) {
        echo json_encode(['status' => 'error', 'message' => 'Invalid input']);
        exit;
    }

    // Extract data
    $to = $data['email'];
    $subject = $data['subject'];
    $message = $data['message'];
    $headers = "From: noreply@yourdomain.com\r\n";

    // Attempt to send email
    if (mail($to, $subject, $message, $headers)) {
        echo json_encode(['status' => 'success', 'message' => 'Email sent successfully']);
    } else {
        echo json_encode(['status' => 'error', 'message' => 'Failed to send email']);
    }
} else {
    echo json_encode(['status' => 'error', 'message' => 'Invalid request method']);
}
exit;

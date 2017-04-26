<?php

$conn_hostname = 'localhost';
$conn_username = 'batcave1_corelex';
$conn_password = trim(file_get_contents('password.txt'));
$conn_database = 'batcave1_corelex';

function show_connection() {
  global $conn_hostname, $conn_username, $conn_password, $conn_database;
  dbg("DATABASE: $conn_hostname > $conn_username > $conn_database"); }

?>

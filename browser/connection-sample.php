<?php

$TIMEML_SERVER = false;

$host = 'localhost:8889';
$user = 'root';
$password = 'root';
$db = 'corelex-browser';

if ($TIMEML_SERVER) {
    $host = 'MySQL.timeml.org';
    $user = 'xtimeml';
    $password = 'store4time!';
    $db = 'xtimeml-aida';
}

?>

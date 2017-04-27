<?php

require('debugging.php');

//$DEBUG = true;

foreach (file('config.txt') as $line) 
{
  if ($line[0] == '#') { continue; }
  $fields = explode('=', $line);
  if (count($fields) == 2) {
     $key = trim($fields[0]);
     $value = trim($fields[1]);
     if ($key == 'hostname') { $conn_hostname = $value; }
     elseif ($key == 'username') { $conn_username = $value; }
     elseif ($key == 'password') { $conn_password = $value; }
     elseif ($key == 'database') { $conn_database = $value; }
  }
}

function show_connection() {
  global $conn_hostname, $conn_username, $conn_password, $conn_database;
  dbg("DATABASE: $conn_hostname > $conn_username > $conn_database"); }

?>

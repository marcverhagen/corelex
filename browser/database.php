<?php

include "connection.php";


// basic database connectivity

function db_connect() {
    global $host, $user, $password, $db;
    dbg("$host $user $password $db");
    $conn = new mysqli($host, $user, $password, $db);
    if ($conn->connect_error)
        die("Connection failed: " . $conn->connect_error);
    return $conn;
}

function db_select($conn, $query) {
    dbg($query);
    $result = $conn->query($query);
    $objects = array();
    if ($result->num_rows > 0) {
        while($object = $result->fetch_object())
            $objects[] = $object;
        $result->free(); }
    return $objects;
}

function db_insert($conn, $query) {
    dbg($query);
    $result = $conn->query($query);
}

function db_update($conn, $query) {
    dbg($query);
    $result = $conn->query($query);
}



// CoreLex DB access

function db_get_corelex_types($connection) {
    return db_select($connection, "select * from corelex_types");
}

function db_get_corelex_type($connection, $type_name) {
    return db_select($connection, "select * from corelex_types where corelex_type='$type_name'");
}

function db_get_basic_types($connection) {
    return db_select($connection, "select * from basic_types");
}

function db_get_nouns($connection, $type_name) {
    return db_select($connection, "select * from nouns where corelex_type='$type_name'");
}

function db_get_noun_types($connection, $noun) {
    return db_select($connection, "select * from nouns where noun='$noun'");
}

?>

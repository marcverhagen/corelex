<?php

// DEBUGGING UTILITY METHODS

$DEBUG = false;
$LOGFILE = NULL;


function dbg($object)
{
  global $DEBUG;
  if (! $DEBUG) { return; }
  if (is_object($object) or is_array($object)) {
    echo "<pre>\n";
    print_r($object);
    echo "</pre>\n"; 
  } else {
    echo "<pre>$object</pre>\n";		
  }
}

function dbg_warn($message, $force_warning=False)
{
  global $DEBUG;
  if ($DEBUG or $force_warning) {
    echo "<pre><font color=red>WARNING: $message</font></pre>\n"; }
}

function dbg_memory_usage()
{
  if ( function_exists('memory_get_usage') ) {
    $mem = round(memory_get_usage() / (1024*1024), 1)." Mb";
    dbg("Memory = $mem <br>\n"); }
}

function dbg_vars()
{
  global $_GET, $_POST, $_SESSION, $_FILES, $DEBUG;
  if (! $DEBUG) { return; }
  echo "<pre>\n";
  foreach ($_GET as $var => $value) {
    echo "\$_GET['$var'] => ";
    _dbg_v($var, $value); }
  foreach ($_POST as $var => $value) {
    echo "\$_POST['$var'] => ";
    _dbg_v($var, $value); }
  foreach ($_SESSION as $var => $value) {
    echo "\$_SESSION['$var'] => ";
    _dbg_v($var, $value); }
  foreach ($_FILES as $var => $value) {
    echo "\$_FILES['$var'] => ";
    _dbg_v($var, $value); }
  echo "</pre>\n";
}

function _dbg_v($var, $value)
{
  if (is_array($value)) {
    echo '[ ' . implode(' , ', $value) . " ]\n"; }
  else {
    echo "'$value'\n"; }
}

?>

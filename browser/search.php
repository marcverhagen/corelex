<?php

require('database.php');
require('utils.php');

db_connect();

$DEBUG = true;
$DEBUG = false;

$noun = $_GET['noun'];
if ($noun) {
  $noun_types = db_get_noun_types($noun);
}

?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
<title>CoreLex Browser</title>
<link href="style.css" rel="stylesheet" type="text/css">
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
</head>

<body>

<h1>Search CoreLex</h1>

<?php util_write_navigation(); ?>

<?php
  if ($DEBUG) {
    printf("<pre>\n");
    print_r($noun_types);
    printf("</pre>\n");
  }
?>

<p>
  <form action="search.php">
  Enter a nominal:
  <input type="text" name="noun">
  <input type="submit" value="search">
  </form>
</p>
  
<?php 
  if ($noun and $noun_types) {
    printf("<p>Search results for: <b>$noun</b></p>"); 
?>

<p>
<table class="indent" cellpadding="5" cellspacing="0" border="1">
<tr valign="top">
  <td>Corelex Type</td>
  <td>Polysemous Type</td>
</tr>
<?php
    foreach ($noun_types as $type) {
      $ct = $type->corelex_type;
      printf("<tr>\n");
      printf("  <td><a href='view_type.php?id=%s'>%s</a></td>\n", $ct, $ct);
      printf("  <td>%s</td>\n", $type->polysemous_type);
      printf("</tr>\n");
    }
    ?>
</table>

<?php
  } else if ($noun) {
?>

<p>Did not find <b><?php echo $noun ?></b> in CoreLex</p>

<?php
  }
?>

</body>
</html>

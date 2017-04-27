<?php

require('utils.php'); 
require('database.php'); 

db_connect();

$basic_types = db_get_basic_types();

?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
<title>CoreLex Browser</title>
<link href="style.css" rel="stylesheet" type="text/css">
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
</head>

<body>

<h1>Basic Types</h1>

<?php util_write_navigation(); ?>

<table class="indent" cellpadding="5" cellspacing="0" border="1">

<tr>
<td>basic type</td>
<td>synset</td>
<td>synset members</td>
</tr>

<?php
  foreach ($basic_types as $bt) {
    printf("<tr>\n");
    printf("<td>%s</td>\n", $bt->basic_type);
    printf("<td>%s</td>\n", $bt->synset_number);
    printf("<td>%s</td>\n", $bt->synset_elements);
    printf("</tr>\n");
  }
?>

</table>

</body>
</html>

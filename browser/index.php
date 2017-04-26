<?php

require('database.php');
require('utils.php');

db_connect();

$corelex_types = db_get_corelex_types();
$basic_types = db_get_basic_types();
$basic_types_idx = array();
foreach ($basic_types as $bt) {
  $basic_types_idx[$bt->basic_type] = $bt;
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

<!--
<pre>
<?php print_r($basic_types_idx); ?>
</pre>
-->

<h2>CoreLex Types</h2>

<table cellpadding="5" cellspacing="0" border="1">

<?php

$last = null;
foreach ($corelex_types as $t) {
  $current = $t->corelex_type;
  if ($last == $current) {
    printf("<tr>\n");
    printf("  <td>&nbsp\n");
  } else {
    printf("<tr>\n");
    printf("  <td><a href='view_type.php?id=%s'>%s</a>\n", $t->corelex_type, $t->corelex_type);
  }
  printf("  <td>%s\n", $t->polysemous_type);
  printf("  <td>%s\n", util_collect_synsets($t->polysemous_type, $basic_types_idx));
  $last = $current;
}

?>

</table>

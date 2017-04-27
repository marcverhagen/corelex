<?php

require('database.php');
require('utils.php');

db_connect();

$type_name = $_GET['id'];

$corelex_type = db_get_corelex_type($type_name);

$basic_types = db_get_basic_types();
$basic_types_idx = array();
foreach ($basic_types as $bt) {
  $basic_types_idx[$bt->basic_type] = $bt;
}

$nouns = db_get_nouns($type_name);

$wordnet_url = 'http://wordnetweb.princeton.edu/perl/webwn'

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
<?php 
  //print_r($corelex_type);
  //print_r($nouns); ?>
</pre>
-->

<h1>CoreLex Type <?php echo strtoupper($type_name); ?></h1>

<?php util_write_navigation(); ?>

<table class="indent" cellpadding="5" cellspacing="0" border="1">

<?php

$last = null;
foreach ($corelex_type as $t) {
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

<br/>

<table class="nouns indent" cellpadding="5" cellspacing="0" border="1">

<?php
foreach ($corelex_type as $t) {
  $poltype = $t->polysemous_type;
  printf("<tr>\n");
  printf("  <td valign=top>%s\n", str_replace(' ', '&nbsp;', $poltype));
  printf("  <td>\n");
  foreach ($nouns as $noun) {
    if ($noun->polysemous_type == $poltype) {
      //printf("%s ", $noun->noun);
      printf("<a href='%s?s=%s'>%s</a> ", $wordnet_url, $noun->noun, $noun->noun);
    }
  }
}
?>

</table>

</body>
</html>

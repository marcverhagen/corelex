<?php

include 'debugging.php';
include 'utils.php';
include 'database.php';

$connection = db_connect();

$noun = $_GET['noun'];

$search_allowed = true;
if ($noun) {
    // using ctype_alpha was too restrictive
    if (ctype_alpha($noun) or is_null($noun) or true) {
        $noun_types = db_get_noun_types($connection, $noun);
        //dbg($noun_types);
    } else {
        $search_allowed = false;
    }
}

$connection->close();

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

<h1>Search CoreLex</h1>

<?php util_write_navigation(); ?>

<p>
  <form action="search.php">
  Enter a nominal:
  <input type="text" name="noun">
  <input type="submit" value="search">
  </form>
</p>

<?php
if (! $search_allowed) {
    printf("<p class='warning'>WARNING: search term '%s' is not allowed, use letters only.</p>\n", $noun);
} else if ($noun and $noun_types) {
    printf("<p><b>$noun</b></p>");
?>

<p>
<table class="indent" cellpadding="5" cellspacing="0" border="1">
<tr valign="top">
  <td>Corelex Type</td>
  <td>Polysemous Type</td>
  <td>WordNet Entry</td>
</tr>
<?php
    foreach ($noun_types as $type) {
      $ct = $type->corelex_type;
      $noun_search_term = str_replace("_", "%20", $noun);
      $wn = sprintf("%s?s=%s", $wordnet_url, $noun_search_term);
      printf("<tr>\n");
      printf("  <td><a href='view_type.php?id=%s&noun=%s'>%s</a></td>\n", $ct, $noun, $ct);
      printf("  <td>%s</td>\n", $type->polysemous_type);
      printf("  <td><a href='%s'>%s</a></td>\n", $wn, $wn);
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

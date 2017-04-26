<?php


function util_write_navigation()
{
  printf("<p class='navigation'>\n");
  printf("[ <a href='index.php'>Home</a>\n");
  printf("| <a href='view_types.php'>CoreLex Types</a>\n");
  printf("| <a href='view_basic_types.php'>Basic Types</a>\n");
  printf("| <a href='search.php'>Search</a>\n");
  printf("]\n");
  printf("</p>\n");
}


function util_collect_synsets($basic_types_string, $basic_types_idx) 
{
  $answer = array();
  $basic_types = explode(' ', $basic_types_string);
  foreach ($basic_types as $bt) {
    $synset = $basic_types_idx[$bt]->synset_elements;
    array_push($answer, $synset);
  }
  return implode(' ', $answer);
}

?>
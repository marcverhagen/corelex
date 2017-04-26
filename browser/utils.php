<?php

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
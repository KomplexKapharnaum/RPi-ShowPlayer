<?php


$filename = $_POST['fileName'].'.json';

$file = '../../_SCENARIO/data/'.$filename;

//echo $file;

$fh = fopen($file, 'w') or die("can't open file");
fclose($fh);

unlink($file);

?>

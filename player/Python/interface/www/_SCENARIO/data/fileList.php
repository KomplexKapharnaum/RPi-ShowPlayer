<?php

$dir = "./";

$dh  = opendir($dir);

while (false !== ($filename = readdir($dh))) {
    $files[] = $filename;
}
$jsons=preg_grep ('/\.json$/i', $files);

echo json_encode($jsons);


?>

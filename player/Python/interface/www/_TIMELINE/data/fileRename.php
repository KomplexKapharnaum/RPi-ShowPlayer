<?php


$oldfilename = $_POST['oldname'].'.json';
$newfilename = $_POST['newname'].'.json';

$oldfile = '../../_SCENARIO/data/'.$oldfilename;
$newfile = '../../_SCENARIO/data/'.$newfilename;

rename($oldfile,$newfile);


?>

<?php


    $filename = $_POST['filename'];

    $json = $_POST['contents'];


    $file = fopen($filename,'w+');
    fwrite($file, $json);
    fclose($file);
    $response['status'] = 'success';


    //SEND Ajax response in JSON format
    header('Content-type: application/json');
    echo json_encode($response);
?>

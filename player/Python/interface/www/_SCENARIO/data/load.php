<?php


    $filename = $_POST['filename'].'.json';

    if ( file_exists($filename))
    {
        $response['status'] = 'success';
        $response['contents'] = file_get_contents($filename);
    }
    else
    {
        $response['status'] = 'error';
        $response['message'] = 'File '.$filename.' not found..';
    }

    header('Content-Type: application/json');
    echo json_encode($response);


?>

<?php


    $filename = $_POST['filename'].'.json';

    $json = $_POST['contents'];

    if (json_decode($json) != null)
    {
        $file = fopen($filename,'w+');
        fwrite($file, $json);
        fclose($file);
        $response['status'] = 'success';
    }
    else
    {
        $response['status'] = 'error';
        $response['message'] = 'JSON not valid';
    }

    //SEND Ajax response in JSON format
    header('Content-type: application/json');
    echo json_encode($response);
?>

<?php

header('Content-Type: application/json');
header("Access-Control-Allow-Origin:*");


$conn = new mysqli("qagi935.anmabe.es", "qahu260", "tZz5kw42sautFMbBozJ7uc38JNu4TKFkfJZyxAwJUpNTbUfXyx", "qagi935");

if ($conn->connect_error) {
    echo json_encode(["error" => "Error while connecting to database."]);
}

$sql = "SELECT ".$_GET["param"]." FROM qagi935.`cansat_data` WHERE time='".$_GET["time"]."';";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    // output data of each row
    while($row = $result->fetch_assoc()) {
        echo json_encode($row);
    }
} else {
    // echo json_encode(["sql" => $sql, "error" => "No results where obtained from the given parameter and/or time"]);
    echo json_encode(["error" => "No results where obtained from the given parameter and/or time"]);
}



?>
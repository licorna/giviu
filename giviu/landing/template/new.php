<?php
	foreach($_POST AS $key => $value) {
		${$key} =$value;
	}

	$db_host="localhost"; 
	$db_usuario="root"; 
	$db_password="estel167098592"; 
	$db_nombre="waiting-list"; 
	$conexion = @mysql_connect($db_host, $db_usuario, $db_password) or die(mysql_error()); 
	$db = @mysql_select_db($db_nombre, $conexion) or die(mysql_error()); 

	$sql = "INSERT INTO  `waiting-list`.`users` (`id` ,`name` ,`email` ,`creation-date`)VALUES (NULL ,  '".$name."',  '".$email."', CURRENT_TIMESTAMP)";
	$result=mysql_query($sql, $conexion); 
	echo '1';
?>

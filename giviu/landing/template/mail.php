<?

foreach($_POST AS $key => $value) {
	${$key} =$value;
}
$contact = $name .":". $contact;

$cabecera = "MIME-Version: 1.0" . "\r\n";
$cabecera.= "Content-type:text/html;charset=iso-8859-1" . "\r\n";
$cabecera.= 'From: <'.$email.'>' . "\r\n";

mail("sebastian@giviu.com","[correo landing]",$contact,$cabecera);
?>
<script>
location.href="http://www.giviu.com/?msg=Tu mensaje ha sido enviado";

</script>
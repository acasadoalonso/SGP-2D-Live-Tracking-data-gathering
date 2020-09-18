<?php
$action='list';
$trk='ALL';
if (isset($_GET['action'])){
        $action=$_GET['action'];
}
if (isset($_GET['trk']))
	$trk=$_GET['trk'];
	
#print $trk.$flarmid.$owner.$deleteyn;

$cwd =getcwd();
$rc=0;
ob_start();

passthru('/usr/bin/python3  ./trkstatus.py '.$action.' '.$trk.' ', $rc);

$output = ob_get_clean();
echo nl2br($output);
exit;
?>

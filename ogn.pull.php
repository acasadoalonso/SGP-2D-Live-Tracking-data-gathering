<?php

// Use in the “Post-Receive URLs” section of your GitHub repo.

if ( $_SERVER['HTTP_X_GITHUB_EVENT'] == 'push') {
        ob_start();
        passthru("chmod 775 -R * .gi* ");
        passthru("/usr/bin/git --no-pager pull origin master");
        $var = ob_get_contents();
        passthru("rm -f UPDATED.by.GIT.*");
	$ip = $_SERVER['HTTP_X_REAL_IP'];
        passthru("touch UPDATED.by.GIT.".$ip);
        passthru("chmod 775 -R * .gi* ");
        ob_end_clean(); 
        echo "RC=".$var." \n";
}
echo date("Y-m-d H:i:s")." ";
//echo var_dump($_SERVER);
echo $_SERVER['HTTP_X_GITHUB_EVENT'];
echo " IP: ";
echo $_SERVER['HTTP_X_REAL_IP'];
?> Hi ... git pull done !!!


<?php

// Use in the “Post-Receive URLs” section of your GitHub repo.

if ( $_SERVER['HTTP_X_GITHUB_EVENT'] == 'push') {
        ob_start();
        passthru("chmod 775 -R * .gi* ");
        passthru("/usr/bin/git --no-pager pull origin master");
        $var = ob_get_contents();
        passthru("chmod 775 -R * .gi* ");
        passthru("touch UPDATED.by.GIT");
        ob_end_clean(); 
        echo "RC=".$var." \n";
}
echo date("Y-m-d H:i:s")." ";
//echo var_dump($_SERVER);a
echo $_SERVER['HTTP_X_GITHUB_EVENT']
?> Hi ... git pull done !!!

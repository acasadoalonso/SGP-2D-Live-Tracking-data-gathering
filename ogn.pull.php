<?php

// Use in the “Post-Receive URLs” section of your GitHub repo.

if ( $_SERVER['HTTP_X_GITHUB_EVENT'] == 'push') {
        ob_start();
        passthru("/usr/bin/git --no-pager pull origin master");
        $var = ob_get_contents();
        echo "RC=".$var."\n";
        passthru("chmod 775 -R * .gi* ");
        passthru("touch UPDATED.by.GIT");
        ob_end_clean(); 
}
//echo var_dump($_SERVER);
?>Hi ... git pull done !!!

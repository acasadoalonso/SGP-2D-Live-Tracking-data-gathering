<?php

// Use in the “Post-Receive URLs” section of your GitHub repo.

if ( $_SERVER['HTTP_X_GITHUB_EVENT'] == 'push') {
        ob_start();
        passthru("/usr/bin/git --no-pager pull origin master");
        $var = ob_get_contents();
        passthru("touch UPDATED.by.GIT");
        ob_end_clean(); 
        echo "RC=".$var."\n";
        //echo "git pull done\n\n";
}
//echo var_dump($_SERVER);
?>hi

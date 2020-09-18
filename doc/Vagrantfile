# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"
  config.vm.hostname = "UBUVM"
  config.ssh.username = "ubuntu"
  config.ssh.password = "ubuntu"
  # config.vm.network "forwarded_port", guest: 80, host: 8080
  # config.vm.network "private_network", ip: "192.168.33.10"
   config.vm.network "public_network", ip: "192.168.2.77", bridge: "eth1: Broadcom NetXtreme Gigabit Ethernet"
   config.vm.synced_folder "./html", "/var/www/html"
  # default router
  config.vm.provision "shell",
    run: "always",
    inline: "route add default gw 192.168.2.1"


  # delete default gw on eth0
  config.vm.provision "shell",
    run: "always",
    inline: "eval `route -n | awk '{ if ($8 ==\"eth0\" && $2 != \"0.0.0.0\") print \"route del default gw \" $2; }'`"
end



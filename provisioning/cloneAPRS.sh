#!/bin/bash
sudo apt install -y  python3-pip
/usr/bin/python3 -m pip install --upgrade pip
pip3 install ansible
rm html
sudo rm -r public
git clone https://github.com/acasadoalonso/SGP-2D-Live-Tracking.git 			public
git clone https://github.com/acasadoalonso/SGP-2D-Live-Tracking-data-gathering.git 	public/main
ln -s public html
ls -la
echo " "
echo "invoke:   vagrant up      in order to create the VM and provision it "
echo " "

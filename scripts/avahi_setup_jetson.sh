#!/bin/bash -e
echo "Setting up Avahi and setup tools..."

sudo apt-get install -y avahi-daemon

# https://manpages.ubuntu.com/manpages/trusty/man5/avahi-daemon.conf.5.html
# Enables some settings that are good and useful to have actived
avahi_modify() { # Usage: avahi_modify KEY VALUE
	# first -e removes comment # if it exists. Second -e sets the value to whatever was passed. 
	sudo sed -i -e "/$1/s/^#//g" -e "s/\($1 *= *\).*/\1$2/" /etc/avahi/avahi-daemon.conf
}

avahi_modify publish-addresses yes
avahi_modify publish-hinfo yes
avahi_modify publish-workstation yes
avahi_modify publish-domain yes

hostname=$(hostname)

echo "Avahi Succesfully set up"
echo -e "Your computer is accesible at ${hostname}.local"

while true; do
	printf "Would you like to change the address hostname it is accesible at obico.local?\nYes/No (yN)\tDetails (d) "
	read -p " " ynd

	case $ynd in
		[Yy]* ) avahi_modify host-name obico; hostname="obico"; printf "\nHostname set to Obico.\n"; break;;
		[Nn]* ) break;;
		[Dd]* ) echo "Changing the Avahi hostname to Obico will change the address your server is currently accesible from. This will not have any other effect on your computer. This can easily be manually rverted or changed back later on if you choose.";;
		* ) echo "Please answer yes for obico, or no to leave hostname as is";;
	esac
done

sudo systemctl enable avahi-daemon
sudo systemctl start avahi-daemon

sleep 5
# Test pings to ensure that the address is setup. In my experience, Avahi sets up pretty quickly, so more than 5 seconds is unnecesary
ping -q -c5 $hostname.local > /dev/null
if [ $? -eq 0 ]; then
	sudo systemctl restart avahi-daemon
fi

sleep 5

ping -q -c5 $hostname.local > /dev/null
if [ $? -eq 0 ]; then
 	echo -e "Odd, Avahi is still not running. Status of avahi can be found with the command \"sudo systemctl status avahi-daemon\""
else
	echo -e "Avahi is now setup. Server is accessible at $hostname.local"
fi

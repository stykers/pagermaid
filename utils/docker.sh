#!/bin/sh

echo ""
echo "Welcome to Jarvis docker installer."
echo "The installation process will begin"
echo "in 5 seconds, if you wish to cancel,"
echo "please abort within 5 seconds."
echo ""
sleep 5

echo "Checking for docker . . ."
if command -v docker;
then
  echo "Docker appears to be present, moving on . . ."
else
  echo "Docker is not installed on this system, please"
  echo "install docker and add yourself to the docker"
  echo "group and re-run this script."
  exit 1
fi

echo "Testing for docker access . . ."
if [ -w /var/run/docker.sock ]
then
  echo "This user can access docker, moving on . . ."
else
  echo "This user has no access to docker, please add"
  echo "yourself to the docker group or run the script"
  echo "as superuser."
fi

echo "Downloading repository . . ."
rm -rf /tmp/jarvis
git clone https://git.stykers.moe/scm/~stykers/jarvis.git /tmp/jarvis
cd /tmp/jarvis || return

echo "Generating config file . . ."
cp config.gen.env config.env
printf "Please enter application API Key: "
read -r api_key
sed -i "s/ID_HERE/$api_key/"
printf "Please enter application API Hash: "
read -r api_hash
sed -i "s/HASH_HERE/$api_hash/"
printf "Please enter application language (Example: en): "
read -r application_language
sed -i "s/en/$application_language/"
printf "Please enter application region (Example: United States): "
read -r application_region
sed -i "s/United States/$application_region/"
printf "Enable logging? [Y/n]"
read -r logging_confirmation
case $logging_confirmation in
    [yY][eE][sS]|[yY])
		printf "Please enter your logging group/channel chatid: "
		read -r log_chatid
		sed -i "s/en/$log_chatid/"
		sed -i "s/LOG=False/LOG=True/"
		;;
    [nN][oO]|[nN])
		echo "Moving on . . ."
       		;;
    *)
	echo "Invalid choice . . ."
	exit 1
	;;
esac

echo "Building docker image . . ."
docker rm -f jarvis > /dev/null 2>&1
docker build . --force-rm --no-cache -t jarvis

echo "Starting docker container . . ."
echo "After logging in, press Ctrl + C to make the container restart in background mode."
docker run -it --restart=always --name=jarvis --hostname=jarvis jarvis

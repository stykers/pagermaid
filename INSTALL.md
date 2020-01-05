# Installation

Here are the installation instructions of Jarvis, with support
 for a variation of init systems.

## Quick start
If your system is compatible with docker, and you want a 
snappy and supported environment, docker is the way for you.
Tho this will limit system-wide utilities to within the container.

Create your application at https://my.telegram.org/, and 
run this command:
```shell script
curl -fsSL https://git.stykers.moe/users/stykers/repos/jarvis/raw/utils/docker.sh | sh
```
If you want to inspect the script content before running:
```shell script
curl https://git.stykers.moe/users/stykers/repos/jarvis/raw/utils/docker.sh -o docker.sh
vim docker.sh
chmod 0755 docker.sh
./docker.sh
```

## Requirements
You need Linux or *BSD for this software, and your system
 should run at least python 3.6, virtualenv support is
  recommended.

Assuming you have settled your python environment (python
 interpreter, virtualenv and such), let's move on to
  configuration.

## Configuration
Copy the file config.gen.env to config.env, and open it with
 your favorite text editor, it should look like this:
```.env
API_KEY="ID_HERE"
API_HASH="HASH_HERE"
DEBUG=False
APPLICATION_LANGUAGE="en"
APPLICATION_REGION="United States"
LOG=False
LOG_CHATID=503691334
RESULT_LENGTH=5
WIDTH=1920
HEIGHT=1080
BACKGROUND="#101010"
MARGIN=20
```
You should definitely update the LOG_CHATID before enabling
 logging (or not if you are close friends with me), but first
 we need to get the bot started, go to
 https://my.telegram.org/apps and create an application,
 fill in the config file API credentials from the data
 provided, and set language to your language code,
 and set region to your country **full name**.

## Installation
Copy the Jarvis work dir to /var/lib, and enter
 /var/lib/jarvis, then source the venv again if needed,
 and install all dependencies from requirements.txt
```shell script
pip3 install -r requirements.txt
```
Now make sure zbar, neofetch, tesseract and ImageMagick
 packages are installed via your package manager, and you
 are ready to start Jarvis.
```shell script
python3 -m jarvis
```

## Deploy init scripts
Make sure you have ran Jarvis at least once or have the
 session file in place before starting the service.
- Runit: make a dir in /etc/sv/jarvis and copy utils/run to
 it
- SystemD: copy utils/jarvis.service into /var/lib/systemd/system
- Direct: run utils/start.sh

## Authentication
Sometimes (or most of the times) when you deploy Jarvis on
 a server, you will have problems during login, when this
 happens, finish the configuration step and then run
 utils/mksession.py on your PC, and push the jarvis.session
 to the server.
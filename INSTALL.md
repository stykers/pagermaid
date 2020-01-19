# Installation

Here are instructions you will need to get PagerMaid started, with
 support for various init systems.

## Quick start
If your system is compatible with docker, and you want a 
snappy and supported installation, docker will get you started
 very quickly. Despite the convenience, this installation method
 limits system-wide utilities to within the container.

Create your application at https://my.telegram.org/, and 
run this command:
```shell script
curl -fsSL https://git.stykers.moe/users/stykers/repos/pagermaid/raw/utils/docker.sh | sh
```
If you want to inspect the script content before running:
```shell script
curl https://git.stykers.moe/users/stykers/repos/pagermaid/raw/utils/docker.sh -o docker.sh
vim docker.sh
chmod 0755 docker.sh
./docker.sh
```

## Requirements
You need Linux or *BSD for this software, and your system
 should run at least python 3.6, virtualenv support is
  recommended.

Assuming your python environment meets the standards,
 let's move on to configuration.

## Configuration
Copy the file config.gen.env to config.env, and open it with
 your favorite text editor. Edit the config file until you are
 satisfied with the settings.

## Installation from source
Copy the PagerMaid work dir to /var/lib, and enter
 /var/lib/pagermaid, then source the venv again if needed,
 and install all dependencies from requirements.txt
```shell script
pip3 install -r requirements.txt
```
Now make sure zbar, neofetch, tesseract and ImageMagick
 packages are installed via your package manager, and you
 are ready to start PagerMaid.
```shell script
python3 -m pagermaid
```

## Deploy init scripts
Make sure you have ran PagerMaid at least once or have the
 session file in place before starting the service.
- Runit: make a dir in /etc/sv/pagermaid and copy utils/run to
 it
- SystemD: copy utils/pagermaid.service into /var/lib/systemd/system
- Direct: run utils/start.sh

## Authentication
Sometimes (or most of the times) when you deploy PagerMaid on
 a server, you will have problems during login, when this
 happens, finish the configuration step and then run
 utils/mksession.py on your PC, and push the pagermaid.session
 to the server.
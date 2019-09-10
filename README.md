# Jarvis

Jarvis is a utility daemon for telegram.

It automates a range of tasks by responding to commands issued to self.

## Features

Jarvis has many features, including account manipulation and query, system administration utilities, chat moderation,
and misc message utils.

For full list see [FEATURES.md](https://git.stykers.moe/users/stykers/repos/jarvis/browse/FEATURES.md).

## Get Started

A venv is recommended for this program, python 3.6+ is required too.

Inside the project directory, run:

```bash
/usr/bin/env python3 -m virtualenv venv
```

And then:

```bash
source venv/bin/activate
```

After that, install dependencies:

```bash
pip install -r requirements.txt
# After you install the python modules you also need to install the 
# zbar, neofetch, tesseract and imagemagick packages using your 
# distribution's native package manager.
```

Generate config files:

```bash
cp config.gen.env config.env
vim config.env
```

Fill in your options, and start the bot.

```bash
/bin/sh -c utils/start.sh
```

Follow the prompts, after you login, do -help in telegram for the help message.

## Using SystemD

After running the bot first time, you can consider using the systemd unit.

Move the directory to /var/lib:

```bash
sudo mv jarvis /var/lib/jarvis
```

Edit the sample unit file in utils/ to meet your work user and copy it into systemd unit files.

```bash
sudo cp /var/lib/jarvis/utils/jarvis.service /usr/lib/systemd/system/jarvis.service
sudo vim /usr/lib/systemd/system/jarvis.service
```

Now reload systemd and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now jarvis.service
```
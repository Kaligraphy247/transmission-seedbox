# transmission-seedbox
...


## Making gunicorn run as a daemon
- Note: Replace all the text in angled brackets with your own infomation

```bash
[Unit]
Description=Gunicorn server for <myseedboxname or NameOfYourChoice>

[Service]
User=<root or your username>
WorkingDirectory=<pathToYourSeedboxDirector>
ExecStart=/bin/bash -c 'cd <projectDirectory> && source <venvDir>/bin/activate && gunicorn wsgi:app'

[Install]
WantedBy=multi-user.target
```

- reload the service file to include the new service

```bash
sudo systemctl daemon-reload
```

- start the service
```bash
sudo systemctl start <NameOfServiceYouJustCreated>.service
```

- check the status of your new service
```bash
sudo systemctl status <NameOfServiceYouJustCreated>.service
```

- enable your service on every reboot
```bash
sudo systemctl enable <NameOfServiceYouJustCreated>.service
```

- to disable your service on every reboot
```bash
sudo systemctl disable <NameOfServiceYouJustCreated>.service
```
<hr>


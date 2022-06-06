---
title: Instructions for Server 2019 Installation
---

If you happen to have a Server 2019 box up and running, here are the instructions to install Docker Enterprise and Docker-compose.

All commands are run from PowerShell.

### Prerequisites
Need to have both Hyper-V and Containers features installed on the server.

```
Install-WindowsFeature -Name Hyper-V,Containers -IncludeAllSubFeature -IncludeManagementTools
```
Once installed, reboot.
```
Restart-Computer -Force
```


### Install Docker Enterprise
```
Install-Module DockerMSFTProvider

Import-Module -Name DockerMSFTProvider -Force
Import-Packageprovider -Name DockerMSFTProvider -Force

Install-Package -Name Docker -Source DockerDefault
```

### Enable Linux Containers
```
[Environment]::SetEnvironmentVariable("LCOW_SUPPORTED", "1", "Machine")
```


### Create Daemon Config File
This creates a new daemon.json file.  If you already have one, then just edit it to add the ```"experimental": true``` value
```
$configfile = @"
{
    "experimental": true
}
"@
$configfile | Out-File -FilePath C:\ProgramData\docker\config\daemon.json -Encoding ascii -Force
```

### Install Linux Kernel
```
Invoke-WebRequest -Uri "https://github.com/linuxkit/lcow/releases/download/v4.14.35-v0.3.9/release.zip" -UseBasicParsing -OutFile release.zip
Expand-Archive release.zip -DestinationPath "$Env:ProgramFiles\Linux Containers\."
```

### Install Docker-compose
```
$dockerComposeVersion = "1.26.2"
Invoke-WebRequest "https://github.com/docker/compose/releases/download/$dockerComposeVersion/docker-compose-Windows-x86_64.exe" -UseBasicParsing -OutFile $Env:ProgramFiles\docker\docker-compose.exe
```

### [Get the code and start the server](../../configure)

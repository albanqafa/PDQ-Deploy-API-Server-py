# PDQ-Deploy-API-Server-py

I wanted PDQ Deploy to have an API server so i wrote one for it

You can use it to deploy packages that have been added to the whitelist in config.txt

It has basic regex matching for input sanitation (it only accepts package/computer names consisting of numbers, letters, and hyphens)

It does the server-side command execution with a different account, credentials of which go in config.txt

## Requirements:

-  [Python](https://www.python.org/downloads/windows/)
-  [Pywin32](https://pypi.org/project/pywin32/)

The account that does command execution must be a "Console User" in PDQ Deploy as well as part of the Windows "Administrators" group (more info [here](https://help.pdq.com/hc/en-us/articles/115002510472-PDQ-Credentials-Explained) and how to [here](https://www.pdq.com/blog/adding-console-users-explained/))

This API server can be configured as a Windows service with [NSSM](http://nssm.cc/) :

<img src="https://github.com/albanqafa/PDQ-Deploy-API-Server-py/assets/37601993/327e1bd5-d837-45c7-ad00-22a56103a0ab" width="400" height="200">

**NOTE: Unfortunately, right now it needs to be ran as LocalSystem to work as a Windows service**

## TODO:

-  figure out the specific permissions win32process.CreateProcessAsUser needs
-  OR switch to ctypes.windll.advapi32.CreateProcessWithLogonW (painful)

## How do i use this?

The server accepts requests via the URI /deploy/packagename/computername

Sending a request to it looks like this:

Invoke-WebRequest "http://your_pdq_server:8080/deploy/packagename/targetcomputer"

or this:

curl -X GET http://your_pdq_server:8080/deploy/packagename/targetcomputer

## Use cases:

Useful for login scripts to check if the user belongs to a group that should have a thing installed, and if its not installed tell PDQ to install it, etc.

PDQ Deploy does not have any way of installing software based on users group membership

The script [example_login_script.ps1](https://github.com/albanqafa/PDQ-Deploy-API-Server-py/blob/main/example_login_script.ps1) is included in this repo as an example

# PDQ-Deploy-API-Server-py

I wanted PDQ Deploy to have an API server so i wrote one for it

Very basic right now, supports deploying packages from a whitelist in config.txt

Basic regex matching for input sanitation (it only accepts package/computer names consisting of numbers, letters, and hyphens)

Also, it does the server-side command execution with a different account and psexec, credentials of which go in config.txt

The account that does command execution must be a "Console User" in PDQ Deploy (Info here: https://help.pdq.com/hc/en-us/articles/115002510472-PDQ-Credentials-Explained)

For some annoying reason, PDQ Deploy "Console Users" need to also be local Administrators to interface with PDQ

This API server accepts requests via the URI /deploy/packagename/computername

Sending a request to it with CURL looks like this:

curl -X GET http://your_pdq_server:8080/deploy/packagename/targetcomputer

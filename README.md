The code is inspired from https://www.pyimagesearch.com
Certain additions and modification has been done to extended use.

Certain parameters are defined in a json file like (ftp login/password) and time interval of capture.

Key modification include:
>> Storing the video on local disk when motion is detected.
>> ftp is used to transfer files to local server. (multi-threading is used)
>> storage optimization

The flowchart attached, explains the working of the project..
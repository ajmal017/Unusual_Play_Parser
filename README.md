Unusual WHales is a service that scans the options chain for activity that is deemed unusual by a certain metric.
There is a discord group (https://discord.gg/JQTyWq), a twitter feed (https://twitter.com/unusual_whales/) and the website (https://unusualwhales.com/) all dedicated to the franchise.

WHY I CREATED THE UNUSUAL WHALES PLAY PARSER
My program was born from the need to have all the plays in one file, to parse and examine as I see fit.
As of 06/16/20, there have been 8590 plays created by Unusual WHales to examine. That is a lot to go through, A LOT.
The website offers some filtering but it is not desirable to use and it not usable for daily use
The service has great potential but there is much that needs to be done before it is the gem that the author envisioned.

The program is simple in its workings. The plays are scrapped from the discord chat and downloaded into a json file. The plays are then added to a database
and can be sorted and filter to make it easier for the user to view. This is all thanks to Alexey Golub (https://github.com/Tyrrrz/DiscordChatExporter).
His program can download a discord channel's messages for specified dates and in html, txt, json or csv file formats. I could not have competed this without him.

To use this program, you need to down and install the .NET Core runtime*. 
https://github.com/sqlitebrowser/sqlitebrowser/releases/download/v3.12.0/DB.Browser.for.SQLite-3.12.0.dmg is a sql database browser, easy to use.
This program was designed for a Mac/Linux as the file uses back slashes (/) instead of forward slashes like Windows (\).
So you will need to changed the '/' to the escaped '\\' aka os.chdir("file/A") changes to os.chdir("file\\A") for Windows
In the download_plays function, 









.NET Core Runtime
Windows 64 bit: https://dotnet.microsoft.com/download/dotnet-core/thank-you/runtime-desktop-3.1.0-windows-x64-installer
Windows 32 bit: https://dotnet.microsoft.com/download/dotnet-core/thank-you/runtime-desktop-3.1.0-windows-x86-installer
Linux: https://docs.microsoft.com/en-us/dotnet/core/install/linux-package-manager-ubuntu-1904#install-the-net-core-runtime
Mac: https://dotnet.microsoft.com/download/dotnet-core/thank-you/runtime-3.1.0-macos-x64-installer
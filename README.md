This is a fun side project which is a single file discord bot written in python used to facilitate the game Resistance.

Resistance is a game of deception. Read the rules here: https://en.wikipedia.org/wiki/The_Resistance_%28game%29. Typically, this game is played with normal playing cards. Colors are used to assign roles. Anonymity is crucial for the game so having an impartial bot is essential for remote playing on discord with voice chat. This bot started, v1.0.0-v1.1.0, as a text based game where you would literally tell the bot who you were and what you wanted to do (voting and nominating, see the rules for more details).

Newer versions attempt to limit the amount of typing that needs to be done which improves the experience overall by being easier to play on discord mobile and reducing the chances for typos.

The current stable version is v1.1.1 (bot_1_1_1.py, I wrote these primarily on windows which explains the _ instead of the . in the file name). This is in the old_versions directory as this is not a serious project.

Updates for v1.1.1: 
  - Deprecated the results command. The bot will update the scores immediately at the end of the rounds.
  - Votes on nominated missions are handled by a poll

Updates for v1.1.2:
  - Nominating players for missions are now also handled by a poll

Known issues:
  - There are instances where rejecting missions have broken the game in both v1.1.1 and v1.1.2. This is currently being explored.

Requirements to make/run these bots:
- Need python 3.8.x
- discord.py
- dotenv
- Discord.com certificate

To set up your python bot with discord: https://realpython.com/how-to-make-a-discord-bot-python/

To get this certificate so your bot can access your server:
- Go to discord.com in Microsoft Edge
- Click on the lock to the left of the url
- On the pop up menu that appears on the right side of the window, select the certificate file (should be highlighted)
- Download this
- Find the file and double click, an install option should appear which leads to an install wizard
- After install, your python script bot can connect to discord

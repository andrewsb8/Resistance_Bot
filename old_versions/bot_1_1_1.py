#*************************************************************************************************************
#Python script that runs a discord bot responsible for moderating games of The Resistance.

#Author: Brian Andrews
#Last Date Modified: 1/8/2021
#*************************************************************************************************************

import os
import discord
from discord.ext import commands
from discord import User
from discord.ext.commands import Greedy
from discord.ext.commands import command, has_permissions
from discord import Embed
from dotenv import load_dotenv
import math
from random import randint
import string

#below is an array of numbers for use in an embedded discord poll
#numbers = ("1️⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟")

#********************************************************************************************************************
#Define game class below to store information and affect game
class Game:
    def __init__(self):
        self.active_game = 0
        self.channel_name = 0
        self.players = []
        self.num_players = 0
        self.assignments = [] #entries here are the assignment of Resistance (0) or Spy (1)
        self.players_on_mission = []
        self.mission_count = 1
        self.total_missions = 5
        self.nominator = -1 #index of players to nominate 
        self.num_nominated = [ #number of players to be nominated depending on the number of players (index 1) and mission_count (index 2)
            [2,3,2,3,3], #5 players
            [2,3,4,3,4], #6
            [2,3,3,4,4], #7
            [3,4,4,5,5], #8
            [3,4,4,5,5], #9
            [3,4,4,5,5] #10
            ] 
        self.current_vote = []
        self.votes = 0
        self.submissions = []
        self.submits = 0
        self.commie_score = 0
        self.resist_score = 0
        self.mission_history = []
        self.num_red = 0
        self.rejected_missions = 0
        self.max_rejected_missions = 3
        #self.numbers = ("1️⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣",  "🔟")  #numbers for nomination polls
        self.vote_numbers = ("1️⃣", "2⃣") #only need two options in poll, yes or no for approving missions
        #self.poll_type_options = ("Vote on Mission", "Nominations")
        #self.current_poll_type = "" #string to determine what type of poll needs to be read
        #self.poll_message_id = 0 #variable to store the message id of the poll to make sure reactions to other polls do not break the game
        self.submit_open = 0

    def start_game(self):
        self.active_game = 1
        return

    def in_current_game(self):
        if self.active_game == 1:
            return True
        else:
            return False

    def assign_spies(self, num_players):
        num_spies = math.ceil(num_players/3)
        who_are_spies = []

        x = -1
        for i in range(num_spies):
            if x == -1:
                x = randint(0, num_players-1)
                who_are_spies.append(x)

                self.assignments[x] = 1
            else:
                while len(who_are_spies) < num_spies:
                    x = randint(0, num_players-1)
                    if self.assignments[x] != 1:
                        self.assignments[x] = 1
                        who_are_spies.append(x)
            
        return
    

    async def message_assignments(self):
        for i in range(len(self.players)):
            #message Resistance
            if self.assignments[i] == 0:
                await self.players[i].send("You are Resistance. Stop those commies.")

            #message the spies
            if self.assignments[i] == 1:
                await self.players[i].send("You're a god damned commie.")

                #tell each spy who all of the spies are.
                for j in range(len(self.players)):
                    if self.assignments[j] == 1 and j != i:
                        await self.players[i].send("{} is also a god damned commie.".format(self.players[j]))

        return


    def update_vote(self, user, vote):
        if self.votes < self.num_players:
            for i in range(self.num_players):
                if user == self.players[i] and self.current_vote[i] == -1:
                    if vote == "yes":
                        self.current_vote[i] = 1
                        self.votes += 1
                        break
                    if vote == "no":
                        self.current_vote[i] = 0
                        self.votes += 1
                        break
        print(self.current_vote)
        

    def mission_fail(self):
        self.nominator = (self.nominator + 1) % 5
        self.players_on_mission = []
        self.current_vote = []
        self.votes = 0
        self.rejected_missions += 1

    def mission_fail_by_vote(self):
        self.nominator = (self.nominator + 1) % 5
        self.players_on_mission = []
        self.current_vote = []
        self.votes = 0
        self.rejected_missions = 0
        self.commie_score += 1
        self.mission_count += 1
        

    def player_on_mission(self, user):
        for player in game.players_on_mission:
            if player == user[0]:
                return True
        return False


    def update_submits(self, user, submit):
        if self.submits < len(self.players_on_mission):
            for i in range(len(self.players_on_mission)):
                if user[0] == self.players_on_mission[i] and self.submissions[i] == -1:
                    if submit == "red":
                        self.submissions[i] = 1
                        self.submits += 1
                        break
                    if submit == "black":
                        self.submissions[i] = 0
                        self.submits += 1
                        break
        print(self.submissions)

    #v1.1.1 update: removes the loop in place of a simple sum and adds condition that, for 7-10 players, the
    #fourth mission needs two fail cards
    def mission_success(self):
        if self.num_players >= 7 and self.mission_count == 4:
            print("There are >= 7 players and mission 4 requires two fail cards.\n")
            if sum(self.submissions) > 1:
                return False
        else:
            if sum(self.submissions) > 0:
                return False
        return True

   
    def how_many_commies(self):
        return sum(self.submissions)


    def check_win(self):
        if self.resist_score == 3 or self.commie_score == 3:
            return True
        return False


    def update_mission(self):
        self.mission_count += 1
        self.nominator = (self.nominator +1) % 5
        self.current_vote = []
        self.votes = 0
        self.submissions = []
        self.submits = 0
        self.num_red = 0
        self.players_on_mission = []


    def add_mission_history(self):
        self.mission_history.append([self.players_on_mission, self.resist_score,self.commie_score,self.num_red])


    async def create_poll(self, ctx, users, _title, prompt, poll_numbers, options, instructions):
        embed = Embed(title=_title, description=prompt)

        #create field entries by combining the options with the numbers of users
        options_string = ""
        for j in range(len(options)):
            options_string += poll_numbers[j] + " " + options[j] + "\n"
        
        fields = [("Options",  options_string, False),
                  ("Instructions", instructions, False)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        message = await ctx.send(embed=embed)

        for emoji in poll_numbers:
            await message.add_reaction(emoji)
        
        
#End class definition
#*******************************************************************************************************************

#*******************************************************************************************************************
#connect to discord, define commands, and execute bot

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='~')

#create class instance
game = Game()

#command to start a new game!
@bot.command(name='new_game')
async def new_game(ctx):
    if game.in_current_game():
        await ctx.send("There is already an active game. Please quit if you wish to start a new game!")
    else:
        game.start_game()
        game.channel_name = ctx.channel
        await ctx.send("Welcome to Resistance v1.1.1. Please provide the names of the players. Use commands (with ~ prefix) to learn the commands for this bot!\n\nUse the players command to provide the names of the players!")

#THIS COMMAND DOES NOT WORK AND NEEDS TO
#command to quit the current game or get called a quitter
@bot.command(name='quit_game')
async def quit_game(ctx):
    if game.in_current_game():
        del game
        game = Game() 
        await ctx.send("Thanks for playing, I guess.")
    else:
        await ctx.send("There is no active game currently. Please start one for you to quit, quitter.")


#command that gives the bot the player usernames, assigns them roles, and sends the roles out via dm on discord
@bot.command(name='players')
async def collect_assign_players(ctx, users: Greedy[User]):
    if game.in_current_game():
        if len(users) >= 5 and len(users) <= 10:
            game.players = users
            game.num_players = len(game.players)
            game.assignments = [0 for i in range(game.num_players)]

            #assign roles and message them to the players
            game.assign_spies(game.num_players)
            await game.message_assignments()

            #print assignments to console to verify the assignments are correct
            print(game.assignments)

            await ctx.send("Assignments are complete. Now expose these damn commies.")

            game.nominator = randint(0, game.num_players-1)
            await ctx.send("{} will now nominate {} players to go on the first mission.".format(game.players[game.nominator],game.num_nominated[game.num_players-5][game.mission_count-1]))
                
        else:
            await ctx.send("Bro this game only supports 5-10 players. Learn the rules.")
            
    else:
        await ctx.send("There is no active game currently. Please start one when you get friends!")


#next up are the missions, the person who is nominating the mission party submits usernames
#v1.1.1: this function then creates a poll for users to vote on.
@bot.command(name='mission')
async def missions(ctx, users: Greedy[User]):
    if game.in_current_game():
        if game.num_nominated[game.num_players-5][game.mission_count-1] == len(users):
            game.players_on_mission = users
            game.current_vote = [-1 for i in range(game.num_players)]
            
            instructions = "React with the options below to cast your vote. A majority (at least tie if number of players is even) needs to approve the decision."
            users_on_mission_string = ""
            for u in range(len(users)):
                users_on_mission_string += str(users[u].name) + " "
                
            await game.create_poll(ctx, users, "Vote on Current Mission", "Potential commies on mission: " + users_on_mission_string, game.vote_numbers, ("yes", "no"), instructions)
        else:
            await ctx.send("Please nominate only {} users.".format(game.num_nominated[game.num_players-5][game.mission_count-1]))

    else:
        await ctx.send("There is no active game currently. Please start one when you get friends!")

#v1.1.1: read poll for voting in place of previous vote command in v1.0.0
#To do: check to see if this works as a single function for multiple polls and if reacting in post to a previous poll fucks with this.
@bot.event
async def on_raw_reaction_add(payload):
    channel = await bot.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    #print(channel, message)

    print(message.id, payload.member, payload.emoji)

    if game.votes < game.num_players and payload.member.name != "Resistance-Bot":
        print("worked")
        if str(payload.emoji) == game.vote_numbers[0]:
            game.update_vote(payload.member,"yes")
        elif str(payload.emoji) == game.vote_numbers[1]:
            game.update_vote(payload.member,"no")
        else:
            await game.channel_name.send("Wrong emote. Read the rules. I bet you're the commie, " + str(payload.member) + ".")
            
    if game.votes == game.num_players:
        if sum(game.current_vote) > float(game.num_players/2):
            game.submissions = [-1 for i in range(len(game.players_on_mission))]
            await game.channel_name.send("The mission has passed. Users on mission please dm me your choice of card. If you are not a commie, you must submit black. Commies can choose red or black.")
            game.submit_open = 1
        else:
            if game.rejected_missions < game.max_rejected_missions:
                game.mission_fail()
                if game.rejected_missions < game.max_rejected_missions:
                    await game.channel_name.send("The mission has not passed. Now {} will nominate {} players for the mission".format(game.players[game.nominator],game.num_nominated[game.num_players-5][game.mission_count-1]))
            if game.rejected_missions >= game.max_rejected_missions:
                game.mission_fail_by_vote()
                if game.check_win():
                    game.active_game = 0
                    await game.channel_name.send("The game is over! Resistance - {} Commies - {}!".format(game.resist_score, game.commie_score))
                else:
                    await game.channel_name.send("The score is now Resistance - {} Commies - {}.".format(game.resist_score, game.commie_score))
                    await game.channel_name.send("The mission has not passed for the third time. Commies got a free point...... Now {} will nominate {} players for the mission".format(game.players[game.nominator],game.num_nominated[game.num_players-5][game.mission_count-1]))
                    game.add_mission_history()


@bot.command(name="submit")
async def submit_mission(ctx, users: Greedy[User], *args):
    if game.in_current_game() and game.submit_open == 1:
        if game.submits < len(game.players_on_mission):
            if game.player_on_mission(users):
                print("yeet")
                game.update_submits(users, args[0])
                
        #v1.1.1: This block was moved from the results command here for immediate results from the bot. This also sends information directly to a channel instead of 
        if game.submits == len(game.players_on_mission):
            game.submit_open = 0
            if game.mission_success(): 
                await game.channel_name.send("Mission success!")
                game.resist_score += 1
            else:
                await game.channel_name.send("Mission failed. Those commies got us!")
                game.num_red = game.how_many_commies()
                await game.channel_name.send("There were {} commie cards played!".format(game.num_red))
                game.commie_score += 1

            if game.check_win():
                game.active_game = 0
                await game.channel_name.send("The game is over! Resistance - {} Commies - {}!".format(game.resist_score, game.commie_score))
            else:
                await game.channel_name.send("The score is now Resistance - {} Commies - {}.".format(game.resist_score, game.commie_score))
                game.add_mission_history()
                game.update_mission()
                await game.channel_name.send("Now {} will nominate {} players for mission {}".format(game.players[game.nominator],game.num_nominated[game.num_players-5][game.mission_count-1],game.mission_count))
    elif game.submit_open == 0:
        await game.channel_name.send("You cannot submit mission cards to the bot at this time. A mission must be approved before submissions can be processed.")
    else:
        await ctx.send("*sigh*. YOU ARE NOT IN AN ACTIVE GAME")
        

@bot.command(name="mission_history")
async def mis_history(ctx):
    if len(game.mission_history) == 0:
        await ctx.send("There have been no missions yet you fool!")
    else:
        hist_string = "Mission x: users, Resistance Score, Commie Score, Number of Red cards played\n\n"
        for i in range(len(game.mission_history)):
            hist_string += "Mission " + str(i+1) + ": "
            if len(game.mission_history[i][0]) == 0:
                hist_string += "Mission stalled by voting"
            else:
                for j in range(len(game.mission_history[i][0])):
                    hist_string += str(game.mission_history[i][0][j]) + " "
            hist_string += ", "
            for k in range(1,len(game.mission_history[i]),1):
                hist_string += str(game.mission_history[i][k]) + ", "
            hist_string += "\n\n"
        await ctx.send(hist_string)
        #await ctx.send("{}".format(game.mission_history))

@bot.command(name="score")
async def give_score(ctx):
    await ctx.send("Resistance - {} Commies - {}.".format(game.resist_score, game.commie_score))

@bot.command(name="rules")
async def get_rules(ctx):
    await ctx.send("Welcome to The Resistance. I (the bot) help moderate this game via discord in order to keep things anonymous.\n\n"
                   "A complete rule set can be seen here: https://en.wikipedia.org/wiki/The_Resistance_(game) .\n\n"
                   "There are 5-10 players and there are two teams, The Resistance and The Spies. The number of spies are determined by dividing the number of players by 3 and taking the next highest integer.\n\n"
                   "Each round (called missions), I will determine a player to nominate a number of people which will go on the mission. The group will then vote to approve or disapprove the mission proposal. "
                   "Majority wins.\n\nThen, the players nominated will go on a mission by submitting either a red or black card to me via a DM. If you are Resistance, you can only submit black which indicates"
                   "mission success. Spies have a choice (which is the strategy for the spies) of red or black which is mission failure or success respectively. Any red cards indicate a mission failure."
                   "Then the next round happens. A mission success (all black submissions) grants The Resistance 1 point, mission failure (at least 1 red card) grants The Spies 1 point. First to 3 points wins."
                   "There are 5 total rounds.\n\n The Resistance want to determine who the Spies are and deny them access to missions through voting and cooperation. The Spies need to deceive and strategically"
                   "fail missions without giving themselves away.\n\nThe commands for this bot can be seen using the command... command. (~ followed by command)\n\nGood Luck!")

@bot.command(name="commands")
async def get_commands(ctx):
    await ctx.send("All commands have a '~' before them.\n\n"
                   "**Commands that directly affect the game:**\n"
                   "**new_game** : Start a new game. Ex: ~new_game\n\n"
                   "**players** : List the players in the game for the bot to assign roles to. Only 5-10 players will be accepted. Ex: ~players @Resistance-Bot (no plain text)\n\n"
                   "**mission** : Nominate players for a mission (number given by me, the bot). Ex: ~mission @user1 @user2\n\n"
                   "**vote** : v1.1.1: This command was deprecated and now is handled via a poll after the players command\n\n"
                   "**submit** : (Only use this command when DMing me, the bot) Submit black or red to help the mission succeed or completely ruin it. Ex: ~submit @yourself black/red (Resistance can only submit black). When the bot receives all of the mission submissions, the bot will automatically report the results to the channel where the game takes place.\n\n"
                   "**Extra commands not involved in controlling the game:**\n"
                   "**rules** : Print the rules. Ex: ~rules\n\n"
                   "**score** : Report the score so far. Ex: ~score\n\n"
                   "**mission_history** : See who went on what mission, the result, and how many red cards were played in that mission. Ex: ~mission_history")


      
    
#execute bot
bot.run(TOKEN)



#*************************************************************************************************************
#Python script that runs a discord bot responsible for moderating games of The Resistance.

#Author: Brian Andrews
#Last Date Modified: 6/14/2020
#*************************************************************************************************************

import os
import discord
from discord.ext import commands
from discord import User
from discord.ext.commands import Greedy
from dotenv import load_dotenv
import math
from random import randint

#********************************************************************************************************************
#Define game class below to store information and affect game
class Game:
    def __init__(self):
        self.active_game = 0
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
                    for who in who_are_spies:
                        if who != x:
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
                if user[0] == self.players[i] and self.current_vote[i] == -1:
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

    
    def mission_success(self):
        for x in self.submissions:
            if x == 1:
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
        await ctx.send("Welcome to Resistance. Please provide the names of the players")

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

            await ctx.send("Assignments are complete. Now expose these damn commies.")

            game.nominator = randint(0, game.num_players-1)
            await ctx.send("{} will now nominate {} players to go on the first mission.".format(game.players[game.nominator],game.num_nominated[game.num_players-5][game.mission_count-1]))
                
        else:
            await ctx.send("Bro this game only supports 5-10 players. Learn the rules.")
            
    else:
        await ctx.send("There is no active game currently. Please start one when you get friends!")

#next up are the missions, the person who is nominating the mission party submits usernames
@bot.command(name='mission')
async def collect_assign_players(ctx, users: Greedy[User]):
    if game.in_current_game():
        if game.num_nominated[game.num_players-5][game.mission_count-1] == len(users):
            game.players_on_mission = users
            game.current_vote = [-1 for i in range(game.num_players)]
            await ctx.send("Now vote whether or not to approve this mission. A majority needs to approve the decision.")
        else:
            await ctx.send("Please nominate only {} users.".format(game.num_nominated[game.num_players-5][game.mission_count-1]))

    else:
        await ctx.send("There is no active game currently. Please start one when you get friends!")

#each user votes by voting
@bot.command(name='vote')
async def collect_assign_players(ctx, users: Greedy[User], *args):
    if game.in_current_game():
        if game.votes < game.num_players:
            game.update_vote(users,args[0])
        if game.votes == game.num_players:
            if sum(game.current_vote) > float(game.num_players/2):
                game.submissions = [-1 for i in range(len(game.players_on_mission))]
                await ctx.send("The mission has passed. Users on mission please dm me your choice of card. If you are not a commie, you must submit black. Commies can choose red or black.")
            else:
                game.mission_fail()
                await ctx.send("The mission has not passed. Now {} will nominate {} players for the mission".format(game.players[game.nominator],game.num_nominated[game.num_players-5][game.mission_count-1]))
    else:
        await ctx.send("Unlike those *commies*, you can vote! But only AFTER you start a game!")


@bot.command(name="submit")
async def submit_mission(ctx, users: Greedy[User], *args):
    if game.in_current_game():
        if game.submits < len(game.players_on_mission):
            if game.player_on_mission(users):
                print("yeet")
                game.update_submits(users, args[0])
        if game.submits == len(game.players_on_mission):
            await ctx.send("You were the last to vote. Please use the results command in the channel to determine how the mission went!")
            
    else:
        await ctx.send("*sigh*. YOU ARE NOT IN AN ACTIVE GAME")


@bot.command(name="results")
async def mission_results(ctx):
    if game.in_current_game():
        if game.mission_success(): 
            await ctx.send("Mission success!")
            game.resist_score += 1
        else:
            await ctx.send("Mission failed. Those commies got us!")
            game.num_red = game.how_many_commies()
            await ctx.send("There were {} commie cards played!".format(game.num_red))
            game.commie_score += 1

        if game.check_win():
            game.active_game = 0
            await ctx.send("The game is over! Resistance - {} Commies - {}!".format(game.resist_score, game.commie_score))
        else:
            await ctx.send("The score is now Resistance - {} Commies - {}.".format(game.resist_score, game.commie_score))
            game.add_mission_history()
            game.update_mission()
            await ctx.send("Now {} will nominate {} players for mission {}".format(game.players[game.nominator],game.num_nominated[game.num_players-5][game.mission_count-1],game.mission_count))
    else:
        await ctx.send("...dude.")


@bot.command(name="mission_history")
async def mis_history(ctx):
    await ctx.send("{}".format(game.mission_history))

@bot.command(name="score")
async def give_score(ctx):
    await ctx.send("Resistance - {} Commies - {}.".format(game.resist_score, game.commie_score))
       
    
#execute bot
bot.run(TOKEN)



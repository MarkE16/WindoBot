import discord
import asyncio
from discord.ext.commands.errors import MissingPermissions
import praw
import youtube_api
import json
import random
#import googleapiclient.discovery
from discord.ext import commands
from youtube_api import youtube_api_utils
from youtube_api.youtube_api import YouTubeDataAPI, YoutubeDataApi
from private import token

client = commands.Bot(command_prefix='%', help_command=None, intents=discord.Intents().all())

reports = []
registoredUsers = {}
levels = {}
serverSettings = {}
sendToMods, sendToAdmins, sendToOwner = True, False, False

try:
	reports, registoredUsers, levels = json.load(open("reportsregisteredusers.py", "r"))
	serverSettings = json.load(open("settings.py", "r"))
except:
	print("[x] Couldn't load information.")

# Will set the bot to online.
@client.event
async def on_ready():
	await client.change_presence(status=discord.Status.online, activity=discord.Game("I'm currently in the ALPHA phase. Please reach out to Windo#8834 to report any issues."))
	print("Successfully went online.")

@client.event
async def on_message(message):
	global levels
	global registoredUsers

	user = message.author

	if user != client.user:
		try:
			if str(user.id) in registoredUsers[str(message.guild.id)]:
				levels[str(message.guild.id)][str(user.id)][1] -= random.randint(0, 10)
				json.dump((reports, registoredUsers, levels), open("reportsregisteredusers.py", "w"))
				if levels[str(message.guild.id)][str(user.id)][1] <= 0:
					levels[str(message.guild.id)][str(user.id)][0] = levels[str(message.guild.id)][str(user.id)][0] + 1
					levels[str(message.guild.id)][str(user.id)][1] = levels[str(message.guild.id)][str(user.id)][1] + 50 * levels[str(message.guild.id)][str(user.id)][2]
					levels[str(message.guild.id)][str(user.id)][2] = levels[str(message.guild.id)][str(user.id)][2] + 1
					await message.channel.send(f"{user} just leveled up to {levels[str(message.guild.id)][str(user.id)][0]}!")
		except:
			print(f"{user} isn't registered yet.")
		json.dump((reports, registoredUsers, levels), open("reportsregisteredusers.py", "w"))
	await client.process_commands(message)

@client.event
async def on_reaction_add(reaction, user):
	global levels

	ctx = reaction.message # Im used to ctx
	if user != client.user:
		if len(ctx.embeds) > 1:
			return
		# If the embed name is register...
		if ctx.embeds[0].title == "Register":
			# If they select "Yes"...
			if str(reaction) == "????":
				# If they're already registered...
				if str(user.id) in registoredUsers:
					return print(f"{user} already here...")
				registoredUsers[str(ctx.guild.id)].append(str(user.id))
				levels[str(ctx.guild.id)] = {str(user.id): [1, 100, 2]}
				print(levels)
				json.dump((reports, registoredUsers, levels), open("reportsregisteredusers.py", "w"))
				done = discord.Embed(title="Registered", description="Registration complete. You will now gain EXP and levels when talking on this server.")
				await ctx.channel.send(embed=done)
			else:
				close = discord.Embed(title="Denied", description="You denied to register. You will not be able to gain any EXP or levels until you register. If you change your mind, run the command again.")
				await ctx.channel.send(embed=close)
		else:
			print("No embed's found")

# Help command - Prints the list of commands.
@client.command()
@commands.has_permissions(send_messages=True)
async def help(ctx):
	embed = discord.Embed(title="Help | Need a command?", description=
	"<.> help - Lists out all commands.\n"
	"<.> changelog - View the changelog.\n"
	"<.> say  - Repeats the sender's message.\n"
	"<.> meme - Sends a meme. <Being developed>\n"
	"<.> play - Plays music in the voice channel <Being developed>\n"
	"<.> mute - Mute a user.\n"
	"<.> unmute - Unmute a user.\n"
	"<.> kick - Kicks a user.\n"
	"<.> ban - Ban a user.\n"
	"<.> unban - Unban a user.\n"
	"<.> report - Report a user to moderators.\n"
	"<.> level - View your or someone else's level.\n"
	"<.> settings - Alter certain settings to your liking.\n"
	"<.> dm - DM a user with a message (PLEASE DO NOT ABUSE THIS).\n"
	"<.> numguess - Play a number guessing game with 3 difficulties! [NEW!]"
	)
	return await ctx.channel.send(embed=embed)


# Will print an error if the user tries to use a command that does not exist.
@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandNotFound):
		await ctx.send(':x: This command does not exist. Please use a command that exists.')
		print(error)
	elif isinstance(error, commands.CommandError):
		print(error)

# Sends the about information about the bot
@client.command()
@commands.has_permissions(send_messages=True)
async def about(ctx):
	windo = await client.fetch_user(371802974470668321)
	aboutEmb = discord.Embed(title="About the Bot", description=
	"[ Github link here ]"
	)
	aboutEmb.add_field(name="WindoBot Alpha v1.3.0", value=f"Developed by: {windo}", inline=True)
	aboutEmb.set_thumbnail(url=client.user.avatar_url)
	return await ctx.channel.send(embed=aboutEmb)

# Deletes the sender's message, and sends the same message, as if the bot only said it, and not the sender!
@client.command()
@commands.has_permissions(send_messages=True)
async def say(ctx, message):
	await ctx.message.delete()
	return await ctx.channel.send(message)

@say.error
async def say_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.channel.send(":x: Missing required arguments to run this command.\n \nSyntax: `%say <message>`")

"""
**NOT WORKING**
Sends a random post from the subreddit "r/memes"
"""
# @client.command()
# async def meme(ctx):
	# reddit = praw.Reddit("")


	# #embed = discord.Embed(title=selected, description="Stuff")
	# #return await ctx.channel.send(embed=embed)
	# print()

"""
**NOT WORKING**
Plays a song!
"""
# @client.command()
# async def play(ctx, url):
# 	queue = []
# 	#song = YouTubeDataAPI.get

# Mute a person.
@client.command()
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, *, reason=None):
	guild = ctx.guild

	if member.guild_permissions.mute_members or member.guild_permissions.administrator or member.guild_permissions.ban_members or member.guild_permissions.kick_members:
		return await ctx.channel.send(":x: You cannot mute this person.")
	
	for role in member.roles:
		if role.name == "Muted" and not role.permissions.send_messages or not role.permissions.send_messages:
			return await ctx.channel.send(":x: This person is already muted.")
	
	for role in guild.roles:
		if role.name == "Muted" and not role.permissions.send_messages or not role.permissions.send_messages:
			await member.add_roles(role)
			return await ctx.channel.send(f":white_check_mark: Muted {member} for {reason}.")

@mute.error
async def mute_error(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.channel.send(":x: You do not have the valid permissions to run this command. Permissions needed: `manage_messages`.")
	elif isinstance(error, commands.MissingRequiredArgument):
		await ctx.channel.send(":x: Missing required arguments to run this command.\n \nSyntax: `%mute <@member/memberID> <reason>`")

# Unmute a person.
@client.command()
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member):
	if ctx.channel.permissions_for(member).send_messages:
		return await ctx.channel.send(":x: This person is not muted.")
	
	for role in member.roles:
		if role.name == "Muted" and not role.permissions.send_messages or not role.permissions.send_messages:
			await member.remove_roles(role)
			return await ctx.channel.send(f":white_check_mark: {member} was unmuted.")

@unmute.error
async def unmute_error(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.channel.send(":x: You do not have the valid permissions to run this command. Permissions needed: `manage_messages`.")
	elif isinstance(error, commands.MissingRequiredArgument):
		await ctx.channel.send(":x: Missing required arguments to run this command.\n \nSyntax: `%unmute <@member/memberID>`")

# Kick a person.
@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
	if member.guild_permissions.mute_members or member.guild_permissions.administrator or member.guild_permissions.ban_members or member.guild_permissions.kick_members:
		return await ctx.channel.send(":x: You cannot kick this person.")
	
	await member.kick(reason=reason)
	return await ctx.channel.send(f":white_check_mark: Kicked {member} for {reason}.")

@kick.error
async def kick_error(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.channel.send(":x: You do not have the valid permissions to run this command. Permissions needed: `kick_members`.")
	elif isinstance(error, commands.MissingRequiredArgument):
		await ctx.channel.send(":x: Missing required arguments to run this command.\n \nSyntax: `%kick <@member/memberID> <reason>`")

# Report a user.
@client.command()
@commands.has_permissions(send_messages=True)
@commands.cooldown(1, 20, commands.BucketType.user)
async def report(ctx, member: discord.Member, *, reason):
	global reports
	guild = ctx.guild

	if member.guild_permissions.administrator or member.guild_permissions.mute_members or member.guild_permissions.ban_members or member.guild_permissions.kick_members:
		discontinue = discord.Embed(title="Command Failure", description="This person has moderation powers, so this command cannot continue. Try someone else.")
		return await ctx.channel.send(embed=discontinue)
	
	user = str(member)
	reports.append(user)
	json.dump((reports, registoredUsers, levels), open("reportsregisteredusers.py", "w"))
	
	if serverSettings[str(ctx.guild.id)][0][0]:
		""" Code to send to moderators with the valid permissions """
		async for mem in guild.fetch_members():
			if mem != member.bot:
				if mem.guild_permissions.administrator or mem.guild_permissions.mute_members or mem.guild_permissions.ban_members or mem.guild_permissions.kick_members:
					if mem != client.user:
						await discord.DMChannel.send(mem, 
							"```\n"
							"[NEW REPORT]\n"
							f"Reported user: {member}\n"
							f"Reported for: {reason}\n"
							f"Report #{len(reports)}\n"
							"```"
						)
		print("Report successfully sent to moderators.")
	elif serverSettings[str(ctx.guild.id)][0][1]:
		async for mem in guild.fetch_members():
			if mem != member.bot:
				if mem.guild_permissions.administrator:
					if mem != client.user:
						await discord.DMChannel.send(mem, 
							"```\n"
							"[NEW REPORT]\n"
							f"Reported user: {member}\n"
							f"Reported for: {reason}\n"
							f"Report #{len(reports)}\n"
							"```"
						)
		print("Report sucessfully sent to administrators.")
	elif serverSettings[str(ctx.guild.id)][0][2]:
		owner = await client.fetch_user(ctx.guild.owner.id)
		await discord.DMChannel.send(owner, 
			"```\n"
			"[NEW REPORT]\n"
			f"Reported user: {member}\n"
			f"Reported for: {reason}\n"
			f"Report #{len(reports)}\n"
			"```"
		)
	success = discord.Embed(title="Success!", description="Your report was sent.")
	return await ctx.channel.send(embed=success)

@report.error
async def report_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.channel.send(":x: Missing required arguments to run this command.\n \nSyntax: `%report <@member/memberID> <reason>`")

# # Ban command
@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
  await member.ban(reason=reason)
  await ctx.channel.send(f':white_check_mark: Successfully banned {member} for {reason}.')

@ban.error
async def ban_error(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.channel.send(":x: You do not have the valid permissions to run this command. Permissions needed: `ban_members`.")
	elif isinstance(error, commands.MissingRequiredArgument):
		await ctx.channel.send(":x: Missing required arguments to run this command.\n \nSyntax: `%ban <@member/memberID> <reason>`")


# # # Unban Command
@client.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
	banned_users = await ctx.guild.bans()
	member_name, member_discriminator = member.split('#')

	for ban_entry in banned_users:
		user = ban_entry.user

		if(user.name, user.discriminator) == (member_name, member_discriminator):
			await ctx.guild.unban(user)
			await ctx.send(f':white_check_mark: Successfully unbanned {user.name}.')

@unban.error
async def unban_error(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.channel.send(":x: You do not have the valid permissions to run this command. Permissions needed: `ban_members`.")
	elif isinstance(error, commands.MissingRequiredArgument):
		await ctx.channel.send(":x: Missing required arguments to run this command.\n \nSyntax: `%unban <member#0000>`")

@client.command()
@commands.has_permissions(send_messages=True)
async def changelog(ctx):
	latestChangelog = discord.Embed(title="Changelog for Alpha v1.3.0", description=
		"- Added a command 'numguess'; A number guessing game with 3 difficulties.\n"
		"- Made a slight improvement to the mute command."
	)
	latestChangelog.add_field(name="Requested by", value=ctx.message.author, inline=True)
	return await ctx.channel.send(embed=latestChangelog)

@client.command()
@commands.has_permissions(send_messages=True)
async def numguess(ctx):
	difficulty = discord.Embed(title="Select Difficulty", description=
		"e) Easy\n"
		"m) Medium\n"
		"h) Hard"
	)
	difficulty.add_field(name="Type your answer.", value="e.g 'm' for medium mode.", inline=True)
	await ctx.channel.send(embed=difficulty)

	def check(m):
		return m.author.id == ctx.author.id

	message = await client.wait_for("message", check=check)

	if message.content.lower() == 'e':
		attempts = 5
		botNum = random.randint(1, 10)
		easyMode = discord.Embed(title="Number Guess Game | EASY MODE", description=
		"My number: ???"
		)
		easyMode.add_field(name="Type your answer", value=
		"Choose a number from 1-10.\n"
		f"Attempts remaining: {attempts}"
		)
		msg = await ctx.channel.send(embed=easyMode)

		while True:
			selection = await client.wait_for("message", check=check)

			# Try to convert the user's selection into an integer, and to also check if what they sent wasn't a string.
			try:
				guess = int(selection.content)
			except:
				return await ctx.channel.send(":x: You didn't input a number. Run the command again to try again.")

			await selection.delete() # Delete the user's selection.

			# Game Over if run out of attempts
			if attempts <= 1:
				return await ctx.channel.send(":x: Ops, looks like you ran out of attempts. Looks like I win!")
			
			# Check if the user's selection was out of range.
			if guess > 10 or guess < 1:
				await ctx.channel.send(":x: You cannot enter a number above or below the selected range.")
			
			# If the guess was wrong, then lose an attempt and keep going.
			if guess != botNum:
				attempts = attempts	- 1
				easyMode = discord.Embed(title="Number Guess Game | EASY MODE", description=
				"My number: ???"
				)
				easyMode.add_field(name="Type your answer", value=
				"Choose a number from 1-10.\n"
				f"Attempts remaining: {attempts}"
				)
				await msg.edit(embed=easyMode)
			elif guess == botNum:
				easyMode = discord.Embed(title="Number Guess Game | EASY MODE", description=
				f"My number: {botNum}"
				)
				easyMode.add_field(name="Type your answer", value=
				"Choose a number from 1-10.\n"
				f"Attempts remaining: {attempts}"
				)
				await msg.edit(embed=easyMode)
				return await ctx.channel.send("Good job! You won!")
			


	elif message.content.lower() == 'm':
		attempts = 13
		botNum = random.randint(1, 20)
		mediumMode = discord.Embed(title="Number Guess Game | MEDIUM MODE", description=
		"My number: ???"
		)
		mediumMode.add_field(name="Type your answer", value=
		"Choose a number from 1-20.\n"
		f"Attempts remaining: {attempts}"
		)
		msg = await ctx.channel.send(embed=mediumMode)

		while True:
			selection = await client.wait_for("message", check=check)

			# Try to convert the user's selection into an integer, and to also check if what they sent wasn't a string.
			try:
				guess = int(selection.content)
			except:
				return await ctx.channel.send(":x: You didn't input a number. Run the command again to try again.")

			await selection.delete() # Delete the user's selection.

			# Game Over if run out of attempts
			if attempts <= 1:
				return await ctx.channel.send(":x: Ops, looks like you ran out of attempts. Looks like I win!")
			
			# Check if the user's selection was out of range.
			if guess > 20 or guess < 1:
				await ctx.channel.send(":x: You cannot enter a number above or below the selected range.")
			
			# If the guess was wrong, then lose an attempt and keep going.
			if guess != botNum:
				attempts = attempts	- 1
				mediumMode = discord.Embed(title="Number Guess Game | MEDIUM MODE", description=
				"My number: ???"
				)
				mediumMode.add_field(name="Type your answer", value=
				"Choose a number from 1-20.\n"
				f"Attempts remaining: {attempts}"
				)
				await msg.edit(embed=mediumMode)
			elif guess == botNum:
				mediumMode = discord.Embed(title="Number Guess Game | MEDIUM MODE", description=
				f"My number: {botNum}"
				)
				mediumMode.add_field(name="Type your answer", value=
				"Choose a number from 1-20.\n"
				f"Attempts remaining: {attempts}"
				)
				await msg.edit(embed=mediumMode)
				return await ctx.channel.send("Good job! You won!")
	elif message.content.lower() == 'h':
		attempts = 18
		botNum = random.randint(1, 30)
		hardMode = discord.Embed(title="Number Guess Game | HARD MODE", description=
		"My number: ???"
		)
		hardMode.add_field(name="Type your answer", value=
		"Choose a number from 1-30.\n"
		f"Attempts remaining: {attempts}"
		)
		msg = await ctx.channel.send(embed=hardMode)

		while True:
			selection = await client.wait_for("message", check=check)

			# Try to convert the user's selection into an integer, and to also check if what they sent wasn't a string.
			try:
				guess = int(selection.content)
			except:
				return await ctx.channel.send(":x: You didn't input a number. Run the command again to try again.")

			await selection.delete() # Delete the user's selection.

			# Game Over if run out of attempts
			if attempts <= 1:
				return await ctx.channel.send(":x: Ops, looks like you ran out of attempts. Looks like I win!")
			
			# Check if the user's selection was out of range.
			if guess > 30 or guess < 1:
				await ctx.channel.send(":x: You cannot enter a number above or below the selected range.")
			
			# If the guess was wrong, then lose an attempt and keep going.
			if guess != botNum:
				attempts = attempts	- 1
				hardMode = discord.Embed(title="Number Guess Game | HARD MODE", description=
				"My number: ???"
				)
				hardMode.add_field(name="Type your answer", value=
				"Choose a number from 1-30.\n"
				f"Attempts remaining: {attempts}"
				)
				await msg.edit(embed=hardMode)
			elif guess == botNum:
				hardMode = discord.Embed(title="Number Guess Game | HARD MODE", description=
				f"My number: {botNum}"
				)
				hardMode.add_field(name="Type your answer", value=
				"Choose a number from 1-30.\n"
				f"Attempts remaining: {attempts}"
				)
				await msg.edit(embed=hardMode)
				return await ctx.channel.send("Good job! You won!")

# Opens the settings menu to change, you know, SETTINGS
@client.command()
@commands.has_permissions(send_messages=True)
async def settings(ctx):
	global serverSettings
	global sendToMods, sendToAdmins, sendToOwner
	active = ""
	
	if str(ctx.guild.id) not in serverSettings:
		serverSettings[str(ctx.guild.id)] = []
		print(serverSettings)
		serverSettings[str(ctx.guild.id)].append([sendToMods, sendToAdmins, sendToOwner])
		print(serverSettings)
	
	if serverSettings[str(ctx.guild.id)][0][0] is True:
		active = "Send to Mods"
	elif serverSettings[str(ctx.guild.id)][0][1] is True:
		active = "Send to Admins"
	elif serverSettings[str(ctx.guild.id)][0][2] is True:
		active = "Send to Owner"
	# else:
	# 	if [sendToMods, sendToAdmins, sendToOwner] in serverSettings[str(ctx.guild.id)]:
	# 		print("Boolean values already exist.")
	# 	else:
	# 		serverSettings[str(ctx.guild.id)].append([sendToMods, sendToAdmins, sendToOwner])
	# 		print(serverSettings)

	def check(m):
		return m.author.id == ctx.author.id

	main = discord.Embed(title="Settings | Need to change something?", description=
	"a) Change Report Receivers"
	)
	await ctx.channel.send(embed=main)
	message = await client.wait_for("message", check=check)

	if message.content.lower() == 'a':
		if ctx.message.author == ctx.guild.owner:
			reportSettings = discord.Embed(title="Change Who Receives Reports", description=
			"1) Send to people with moderator powers (e.g kick, mute, ban members).\n"
			"2) Send only to people with administrator powers.\n"
			"3) Send only to the owner of the server."
			)
			reportSettings.add_field(name="Current Active Setting", value=active, inline=True)
			await ctx.channel.send(embed=reportSettings)

			change = await client.wait_for("message", check=check)
			try:
				changeInt = int(change.content)
			except:
				await ctx.channel.send("Invalid choice. Rerun the command to try again.")
			if changeInt == 1:
				if serverSettings[str(ctx.guild.id)][0][0]:
					await ctx.channel.send(":x: This setting is already active.")
				else:
					serverSettings[str(ctx.guild.id)][0][0], serverSettings[str(ctx.guild.id)][0][1], serverSettings[str(ctx.guild.id)][0][2] = True, False, False
					await ctx.channel.send(":white_check_mark: Settings applied.")
					json.dump(serverSettings, open("settings.py", "w"))
			elif changeInt == 2:
				if serverSettings[str(ctx.guild.id)][0][1]:
					await ctx.channel.send(":x: This setting is already active.")
				else:
					serverSettings[str(ctx.guild.id)][0][0], serverSettings[str(ctx.guild.id)][0][1], serverSettings[str(ctx.guild.id)][0][2] = False, True, False
					await ctx.channel.send(":white_check_mark: Settings applied.")
					json.dump(serverSettings, open("settings.py", "w"))
			elif changeInt == 3:
				if serverSettings[str(ctx.guild.id)][0][2]:
					await ctx.channel.send(":x: This setting is already active.")
				else:
					serverSettings[str(ctx.guild.id)][0][0], serverSettings[str(ctx.guild.id)][0][1], serverSettings[str(ctx.guild.id)][0][2] = False, False, True
					await ctx.channel.send(":white_check_mark: Settings applied.")
					json.dump(serverSettings, open("settings.py", "w"))
			else:
				await ctx.channel.send("Invalid choice. Rerun the command to try again.")
		else:
			await ctx.channel.send(":x: Only the owner can edit this setting.")
	else:
		await ctx.channel.send("Invalid choice. Rerun the command to try again.")



# Opens the level profile of the user
@client.command()
@commands.has_permissions(send_messages=True)
async def level(ctx, member: discord.Member=None):
	global registoredUsers
	user = ctx.message.author

# If the user didn't specify anyone, and wants to check their own level
	if member is None:
		# If the user isn't registered in registeredUsers
		if str(ctx.guild.id) not in registoredUsers:
			registoredUsers[str(ctx.guild.id)] = []
		if str(user.id) not in registoredUsers[str(ctx.guild.id)]:
			register = discord.Embed(title="Register", description="You're not currently registered in this server to gain EXP and levels. Would you like to register to gain EXP and levels?")
			register.add_field(name="Click on a reaction to confirm.", value="Clicking on a reaction will advance the process.", inline=True)
			registerMsg = await ctx.channel.send(embed=register)
			await registerMsg.add_reaction("????")
			await registerMsg.add_reaction("????")
		else:
			for p in levels[str(ctx.guild.id)]:
				if p == str(user.id):
					userStats = discord.Embed(title=f"{user}'s Stats", description=
					f"Level: **{levels[str(ctx.guild.id)][str(user.id)][0]}**\n"
					f"EXP til next Level: **{levels[str(ctx.guild.id)][str(user.id)][1]}**"
					)
					userStats.add_field(name="Requested by", value=user, inline=True)
					userStats.set_thumbnail(url=user.avatar_url)
					await ctx.channel.send(embed=userStats)
	else:
		if member.bot:
			return await ctx.channel.send(":x: This person is a bot, so you cannot check their level.")
		if str(member.id) not in registoredUsers:
			error = discord.Embed(title="Command Failiure", description=
			"This user is currently **not registered** in this server. You can view their stats when they are registered."
			)
			await ctx.channel.send(embed=error)
		else:
			for p in levels[str(ctx.guild.id)]:
				if p == str(member.id):
					userStats = discord.Embed(title=f"{member}'s Stats", description=
					f"Level: **{levels[str(ctx.guild.id)][str(member.id)][0]}**\n"
					f"EXP til next Level: **{levels[str(ctx.guild.id)][str(member.id)][0]}**"
					)
					userStats.add_field(name="Requested by", value=user, inline=True)
					userStats.set_thumbnail(url=member.avatar_url)
					await ctx.channel.send(embed=userStats)

@client.command()
@commands.has_permissions(send_messages=True)
async def dm(ctx, member: discord.Member, *, message):
	
	receiver = await client.fetch_user(member.id)
	try:
		await discord.DMChannel.send(receiver, f"Message from {ctx.message.author}: {str(message)}")
	except:
		return await ctx.channel.send(":x: There seemed to be an issue when attempting to DM this user. It might be possible that the user has their DMs closed, or even has me blocked.")
	sent = discord.Embed(title="Success!", description=f"Your message was sent to {member}.")
	await ctx.channel.send(embed=sent)

@dm.error
async def dm_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.channel.send(":x: Missing required arguments to run this command.\n \nSyntax: `%dm <@member/memberID> <message>`")

client.run(token)
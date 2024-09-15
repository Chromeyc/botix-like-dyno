import discord
from discord.ext import commands
import json
import asyncio
import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Load configuration from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

# Set bot's activity
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name='Managing servers'))

# Helper function to check permissions
def check_permissions(ctx, required_permissions):
    user_permissions = ctx.author.permissions_in(ctx.channel)
    return all(getattr(user_permissions, perm, False) for perm in required_permissions)

# Lock command
@bot.tree.command(name='lock', description='Lock a channel for all roles except specified ones.')
async def lock(interaction: discord.Interaction, channel: discord.TextChannel):
    if not check_permissions(interaction, ['manage_channels']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    allowed_roles = [role.id for role in interaction.guild.roles if role.permissions.administrator or role.permissions.manage_messages]
    for role in interaction.guild.roles:
        if role.id not in allowed_roles:
            await channel.set_permissions(role, send_messages=False)
    
    await interaction.response.send_message(f"Channel {channel.mention} has been locked for all roles except allowed ones.")

# Slowmode command
@bot.tree.command(name='slowmode', description='Enable/disable slowmode for a channel or user.')
async def slowmode(interaction: discord.Interaction, mode: str, channel: discord.TextChannel, limit: int):
    if not check_permissions(interaction, ['manage_channels']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    if mode not in ['channel', 'user', 'discord']:
        await interaction.response.send_message("Invalid mode. Use 'channel', 'user', or 'discord'.")
        return

    if mode == 'channel':
        await channel.edit(slowmode_delay=limit)
        await interaction.response.send_message(f"Slowmode set to {limit} seconds for {channel.mention}.")
    elif mode == 'user':
        await interaction.response.send_message("User-specific slowmode is not supported in this implementation.")
    elif mode == 'discord':
        await interaction.response.send_message("Server-wide slowmode is not directly supported.")

# Addmod command
@bot.tree.command(name='addmod', description='Add a moderator role to a user.')
async def addmod(interaction: discord.Interaction, role: discord.Role):
    if not check_permissions(interaction, ['manage_roles']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Add moderator role to the user (custom logic needed)
    await interaction.user.add_roles(role)
    await interaction.response.send_message(f"Added {role.name} role to {interaction.user.mention}")

# Addadmin command
@bot.tree.command(name='addadmin', description='Grant full access to all commands to the mentioned user.')
async def addadmin(interaction: discord.Interaction, user: discord.Member):
    if not check_permissions(interaction, ['manage_roles']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Grant admin role to the user (custom logic needed)
    admin_role = discord.utils.get(interaction.guild.roles, name='Admin')
    if admin_role:
        await user.add_roles(admin_role)
        await interaction.response.send_message(f"Granted admin access to {user.mention}")
    else:
        await interaction.response.send_message("Admin role does not exist in this server.")

# AFK Commands
@bot.tree.command(name='afk', description='Set an AFK status to display when you are mentioned.')
async def afk(interaction: discord.Interaction, *, status: str):
    # Store AFK status in a database or cache
    # For demonstration, just sending a message
    await interaction.response.send_message(f"AFK status set to: {status}")

@bot.tree.command(name='afkreset', description='Reset the AFK status for a user.')
async def afkreset(interaction: discord.Interaction, user: discord.Member):
    # Remove AFK status from the database or cache
    # For demonstration, just sending a message
    await interaction.response.send_message(f"AFK status reset for {user.mention}")

# Info command
@bot.tree.command(name='info', description='Get bot info.')
async def info(interaction: discord.Interaction):
    await interaction.response.send_message(f"Bot name: {bot.user.name}\nBot ID: {bot.user.id}")

# Uptime command
@bot.tree.command(name='uptime', description='Get bot uptime.')
async def uptime(interaction: discord.Interaction):
    # Track the bot's start time
    start_time = datetime.datetime.utcnow()
    uptime_duration = datetime.datetime.utcnow() - start_time
    await interaction.response.send_message(f"Bot has been up for: {uptime_duration}")

# Example of additional commands
@bot.tree.command(name='avatar', description='Get a user\'s avatar.')
async def avatar(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(user.avatar.url)

@bot.tree.command(name='randomcolor', description='Generates a random hex color with preview.')
async def randomcolor(interaction: discord.Interaction):
    import random
    color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
    await interaction.response.send_message(f"Random color: {color}")

@bot.tree.command(name='membercount', description='Get the server member count.')
async def membercount(interaction: discord.Interaction):
    count = interaction.guild.member_count
    await interaction.response.send_message(f"Member count: {count}")

@bot.tree.command(name='remindme', description='Set a reminder.')
async def remindme(interaction: discord.Interaction, time: str, *, reminder: str):
    try:
        time = int(time)
        await asyncio.sleep(time)
        await interaction.response.send_message(f"Reminder: {reminder}")
    except ValueError:
        await interaction.response.send_message("Invalid time format. Use seconds.")

@bot.tree.command(name='whois', description='Get user information.')
async def whois(interaction: discord.Interaction, user: discord.Member):
    embed = discord.Embed(title=f"User Info: {user.name}", description=f"ID: {user.id}")
    embed.set_thumbnail(url=user.avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='purge', description='Delete a number of messages from a channel.')
async def purge(interaction: discord.Interaction, count: int):
    if not check_permissions(interaction, ['manage_messages']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    await interaction.channel.purge(limit=count)
    await interaction.response.send_message(f"Deleted {count} messages.")

@bot.tree.command(name='announce', description='Send an announcement using the bot.')
async def announce(interaction: discord.Interaction, channel: discord.TextChannel, *, message: str):
    if not check_permissions(interaction, ['manage_messages']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    await channel.send(message)
    await interaction.response.send_message(f"Announcement sent to {channel.mention}.")

@bot.tree.command(name='nick', description='Change the bot nickname.')
async def nick(interaction: discord.Interaction, *, new_nickname: str):
    if not check_permissions(interaction, ['manage_nicknames']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    await interaction.guild.me.edit(nick=new_nickname)
    await interaction.response.send_message(f"Nickname changed to {new_nickname}.")

@bot.tree.command(name='rolecolor', description='Change the color of a role.')
async def rolecolor(interaction: discord.Interaction, role: discord.Role, color: str):
    if not check_permissions(interaction, ['manage_roles']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    await role.edit(color=discord.Color(int(color.lstrip('#'), 16)))
    await interaction.response.send_message(f"Color of role {role.name} changed.")

@bot.tree.command(name='rolename', description='Change the name of a role.')
async def rolename(interaction: discord.Interaction, role: discord.Role, *, new_name: str):
    if not check_permissions(interaction, ['manage_roles']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    await role.edit(name=new_name)
    await interaction.response.send_message(f"Role name changed to {new_name}.")

@bot.tree.command(name='role', description='Add/remove a user to a role or roles.')
async def role(interaction: discord.Interaction, user: discord.Member, action: str, *roles: discord.Role):
    if not check_permissions(interaction, ['manage_roles']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    if action == 'add':
        for role in roles:
            await user.add_roles(role)
        await interaction.response.send_message(f"Added roles to {user.mention}.")
    elif action == 'remove':
        for role in roles:
            await user.remove_roles(role)
        await interaction.response.send_message(f"Removed roles from {user.mention}.")
    else:
        await interaction.response.send_message("Invalid action. Use 'add' or 'remove'.")

@bot.tree.command(name='temprole', description='Assign/unassign a temporary role to a user.')
async def temprole(interaction: discord.Interaction, user: discord.Member, time: str, role: discord.Role, *, reason: str = None):
    if not check_permissions(interaction, ['manage_roles']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    await user.add_roles(role)
    await interaction.response.send_message(f"Temporary role {role.name} assigned to {user.mention} for {time}.")

    # Remove role after time (handling needs to be implemented)
    await asyncio.sleep(int(time))
    await user.remove_roles(role)
    await interaction.response.send_message(f"Temporary role {role.name} removed from {user.mention}.")

@bot.tree.command(name='modlogs', description='Get a list of moderation logs for a user.')
async def modlogs(interaction: discord.Interaction, user: discord.Member, page: int = 1):
    if not check_permissions(interaction, ['view_audit_log']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Fetch logs (mock example)
    logs = f"Moderation logs for {user.mention} (Page {page})"
    await interaction.response.send_message(logs)

@bot.tree.command(name='warn', description='Warn a member.')
async def warn(interaction: discord.Interaction, user: discord.Member, *, reason: str):
    if not check_permissions(interaction, ['manage_roles']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Log warning (mock example)
    await interaction.response.send_message(f"Warned {user.mention} for reason: {reason}")

@bot.tree.command(name='warnings', description='Get warnings for a user.')
async def warnings(interaction: discord.Interaction, user: discord.Member):
    if not check_permissions(interaction, ['manage_roles']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Fetch warnings (mock example)
    warnings_list = f"Warnings for {user.mention}: None"
    await interaction.response.send_message(warnings_list)

@bot.tree.command(name='unban', description='Unban a member.')
async def unban(interaction: discord.Interaction, user_id: int, *, reason: str = None):
    if not check_permissions(interaction, ['ban_members']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    user = discord.Object(id=user_id)
    await interaction.guild.unban(user, reason=reason)
    await interaction.response.send_message(f"Unbanned {user_id}.")

@bot.tree.command(name='ban', description='Ban a member, with optional time limit.')
async def ban(interaction: discord.Interaction, user: discord.Member, limit: str = None, *, reason: str = None):
    if not check_permissions(interaction, ['ban_members']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    await interaction.guild.ban(user, reason=reason)
    await interaction.response.send_message(f"Banned {user.mention} for reason: {reason}")

@bot.tree.command(name='unmute', description='Unmute a member.')
async def unmute(interaction: discord.Interaction, user: discord.Member, *, reason: str = None):
    if not check_permissions(interaction, ['manage_roles']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Implement unmute logic here
    await interaction.response.send_message(f"Unmuted {user.mention}.")

@bot.tree.command(name='kick', description='Kick a member.')
async def kick(interaction: discord.Interaction, user: discord.Member, *, reason: str = None):
    if not check_permissions(interaction, ['kick_members']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    await user.kick(reason=reason)
    await interaction.response.send_message(f"Kicked {user.mention} for reason: {reason}")

@bot.tree.command(name='deafen', description='Deafen a member.')
async def deafen(interaction: discord.Interaction, user: discord.Member):
    if not check_permissions(interaction, ['manage_channels']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    await user.edit(deafen=True)
    await interaction.response.send_message(f"Deafened {user.mention}.")

@bot.tree.command(name='undeafen', description='Undeafen a member.')
async def undeafen(interaction: discord.Interaction, user: discord.Member):
    if not check_permissions(interaction, ['manage_channels']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    await user.edit(deafen=False)
    await interaction.response.send_message(f"Undeafened {user.mention}.")

@bot.tree.command(name='diagnose', description='Diagnose any command or module in the bot.')
async def diagnose(interaction: discord.Interaction, command_or_module: str):
    if not check_permissions(interaction, ['view_audit_log']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Diagnose command/module (mock example)
    diagnosis = f"Diagnosis of {command_or_module}: No issues found."
    await interaction.response.send_message(diagnosis)

@bot.tree.command(name='rolepersist', description='Assign/unassign a role that persists if the user leaves and rejoins.')
async def rolepersist(interaction: discord.Interaction, user: discord.Member, role: discord.Role, action: str, *, reason: str = None):
    if not check_permissions(interaction, ['manage_roles']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    if action == 'add':
        # Add role persistently (mock example)
        await interaction.response.send_message(f"Role {role.name} added to {user.mention} persistently.")
    elif action == 'remove':
        # Remove role persistently (mock example)
        await interaction.response.send_message(f"Role {role.name} removed from {user.mention} persistently.")
    elif action == 'toggle':
        # Toggle role persistence (mock example)
        await interaction.response.send_message(f"Toggled role {role.name} for {user.mention}.")
    else:
        await interaction.response.send_message("Invalid action. Use 'add', 'remove', or 'toggle'.")

@bot.tree.command(name='softban', description='Softban a member (ban and immediate unban to delete user messages).')
async def softban(interaction: discord.Interaction, user: discord.Member, *, reason: str = None):
    if not check_permissions(interaction, ['ban_members']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    await interaction.guild.ban(user, reason=reason)
    await interaction.guild.unban(user)
    await interaction.response.send_message(f"Softbanned {user.mention} for reason: {reason}")

@bot.tree.command(name='modlogs', description='Get a list of moderation logs for a user.')
async def modlogs(interaction: discord.Interaction, user: discord.Member, page: int = 1):
    if not check_permissions(interaction, ['view_audit_log']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Fetch logs (mock example)
    logs = f"Moderation logs for {user.mention} (Page {page})"
    await interaction.response.send_message(logs)

@bot.tree.command(name='note', description='Add note(s) about a member.')
async def note(interaction: discord.Interaction, user: discord.Member, *, text: str):
    if not check_permissions(interaction, ['manage_roles']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Add note (mock example)
    await interaction.response.send_message(f"Added note to {user.mention}: {text}")

@bot.tree.command(name='notes', description='Get notes for a user.')
async def notes(interaction: discord.Interaction, user: discord.Member):
    if not check_permissions(interaction, ['manage_roles']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Fetch notes (mock example)
    notes_list = f"Notes for {user.mention}: None"
    await interaction.response.send_message(notes_list)

@bot.tree.command(name='delnote', description='Delete a note about a member.')
async def delnote(interaction: discord.Interaction, user: discord.Member, note_id: int):
    if not check_permissions(interaction, ['manage_roles']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Delete note (mock example)
    await interaction.response.send_message(f"Deleted note {note_id} for {user.mention}.")

@bot.tree.command(name='editnote', description='Edit a note about a member.')
async def editnote(interaction: discord.Interaction, user: discord.Member, note_id: int, *, new_note: str):
    if not check_permissions(interaction, ['manage_roles']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Edit note (mock example)
    await interaction.response.send_message(f"Edited note {note_id} for {user.mention}: {new_note}")

@bot.tree.command(name='clearnotes', description='Delete all notes for a member.')
async def clearnotes(interaction: discord.Interaction, user: discord.Member):
    if not check_permissions(interaction, ['manage_roles']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Clear all notes (mock example)
    await interaction.response.send_message(f"Cleared all notes for {user.mention}.")

@bot.tree.command(name='delwarn', description='Delete a warning.')
async def delwarn(interaction: discord.Interaction, warning_id: int):
    if not check_permissions(interaction, ['manage_roles']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Delete warning (mock example)
    await interaction.response.send_message(f"Deleted warning {warning_id}.")

@bot.tree.command(name='modstats', description='Get moderation statistics for a mod/admin.')
async def modstats(interaction: discord.Interaction, user: discord.Member):
    if not check_permissions(interaction, ['view_audit_log']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Fetch stats (mock example)
    stats = f"Moderation stats for {user.mention}"
    await interaction.response.send_message(stats)

@bot.tree.command(name='duration', description='Change the duration of a mute/ban.')
async def duration(interaction: discord.Interaction, modlog_id: int, limit: str):
    if not check_permissions(interaction, ['manage_roles']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Change duration (mock example)
    await interaction.response.send_message(f"Changed duration for modlog ID {modlog_id} to {limit}.")

@bot.tree.command(name='lockdown', description='Lock channels defined in moderation settings.')
async def lockdown(interaction: discord.Interaction, *, message: str = None):
    if not check_permissions(interaction, ['manage_channels']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Lockdown logic (mock example)
    await interaction.response.send_message(f"Channels locked down. {message if message else ''}")

@bot.tree.command(name='star', description='View starboard stats for a message.')
async def star(interaction: discord.Interaction, message_id: int):
    if not check_permissions(interaction, ['view_audit_log']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Fetch starboard stats (mock example)
    stats = f"Starboard stats for message ID {message_id}"
    await interaction.response.send_message(stats)

# Command to add an AFK status
@bot.tree.command(name='afk', description='Set an AFK status.')
async def afk(interaction: discord.Interaction, *, status: str):
    await interaction.response.send_message(f"AFK status set to: {status}")

# Command to reset AFK status
@bot.tree.command(name='afkreset', description='Reset AFK status for a user.')
async def afkreset(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(f"AFK status reset for {user.mention}")

# Command to get a user's avatar
@bot.tree.command(name='avatar', description='Get a user\'s avatar.')
async def avatar(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(user.avatar.url)

# Command to generate a random color
@bot.tree.command(name='randomcolor', description='Generate a random hex color.')
async def randomcolor(interaction: discord.Interaction):
    import random
    color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
    await interaction.response.send_message(f"Random color: {color}")

# Command to get server member count
@bot.tree.command(name='membercount', description='Get the server member count.')
async def membercount(interaction: discord.Interaction):
    count = interaction.guild.member_count
    await interaction.response.send_message(f"Member count: {count}")

# Command to set a reminder
@bot.tree.command(name='remindme', description='Set a reminder.')
async def remindme(interaction: discord.Interaction, time: str, *, reminder: str):
    try:
        time = int(time)
        await asyncio.sleep(time)
        await interaction.response.send_message(f"Reminder: {reminder}")
    except ValueError:
        await interaction.response.send_message("Invalid time format. Use seconds.")

# Command to get user information
@bot.tree.command(name='whois', description='Get user information.')
async def whois(interaction: discord.Interaction, user: discord.Member):
    embed = discord.Embed(title=f"User Info: {user.name}", description=f"ID: {user.id}")
    embed.set_thumbnail(url=user.avatar.url)
    await interaction.response.send_message(embed=embed)

# Command to roll dice
@bot.tree.command(name='roll', description='Roll a dice.')
async def roll(interaction: discord.Interaction, size: str, number_of_dice: int = 1):
    import random
    dice_sizes = {'d4': 4, 'd6': 6, 'd8': 8, 'd10': 10, 'd12': 12, 'd20': 20, 'd100': 100}
    if size not in dice_sizes:
        await interaction.response.send_message("Invalid dice size. Use d4, d6, d8, d10, d12, d20, d100.")
        return

    rolls = [random.randint(1, dice_sizes[size]) for _ in range(number_of_dice)]
    await interaction.response.send_message(f"Rolled {', '.join(map(str, rolls))}")

# Command to flip a coin
@bot.tree.command(name='flipcoin', description='Flip a coin.')
async def flipcoin(interaction: discord.Interaction):
    import random
    result = random.choice(['Heads', 'Tails'])
    await interaction.response.send_message(f"Coin flip result: {result}")

# Command to get server info
@bot.tree.command(name='serverinfo', description='Get server info/stats.')
async def serverinfo(interaction: discord.Interaction):
    embed = discord.Embed(title=f"Server Info: {interaction.guild.name}")
    embed.add_field(name="Total Members", value=interaction.guild.member_count)
    embed.add_field(name="Server Region", value=interaction.guild.region)
    await interaction.response.send_message(embed=embed)

# Command to generate a Dyno-like avatar
@bot.tree.command(name='dynoav', description='Generate a Dyno-like avatar.')
async def dynoav(interaction: discord.Interaction, user: discord.Member = None):
    # Placeholder: generate a simple avatar
    avatar_url = user.avatar.url if user else interaction.guild.icon.url
    await interaction.response.send_message(avatar_url)

# Command to get distance between two coordinates
@bot.tree.command(name='distance', description='Get the distance between two sets of coordinates.')
async def distance(interaction: discord.Interaction, coords1: str, coords2: str):
    # Placeholder: calculate distance (mock example)
    await interaction.response.send_message(f"Distance between {coords1} and {coords2} is unknown.")

# Command to show a color using hex
@bot.tree.command(name='color', description='Show a color using hex.')
async def color(interaction: discord.Interaction, hex_code: str):
    embed = discord.Embed(title=f"Color: {hex_code}", color=int(hex_code.lstrip('#'), 16))
    await interaction.response.send_message(embed=embed)

# Command to list server emojis
@bot.tree.command(name='emotes', description='Get a list of server emojis.')
async def emotes(interaction: discord.Interaction, search: str = None):
    emojis = [emoji for emoji in interaction.guild.emojis if search in emoji.name] if search else interaction.guild.emojis
    emoji_list = ' '.join(str(emoji) for emoji in emojis)
    await interaction.response.send_message(f"Emojis: {emoji_list}")

# Command to get COVID-19 stats
@bot.tree.command(name='covid', description='Get COVID-19 stats.')
async def covid(interaction: discord.Interaction, location: str = None):
    # Placeholder: Fetch COVID-19 stats (mock example)
    await interaction.response.send_message(f"COVID-19 stats for {location if location else 'global'} are unknown.")

# Command to get highlights
@bot.tree.command(name='highlights', description='Get notified when a specific phrase is said in a server.')
async def highlights(interaction: discord.Interaction, action: str, phrase: str):
    # Placeholder: Manage highlights (mock example)
    await interaction.response.send_message(f"Highlights {action} for phrase: {phrase}")

# Command to clean up responses
@bot.tree.command(name='clean', description='Clean up bot responses.')
async def clean(interaction: discord.Interaction, number: int = None):
    if not check_permissions(interaction, ['manage_messages']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Clean responses (mock example)
    await interaction.response.send_message(f"Cleaned up {number if number else 'all'} responses.")

# Command to deafen a member
@bot.tree.command(name='deafen', description='Deafen a member.')
async def deafen(interaction: discord.Interaction, user: discord.Member):
    if not check_permissions(interaction, ['manage_channels']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    await user.edit(deafen=True)
    await interaction.response.send_message(f"Deafened {user.mention}.")

# Command to undeafen a member
@bot.tree.command(name='undeafen', description='Undeafen a member.')
async def undeafen(interaction: discord.Interaction, user: discord.Member):
    if not check_permissions(interaction, ['manage_channels']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    await user.edit(deafen=False)
    await interaction.response.send_message(f"Undeafened {user.mention}.")

# Command to manage active moderations
@bot.tree.command(name='active_mods', description='Manage active moderations.')
async def active_mods(interaction: discord.Interaction, action: str, mod_id: int):
    if not check_permissions(interaction, ['view_audit_log']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Manage active moderations (mock example)
    await interaction.response.send_message(f"Active moderation {action} for mod ID {mod_id}.")

# Command to set a custom command
@bot.tree.command(name='addcustomcmd', description='Add a custom command.')
async def addcustomcmd(interaction: discord.Interaction, command_name: str, *, response: str):
    if not check_permissions(interaction, ['manage_guild']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Add custom command (mock example)
    await interaction.response.send_message(f"Custom command '{command_name}' added with response: {response}")

# Command to list custom commands
@bot.tree.command(name='listcustomcmds', description='List all custom commands.')
async def listcustomcmds(interaction: discord.Interaction):
    if not check_permissions(interaction, ['manage_guild']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # List custom commands (mock example)
    commands_list = "Custom commands: None"
    await interaction.response.send_message(commands_list)

# Command to delete a custom command
@bot.tree.command(name='delcustomcmd', description='Delete a custom command.')
async def delcustomcmd(interaction: discord.Interaction, command_name: str):
    if not check_permissions(interaction, ['manage_guild']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Delete custom command (mock example)
    await interaction.response.send_message(f"Custom command '{command_name}' deleted.")

# Command to get the bot's ping
@bot.tree.command(name='ping', description='Get the bot\'s ping.')
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Bot ping is {round(bot.latency * 1000)}ms")

# Command to add a user to the starboard
@bot.tree.command(name='starboard', description='Add a message to the starboard.')
async def starboard(interaction: discord.Interaction, message_id: int):
    if not check_permissions(interaction, ['manage_messages']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Add message to starboard (mock example)
    await interaction.response.send_message(f"Message ID {message_id} added to starboard.")

# Command to unlock a channel
@bot.tree.command(name='unlock', description='Unlock a channel for all roles.')
async def unlock(interaction: discord.Interaction, channel: discord.TextChannel):
    if not check_permissions(interaction, ['manage_channels']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Unlock channel (mock example)
    await interaction.response.send_message(f"Channel {channel.mention} unlocked.")

# Command to manage role mentions
@bot.tree.command(name='management', description='Manage role mentions.')
async def management(interaction: discord.Interaction, action: str, role: discord.Role):
    if not check_permissions(interaction, ['manage_roles']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    if action == 'enable':
        # Enable role mentions (mock example)
        await interaction.response.send_message(f"Role {role.name} mentions enabled.")
    elif action == 'disable':
        # Disable role mentions (mock example)
        await interaction.response.send_message(f"Role {role.name} mentions disabled.")
    else:
        await interaction.response.send_message("Invalid action. Use 'enable' or 'disable'.")

# Command to clean up message history
@bot.tree.command(name='cleanhistory', description='Clean up message history.')
async def cleanhistory(interaction: discord.Interaction, number: int):
    if not check_permissions(interaction, ['manage_messages']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    # Clean up message history (mock example)
    await interaction.response.send_message(f"Cleaned up {number} messages.")

# Command to add or remove a role from a user
@bot.tree.command(name='role', description='Add or remove a role from a user.')
async def role(interaction: discord.Interaction, user: discord.Member, role: discord.Role, action: str):
    if not check_permissions(interaction, ['manage_roles']):
        await interaction.response.send_message("You don't have permission to use this command.")
        return

    if action == 'add':
        await user.add_roles(role)
        await interaction.response.send_message(f"Role {role.name} added to {user.mention}.")
    elif action == 'remove':
        await user.remove_roles(role)
        await interaction.response.send_message(f"Role {role.name} removed from {user.mention}.")
    else:
        await interaction.response.send_message("Invalid action. Use 'add' or 'remove'.")

# Run the bot
bot.run('YOUR_BOT_TOKEN') 

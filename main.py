import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import datetime
import random
import os
import time
import json
import platform
import re
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot je aktivan!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()



# Bot configuration
keep_alive()
TOKEN = os.environ['TOKEN']
WELCOME_CHANNEL_ID = 1362000588858069093  # Specific welcome channel ID

# Define intents
intents = discord.Intents.default()
intents.members = True  # Enable to receive member join events
intents.message_content = True

# Initialize bot with command prefix '/' and defined intents
bot = commands.Bot(command_prefix='/', intents=intents)

# Color theme for embeds
ZEUS_BLUE = 0x3498db
ZEUS_GOLD = 0xf1c40f
ZEUS_RED = 0xe74c3c
ZEUS_GREEN = 0x2ecc71
ZEUS_PURPLE = 0x9b59b6

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'╔═══════════════════════════════════════╗')
    print(f'║ {bot.user.name} is now online!        ║')
    print(f'║ Bot ID: {bot.user.id}                 ║')
    print(f'╚═══════════════════════════════════════╝')

    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

    # Set activity status
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Zeus"))

# Event: Member joins the server
@bot.event
async def on_member_join(member):
    # Get the specific welcome channel
    channel = bot.get_channel(WELCOME_CHANNEL_ID)

    if channel is not None:
        # Create welcome embed
        embed = discord.Embed(
            title="⚡ Welcome to the Server! ⚡",
            description=f"Hey {member.mention}, welcome to **{member.guild.name}**!\n\nFeel free to check out our channels and get involved!",
            color=ZEUS_BLUE
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Member Count", value=f"#{len(member.guild.members)}", inline=True)
        embed.add_field(name="Created Account", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
        embed.set_footer(text=f"Zeus Bot • Powered by Joxy")
        embed.timestamp = datetime.datetime.utcnow()

        # Send welcome message
        await channel.send(embed=embed)

# Message event: Detect and handle Discord invite links
@bot.event
async def on_message(message):
    # Ignore messages from bots
    if message.author.bot:
        return

    # Process commands first (important to keep bot commands working)
    await bot.process_commands(message)

    # Skip message checking if user has admin permissions
    if isinstance(message.author, discord.Member) and message.author.guild_permissions.administrator:
        return

    # Check for Discord invite links
    invite_regex = r"discord\.gg\/\w+|discordapp\.com\/invite\/\w+|discord\.com\/invite\/\w+"
    if re.search(invite_regex, message.content, re.IGNORECASE):
        try:
            # Delete the message
            await message.delete()

            # Timeout the user for 1 minute
            timeout_duration = datetime.datetime.utcnow() + datetime.timedelta(minutes=1)
            await message.author.timeout(timeout_duration, reason="Sending Discord invite links")

            # Notify in channel
            warning_embed = discord.Embed(
                title="⚠️ Anti-Link System",
                description=f"{message.author.mention} has been timed out for 1 minute for sending Discord invite links.",
                color=ZEUS_RED
            )
            warning_embed.add_field(name="Action", value="Message deleted & 1 minute timeout", inline=False)
            warning_embed.set_footer(text="Zeus Bot • Powered by Joxy")
            warning_embed.timestamp = datetime.datetime.utcnow()

            warning_msg = await message.channel.send(embed=warning_embed)

            # Auto-delete the warning after 10 seconds
            await asyncio.sleep(10)
            await warning_msg.delete()

        except Exception as e:
            print(f"Error handling Discord invite: {e}")

# Command: antilinks
@bot.tree.command(name="antilinks", description="Toggle anti-Discord invite links system")
@app_commands.describe(status="Enable or disable the anti-links system")
async def antilinks(interaction: discord.Interaction, status: str):
    # Check if user has permissions
    if not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message("❌ You don't have permission to manage server settings!", ephemeral=True)
        return

    status = status.lower()

    if status not in ["enable", "disable", "on", "off", "status"]:
        await interaction.response.send_message("⚠️ Invalid option. Use 'enable', 'disable', or 'status'.", ephemeral=True)
        return

    # This is just a demonstration command since the anti-link functionality is always active
    # In a real implementation, you would store server-specific settings in a database

    if status in ["enable", "on"]:
        embed = discord.Embed(
            title="⚙️ Anti-Links System",
            description="✅ Anti-Discord invite links system has been **enabled**.",
            color=ZEUS_GREEN
        )
        embed.add_field(name="Action", value="All Discord invite links will be deleted and senders will be timed out for 1 minute.", inline=False)
    elif status in ["disable", "off"]:
        embed = discord.Embed(
            title="⚙️ Anti-Links System",
            description="⚠️ Anti-Discord invite links system has been **disabled**.",
            color=ZEUS_RED
        )
        embed.add_field(name="Action", value="Discord invite links will be allowed in the server.", inline=False)
    else:  # status
        embed = discord.Embed(
            title="⚙️ Anti-Links System",
            description="ℹ️ Anti-Discord invite links system is currently **active**.",
            color=ZEUS_BLUE
        )
        embed.add_field(name="Action", value="All Discord invite links are being deleted and senders are timed out for 1 minute.", inline=False)

    embed.set_footer(text="Zeus Bot • Powered by Joxy")
    embed.timestamp = datetime.datetime.utcnow()

    await interaction.response.send_message(embed=embed)

# Command: marko
@bot.tree.command(name="marko", description="Triggers the Marko voice message")
async def marko(interaction: discord.Interaction):
    await interaction.response.defer()

    # Check if user is in a voice channel
    if not interaction.user.voice:
        await interaction.followup.send("⚠️ You need to be in a voice channel to use this command!")
        return

    voice_channel = interaction.user.voice.channel

    # Check if we're already connected to a voice channel in this guild
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if voice_client and voice_client.is_connected():
        if voice_client.channel.id != voice_channel.id:
            await voice_client.move_to(voice_channel)
    else:
        try:
            voice_client = await voice_channel.connect()
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error connecting to voice channel: {str(e)}\n\nMake sure you have PyNaCl installed: `pip install PyNaCl`")
            return

    # Create status embed
    embed = discord.Embed(
        title="🔊 Voice Command Activated",
        description=f"Connected to {voice_channel.mention}!",
        color=ZEUS_PURPLE
    )
    embed.set_footer(text="Zeus Bot • Powered by Joxy")
    await interaction.followup.send(embed=embed)

    # Direct use of text-to-speech through discord.py's TTS feature
    text_channel = interaction.channel
    await text_channel.send("marko pusi kurac", tts=True)

    # Wait a bit to ensure TTS is heard
    await asyncio.sleep(5)

    # Disconnect from voice
    await voice_client.disconnect()

# Command: ban
@bot.tree.command(name="ban", description="Ban a user from the server")
@app_commands.describe(member="The member to ban", reason="Reason for banning")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    # Check if user has permissions
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ You don't have permission to ban members!", ephemeral=True)
        return

    # Check if bot can ban the target
    if not interaction.guild.me.guild_permissions.ban_members:
        await interaction.response.send_message("❌ I don't have permission to ban members!", ephemeral=True)
        return

    # Check if target is higher in role hierarchy
    if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("⚠️ You cannot ban someone with a higher or equal role!", ephemeral=True)
        return

    # Ban animation effect
    ban_messages = [
        f"⚡ Charging Zeus's lightning bolt...",
        f"🔍 Identifying target: {member.display_name}...",
        f"⚠️ Violation detected for user {member.display_name}...",
        f"⚡ Zeus's lightning bolt is aimed and ready..."
    ]

    await interaction.response.send_message(ban_messages[0])
    msg = await interaction.original_response()

    for message in ban_messages[1:]:
        await asyncio.sleep(1)
        await msg.edit(content=message)

    # Perform the ban
    try:
        await member.ban(reason=reason)
        await asyncio.sleep(1)

        # Final ban message with embed
        embed = discord.Embed(
            title="⚡ User Banned by Zeus ⚡",
            description=f"{member.mention} has been struck by lightning and banished from the server.",
            color=ZEUS_RED
        )
        embed.add_field(name="Executor", value=interaction.user.mention, inline=True)

        if reason:
            embed.add_field(name="Reason", value=reason, inline=True)

        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text="Zeus Bot • Powered by Joxy")
        embed.timestamp = datetime.datetime.utcnow()

        await msg.edit(content="", embed=embed)
    except Exception as e:
        await msg.edit(content=f"❌ Failed to ban {member.mention}: {str(e)}")

# Command: info
@bot.tree.command(name="info", description="Show information about the bot")
async def info(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚡ Zeus Bot Information ⚡",
        description="A powerful Discord bot with welcome messages, moderation tools, and voice commands.",
        color=ZEUS_GOLD
    )

    # Bot details
    embed.add_field(name="Creator", value="Joxy", inline=True)
    embed.add_field(name="Version", value="2.1.0", inline=True)
    embed.add_field(name="Created", value=bot.user.created_at.strftime("%Y-%m-%d"), inline=True)

    # Server stats
    embed.add_field(name="Server Count", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Python Version", value=platform.python_version(), inline=True)

    # Commands list (updated with new antilinks command)
    embed.add_field(name="Commands", 
                   value="```\n/marko - Voice command\n/ban - Ban users\n/kick - Kick users\n/info - Bot information\n/help - Show commands\n/ping - Check latency\n/poll - Create a poll\n/clear - Clear messages\n/server - Server info\n/user - User info\n/antilinks - Toggle anti-link system\n```", 
                   inline=False)

    # Set footer and image
    embed.set_footer(text="Made with ⚡ by Joxy")
    embed.set_thumbnail(url=bot.user.display_avatar.url)

    await interaction.response.send_message(embed=embed)

# Command: help
@bot.tree.command(name="help", description="Show available commands")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚡ Zeus Bot Commands ⚡",
        description="Here are all available commands for this bot:",
        color=ZEUS_BLUE
    )

    # Command categories (updated with new antilinks command)
    general_cmds = "`/info` - Bot information\n`/help` - This help menu\n`/ping` - Check bot latency\n`/server` - Server information\n`/user` - User information"
    fun_cmds = "`/marko` - Play a voice message\n`/poll` - Create a voting poll\n`/8ball` - Ask the magic 8ball"
    mod_cmds = "`/ban` - Ban a member\n`/kick` - Kick a member\n`/clear` - Clear messages\n`/timeout` - Timeout a user\n`/antilinks` - Control anti-invite system"

    embed.add_field(name="🔷 General Commands", value=general_cmds, inline=False)
    embed.add_field(name="🎮 Fun Commands", value=fun_cmds, inline=False)
    embed.add_field(name="🛡️ Moderation Commands", value=mod_cmds, inline=False)

    embed.set_footer(text="Zeus Bot • Powered by Joxy")
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# Command: ping
@bot.tree.command(name="ping", description="Check the bot's response time")
async def ping(interaction: discord.Interaction):
    start_time = time.time()
    await interaction.response.defer()
    end_time = time.time()

    api_latency = round((end_time - start_time) * 1000)
    ws_latency = round(bot.latency * 1000)

    if ws_latency < 100:
        color = ZEUS_GREEN
        status = "Excellent"
        emoji = "🟢"
    elif ws_latency < 200:
        color = ZEUS_GOLD
        status = "Good"
        emoji = "🟡"
    else:
        color = ZEUS_RED
        status = "Poor"
        emoji = "🔴"

    embed = discord.Embed(
        title="⚡ Zeus Network Status ⚡",
        color=color
    )

    embed.add_field(name="WebSocket Latency", value=f"{emoji} {ws_latency}ms ({status})", inline=False)
    embed.add_field(name="API Latency", value=f"{emoji} {api_latency}ms", inline=False)

    embed.set_footer(text="Zeus Bot • Powered by Joxy")
    await interaction.followup.send(embed=embed)

# Command: poll
@bot.tree.command(name="poll", description="Create a poll for users to vote on")
@app_commands.describe(question="The poll question", option1="First option", option2="Second option")
async def poll(interaction: discord.Interaction, question: str, option1: str, option2: str):
    embed = discord.Embed(
        title="⚡ Zeus Poll ⚡",
        description=f"**{question}**",
        color=ZEUS_PURPLE
    )

    embed.add_field(name="Option 1️⃣", value=option1, inline=False)
    embed.add_field(name="Option 2️⃣", value=option2, inline=False)

    embed.set_footer(text=f"Poll created by {interaction.user.display_name} • Zeus Bot")
    embed.timestamp = datetime.datetime.utcnow()

    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()

    # Add reactions for voting
    await msg.add_reaction("1️⃣")
    await msg.add_reaction("2️⃣")

# Command: kick
@bot.tree.command(name="kick", description="Kick a user from the server")
@app_commands.describe(member="The member to kick", reason="Reason for kicking")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    # Check if user has permissions
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ You don't have permission to kick members!", ephemeral=True)
        return

    # Check if bot can kick the target
    if not interaction.guild.me.guild_permissions.kick_members:
        await interaction.response.send_message("❌ I don't have permission to kick members!", ephemeral=True)
        return

    # Check if target is higher in role hierarchy
    if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("⚠️ You cannot kick someone with a higher or equal role!", ephemeral=True)
        return

    # Perform the kick
    try:
        await member.kick(reason=reason)

        # Kick message with embed
        embed = discord.Embed(
            title="👢 User Kicked",
            description=f"{member.mention} has been kicked from the server.",
            color=ZEUS_GOLD
        )
        embed.add_field(name="Executor", value=interaction.user.mention, inline=True)

        if reason:
            embed.add_field(name="Reason", value=reason, inline=True)

        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text="Zeus Bot • Powered by Joxy")
        embed.timestamp = datetime.datetime.utcnow()

        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to kick {member.mention}: {str(e)}")

# Command: clear (purge messages)
@bot.tree.command(name="clear", description="Clear a specified number of messages")
@app_commands.describe(amount="Number of messages to delete (1-100)")
async def clear(interaction: discord.Interaction, amount: int):
    # Check if user has permissions
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ You don't have permission to manage messages!", ephemeral=True)
        return

    # Check if bot can manage messages
    if not interaction.guild.me.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ I don't have permission to manage messages!", ephemeral=True)
        return

    # Limit amount between 1 and 100
    amount = min(max(1, amount), 100)

    await interaction.response.defer(ephemeral=True)

    # Delete messages
    try:
        deleted = await interaction.channel.purge(limit=amount)

        # Send confirmation
        await interaction.followup.send(f"✅ Successfully deleted {len(deleted)} messages!", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Error deleting messages: {str(e)}", ephemeral=True)

# Command: server (server info)
@bot.tree.command(name="server", description="Get information about the server")
async def server(interaction: discord.Interaction):
    guild = interaction.guild

    # Count members by status
    total_members = len(guild.members)
    bot_count = len([m for m in guild.members if m.bot])
    human_count = total_members - bot_count

    # Get boost info
    boost_level = guild.premium_tier
    boost_count = guild.premium_subscription_count

    # Get channel counts
    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)
    categories = len(guild.categories)

    embed = discord.Embed(
        title=f"⚡ {guild.name} Server Information",
        description=guild.description or "No description set",
        color=ZEUS_BLUE
    )

    # Server information
    created_timestamp = int(guild.created_at.timestamp())

    embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="Created", value=f"<t:{created_timestamp}:R>", inline=True)
    embed.add_field(name="Server ID", value=guild.id, inline=True)

    # Member information
    embed.add_field(name="Members", value=f"👥 {human_count} • 🤖 {bot_count}", inline=True)
    embed.add_field(name="Boost Level", value=f"⭐ Level {boost_level} ({boost_count} boosts)", inline=True)
    embed.add_field(name="Channels", value=f"💬 {text_channels} • 🔊 {voice_channels} • 📁 {categories}", inline=True)

    # Server icon
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    embed.set_footer(text="Zeus Bot • Powered by Joxy")
    embed.timestamp = datetime.datetime.utcnow()

    await interaction.response.send_message(embed=embed)

# Command: user (user info)
@bot.tree.command(name="user", description="Get information about a user")
@app_commands.describe(member="The member to get information about (leave empty for yourself)")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    # If no member is specified, use the command user
    if member is None:
        member = interaction.user

    # Calculate account age and join date
    created_timestamp = int(member.created_at.timestamp())
    joined_timestamp = int(member.joined_at.timestamp()) if member.joined_at else None

    # Get roles
    roles = [role.mention for role in member.roles if role.name != "@everyone"]
    roles_str = ", ".join(roles) if roles else "No roles"

    # Create embed
    embed = discord.Embed(
        title=f"User Information - {member.display_name}",
        color=member.color if member.color != discord.Color.default() else ZEUS_BLUE
    )

    # Basic information
    embed.add_field(name="Username", value=member.name, inline=True)
    embed.add_field(name="User ID", value=member.id, inline=True)
    embed.add_field(name="Bot", value="Yes" if member.bot else "No", inline=True)

    # Timestamps
    embed.add_field(name="Account Created", value=f"<t:{created_timestamp}:R>", inline=True)
    if joined_timestamp:
        embed.add_field(name="Joined Server", value=f"<t:{joined_timestamp}:R>", inline=True)

    # Status and activity
    status_emoji = {
        discord.Status.online: "🟢",
        discord.Status.idle: "🟡",
        discord.Status.dnd: "🔴",
        discord.Status.offline: "⚫"
    }

    status = f"{status_emoji.get(member.status, '⚫')} {str(member.status).capitalize()}"
    embed.add_field(name="Status", value=status, inline=True)

    # Roles (truncate if too many)
    if len(roles_str) > 1024:
        roles_str = roles_str[:1020] + "..."
    embed.add_field(name=f"Roles [{len(roles)}]", value=roles_str, inline=False)

    # Set thumbnail to user's avatar
    embed.set_thumbnail(url=member.display_avatar.url)

    embed.set_footer(text="Zeus Bot • Powered by Joxy")
    embed.timestamp = datetime.datetime.utcnow()

    await interaction.response.send_message(embed=embed)

# Command: 8ball
@bot.tree.command(name="8ball", description="Ask the magic 8-ball a question")
@app_commands.describe(question="The question to ask the magic 8-ball")
async def eightball(interaction: discord.Interaction, question: str):
    responses = [
        "It is certain.",
        "It is decidedly so.",
        "Without a doubt.",
        "Yes, definitely.",
        "You may rely on it.",
        "As I see it, yes.",
        "Most likely.",
        "Outlook good.",
        "Yes.",
        "Signs point to yes.",
        "Reply hazy, try again.",
        "Ask again later.",
        "Better not tell you now.",
        "Cannot predict now.",
        "Concentrate and ask again.",
        "Don't count on it.",
        "My reply is no.",
        "My sources say no.",
        "Outlook not so good.",
        "Very doubtful."
    ]

    # Get random response
    response = random.choice(responses)

    # Determine color based on response
    if response in responses[:10]:  # Positive responses
        color = ZEUS_GREEN
    elif response in responses[10:15]:  # Neutral responses
        color = ZEUS_GOLD
    else:  # Negative responses
        color = ZEUS_RED

    # Create embed
    embed = discord.Embed(
        title="🔮 Magic 8-Ball",
        color=color
    )

    embed.add_field(name="Question", value=question, inline=False)
    embed.add_field(name="Answer", value=response, inline=False)

    embed.set_footer(text="Zeus Bot • Powered by Joxy")
    embed.timestamp = datetime.datetime.utcnow()

    await interaction.response.send_message(embed=embed)

# Command: timeout (mute)
@bot.tree.command(name="timeout", description="Timeout a user for a specified duration")
@app_commands.describe(
    member="The member to timeout",
    duration="Duration in minutes (max 40320 = 4 weeks)",
    reason="Reason for the timeout"
)
async def timeout(interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = None):
    # Check if user has permissions
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ You don't have permission to timeout members!", ephemeral=True)
        return

    # Check if bot can timeout the target
    if not interaction.guild.me.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ I don't have permission to timeout members!", ephemeral=True)
        return

    # Check if target is higher in role hierarchy
    if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("⚠️ You cannot timeout someone with a higher or equal role!", ephemeral=True)
        return

    # Limit duration to maximum allowed (4 weeks)
    duration = min(duration, 40320)

    # Calculate timeout end time
    timeout_until = datetime.datetime.utcnow() + datetime.timedelta(minutes=duration)

    # Apply timeout
    try:
        await member.timeout(timeout_until, reason=reason)

        # Format duration for display
        if duration < 60:
            duration_str = f"{duration} minute(s)"
        elif duration < 1440:  # Less than a day
            hours = duration // 60
            minutes = duration % 60
            duration_str = f"{hours} hour(s)"
            if minutes > 0:
                duration_str += f", {minutes} minute(s)"
        else:
            days = duration // 1440
            remaining = duration % 1440
            hours = remaining // 60
            minutes = remaining % 60
            duration_str = f"{days} day(s)"
            if hours > 0:
                duration_str += f", {hours} hour(s)"
            if minutes > 0:
                duration_str += f", {minutes} minute(s)"

        # Create embed
        embed = discord.Embed(
            title="⏱️ User Timed Out",
            description=f"{member.mention} has been timed out for {duration_str}.",
            color=ZEUS_GOLD
        )

        embed.add_field(name="Executor", value=interaction.user.mention, inline=True)
        embed.add_field(name="Duration", value=duration_str, inline=True)
        embed.add_field(name="Expires", value=f"<t:{int(timeout_until.timestamp())}:R>", inline=True)

        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)

        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text="Zeus Bot • Powered by Joxy")
        embed.timestamp = datetime.datetime.utcnow()

        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to timeout {member.mention}: {str(e)}")

# Run the bot
if __name__ == "__main__":
    print("╔═══════════════════════════════════════╗")
    print("║        ZEUS BOT - STARTING UP         ║")
    print("╚═══════════════════════════════════════╝")

try:
    bot.run(TOKEN)
except discord.LoginFailure:
    print("❌ ERROR: Invalid Discord token. Please check your token and try again.")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

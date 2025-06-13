import os
import asyncio
import discord
from discord.ext import commands
import random
import re
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('discord_multi_bot')

# Get all bot tokens from environment variables
def get_all_tokens():
    """Retrieve all bot tokens from environment variables"""
    tokens = []
    # Get main token first
    main_token = os.getenv('DISCORD_BOT_TOKEN_MAIN')
    if main_token:
        tokens.append(main_token)
    
    # Get worker tokens (DISCORD_BOT_TOKEN_1, DISCORD_BOT_TOKEN_2, etc.)
    for i in range(1, 100):  # Support up to 99 worker accounts
        token = os.getenv(f'DISCORD_BOT_TOKEN_{i}')
        if token:
            tokens.append(token)
    
    if not tokens:
        logger.error("No bot tokens found in environment variables!")
        sys.exit(1)
    
    logger.info(f"Loaded {len(tokens)} bot tokens")
    return tokens

class MultiBot:
    def __init__(self):
        self.bots = []
        self.tokens = get_all_tokens()
        self.main_bot = None
        self.command_prefix = '+'
        self.is_ready = False
        
    async def start_bots(self):
        """Start all bot instances"""
        tasks = []
        for token in self.tokens:
            # Create bot instance with basic intents
            intents = discord.Intents.default()
            intents.message_content = True
            
            bot = commands.Bot(
                command_prefix=self.command_prefix,
                intents=intents,
                help_command=None
            )
            
            # Register events
            bot.event(self.on_ready)
            bot.event(self.on_command_error)
            
            # Only register commands on the first bot (main bot)
            if not self.main_bot:
                bot.command(name='share')(self.share_command)
                bot.command(name='help')(self.help_command)
                bot.command(name='status')(self.status_command)
                self.main_bot = bot
            
            self.bots.append(bot)
            tasks.append(bot.start(token))
        
        await asyncio.gather(*tasks)
    
    async def on_ready(self):
        """Called when a bot is ready"""
        if not self.is_ready:
            logger.info(f"Main bot ready: {self.main_bot.user}")
            await self.main_bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"{self.command_prefix}help"
                )
            )
            self.is_ready = True
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        
        logger.error(f"Command error: {error}")
        await ctx.send(f"❌ Error: {str(error)}")
    
    async def help_command(self, ctx):
        """Show help message"""
        embed = discord.Embed(
            title="Multi-Share Bot Help",
            description="Share videos through multiple bot accounts",
            color=0x3498db
        )
        embed.add_field(
            name=f"{self.command_prefix}share <url>",
            value="Share a video through all available bot accounts",
            inline=False
        )
        embed.add_field(
            name=f"{self.command_prefix}status",
            value="Show current bot status",
            inline=False
        )
        embed.add_field(
            name=f"{self.command_prefix}help",
            value="Show this help message",
            inline=False
        )
        embed.set_footer(text=f"Total bot accounts: {len(self.bots)}")
        await ctx.send(embed=embed)
    
    async def status_command(self, ctx):
        """Show bot status"""
        embed = discord.Embed(
            title="Bot Status",
            description="Multi-account sharing system",
            color=0x2ecc71
        )
        embed.add_field(
            name="Accounts Ready",
            value=f"{len(self.bots)} bot accounts",
            inline=False
        )
        embed.add_field(
            name="Last Command",
            value=f"`{self.command_prefix}share <url>` to share videos",
            inline=False
        )
        await ctx.send(embed=embed)
    
    async def share_command(self, ctx, video_url: str):
        """Share a video through multiple bot accounts"""
        # Validate URL
        if not re.match(r'https?://(?:www\.)?\w+\.\w+', video_url):
            await ctx.send("❌ Invalid URL format. Use `+share <valid_url>`")
            return
        
        # Confirm command received
        total_bots = len(self.bots)
        status_msg = await ctx.send(f"🔄 Sharing video through {total_bots} accounts...")
        
        # Share from all bots with delays
        success_count = 0
        for i, bot in enumerate(self.bots):
            try:
                # Skip if it's the same bot that received the command
                if bot.user.id == ctx.author.id:
                    continue
                
                # Random delay to avoid rate limits (1-5 seconds per message)
                delay = random.uniform(1.0, 5.0)
                await asyncio.sleep(delay)
                
                # Get channel object
                channel = bot.get_channel(ctx.channel.id)
                if channel is None:
                    channel = await bot.fetch_channel(ctx.channel.id)
                
                # Send message from this bot
                await channel.send(f"📹 **Bot Account {i+1}**: {video_url}")
                success_count += 1
                
                # Update status message every 3 accounts
                if i % 3 == 0:
                    await status_msg.edit(
                        content=f"🔄 Sharing... ({success_count}/{total_bots} accounts)"
                    )
                    
            except Exception as e:
                logger.error(f"Bot {i} error: {e}")
        
        # Completion message
        await status_msg.edit(
            content=f"✅ Video shared successfully through {success_count} accounts!"
        )

if __name__ == "__main__":
    bot_manager = MultiBot()
    
    # Start the bot system
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(bot_manager.start_bots())
    except KeyboardInterrupt:
        logger.info("Shutting down bots...")
        for bot in bot_manager.bots:
            loop.run_until_complete(bot.close())
    finally:
        loop.close()

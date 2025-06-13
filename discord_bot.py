import discord
from discord.ext import commands
import asyncio
import logging
from account_manager import AccountManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord_bot')

# Create bot instance
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='+', intents=intents)

# Create account manager
account_manager = AccountManager()

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="+share <tiktok_url>"
        )
    )

@bot.command(name='share')
async def share_video(ctx, video_url: str):
    """Share a TikTok video using multiple accounts"""
    # Validate URL
    if "tiktok.com" not in video_url:
        await ctx.send("❌ Please provide a valid TikTok URL")
        return
    
    # Get number of shares requested (default: 5)
    share_count = 5
    if ' ' in ctx.message.content:
        try:
            share_count = int(ctx.message.content.split(' ')[2])
        except (IndexError, ValueError):
            pass
    
    # Limit max shares
    share_count = min(share_count, 20)
    
    # Start sharing
    message = await ctx.send(f"🔄 Starting to share video with {share_count} accounts...")
    
    # Perform shares
    success_count = 0
    for i in range(share_count):
        result = account_manager.share_video(video_url)
        if result["success"]:
            success_count += 1
            logger.info(f"Account {result['account']} shared successfully")
        else:
            logger.error(f"Account {result['account']} failed: {result['message']}")
        
        # Update status
        if i % 3 == 0:
            await message.edit(content=f"🔄 Sharing... ({i+1}/{share_count} accounts)")
        
        # Add delay between shares
        await asyncio.sleep(random.uniform(5, 15))
    
    # Final result
    await message.edit(content=f"✅ Video shared successfully with {success_count}/{share_count} accounts!")

@bot.command(name='accounts')
async def show_accounts(ctx):
    """Show available TikTok accounts"""
    embed = discord.Embed(
        title="TikTok Accounts",
        description="Accounts available for sharing",
        color=0x00FFFF
    )
    
    for account in account_manager.accounts:
        embed.add_field(
            name=account["name"],
            value=f"Shares: {account['share_count']} | Last used: {time.ctime(account['last_used'])}",
            inline=False
        )
    
    await ctx.send(embed=embed)

if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))

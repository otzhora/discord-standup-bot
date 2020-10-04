import os
from dotenv import load_dotenv

from bot.standup_bot import StandupBot, Register

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = StandupBot(GUILD, command_prefix="!")
bot.add_cog(Register(bot))

bot.run(TOKEN)

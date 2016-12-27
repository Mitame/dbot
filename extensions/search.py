from dbot.extensions import BaseExtInfo, bot
from discord import Embed
import google

@bot.command("google")
@bot.command("g")
async def cmd_google(msg, *search_args):
    search_string = " ".join(search_args)
    results = list(google.search(search_string, stop=5))[:5]
    await bot.api.send_message(msg.server, "\n".join(results), embed=Embed())


class ExtInfo(BaseExtInfo):
    name = "search"
    short = "Searching stuff"
    description = "Search on google for web/image/video"
    provides = ["search"]
    requires = []
    help_group = "search"
    enable_func = None
    disable_func = None

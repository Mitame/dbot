from dbot.extensions import BaseExtInfo, bot

@bot.command()
async def hi(msg):
    """
    Say 'Hi!'.
    Syntax:
        `{command_tag}hi`
    """
    await bot.api.send_message(msg.server, "Hi!")


class ExtInfo(BaseExtInfo):
    name = "example"
    description = "An example"

from dbot.extensions import BaseExtInfo, bot

def on_enable():
    pass

def on_disable():
    pass

@bot.command()
async def echo(msg, *args, **kwargs):
    """
    Replies with exactly what you said, minus the command part
    """
    await bot.api.send_message(msg.server, "You said '%s'" % " ".join(args))

@bot.command("cmdtag")
async def update_command_tag(msg, new_tag):
    """
    Changes the command tag (currently globaly)
    Syntax:
        `{command_tag}cmdtag <new tag>`
    """
    bot.command_tag = new_tag
    await bot.api.send_message(msg.server, "Command tag changed to '%s'" % new_tag)

@bot.command("reload")
async def cmd_reload_extension(msg, ext_name):
    """
    Reloads the extension in place
    Syntax:
        `{command_tag}reload <extension name>`
    """
    if bot.reload_extension(ext_name):
        await bot.api.send_message(msg.server, "Extension successfully reloaded.")
    else:
        await bot.api.send_message(
            msg.server,
            "Extension reload failed. Check your logs."
        )

@bot.command("load")
async def cmd_load_extension(msg, file_name):
    """
    Loads the extension in place
    Syntax:
        `{command_tag}load <extension file>`
    """
    full_path = os.path.realpath(os.path.join(bot.extension_dir, file_name))
    extension_dir = os.path.realpath(bot.extension_dir)

    if os.path.relpath(full_path, extension_dir).startswith(".."):
        await bot.api.send_message(msg.server, "Could not find extension.")
        return

    bot.load_extension(full_path)
    await bot.api.send_message(msg.server, "Extension successfully loaded.")

@bot.command("enable")
async def cmd_enable_extension(msg, ext_name):
    """
    Enable a loaded extension
    Syntax:
        `{command_tag}enable <extension name>`
    """
    if bot.enable_extension(ext_name):
        await bot.api.send_message(msg.server, "Extension successfully enabled.")
    else:
        await bot.api.send_message(
            msg.server,
            "Extension enable failed. Check your logs."
        )

class ExtInfo(BaseExtInfo):
    name = "util"
    short = "Basic utilities"
    description = "Basic utilities for managing modules and testing stuff"
    provides = ["util"]
    requires = []
    help_group = "util"
    enable_func = on_enable
    disable_func = on_disable

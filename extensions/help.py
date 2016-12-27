from dbot.extensions import BaseExtInfo, bot
import inspect

@bot.command()
async def help(msg, command_name=None):
    """
    Show help for a command or list commands
    List commands:
        `{command_tag}help`
    Show help for a single command:
        `{command_tag}help <command name>`
    """
    if command_name:
        try:
            commands = bot.commands[command_name]
            for x in commands:
                await bot.api.send_message(
                    msg.server,
                    bot.format_doc_string(
                        inspect.getdoc(x),
                        server=msg.server
                    )
                )
        except KeyError:
            await bot.api.send_message(msg.server, "Could not find command '%s'" % command_name)
    else:
        groups = {}

        for ext in bot.extensions.values():
            if ext["info"].help_group not in groups:
                groups[ext["info"].help_group] = []
            for name, cmds in ext["commands"].items():
                for cmd in cmds:
                    cmd_message = "{}: {}".format(
                        name,
                        bot.format_doc_string(
                            inspect.getdoc(cmd).split("\n")[0],
                            server=msg.server
                        )
                    )
                    groups[ext["info"].help_group].append(cmd_message)

        message = "```diff\n"
        for group_name in sorted(groups.keys()):
            message += "+{}:\n".format(group_name)
            for command_msg in groups[group_name]:
                message += "    {}\n".format(command_msg)
        message += "```\n"

        await bot.api.send_message(msg.server, message)


class ExtInfo(BaseExtInfo):
    name = "help"
    short = "Help messages"
    description = "Shows help messages for commands and lists commands"
    provides = ["help"]
    requires = []
    help_group = "help"
    enable_func = None
    disable_func = None

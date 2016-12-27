import discord
import asyncio
import logging
import importlib.util
import os
import traceback

from inspect import getmembers, getdoc
from pprint import pprint

logging.basicConfig(format="%(message)s")
logging.getLogger().setLevel(logging.INFO)

logger = logging.getLogger("dbot")

loop = asyncio.get_event_loop()
oauth2_url = "https://discordapp.com/oauth2/authorize?&client_id={bot_id}&scope={scope}&permissions={permissions}"

class Bot():
    def __init__(self, token, mongo_db, command_tag=None, extension_dir="./extensions"):
        self.api = discord.Client()

        self.token = token
        self.mongo_db = mongo_db
        self.command_tag = command_tag
        self.extension_dir = extension_dir

        self.commands = {}
        self.extensions = {}

        self.loading_commands = None

        self.load_all_extensions(self.extension_dir)

        #Register some handlers
        self.api.event(self.on_message)
        self.api.event(self.on_ready)
        self.api.event(self.on_server_join)
        self.api.event(self.on_server_remove)

    def start(self):
        self.api.run(self.token)

    @staticmethod
    def register_command(command_dict, command_name, coro):
        if command_name not in command_dict:
            command_dict[command_name] = []

        command_dict[command_name].append(coro)

    def command(self, command_name=None):
        if self.loading_commands is None:
            command_list = self.commands
        else:
            command_list = self.loading_commands
        if command_name:
            def named(coro):
                self.register_command(command_list, command_name, coro)
                return coro # So we can chain decorators
            return named
        else:
            def unnamed(coro):
                command_name = coro.__name__
                self.register_command(command_list, command_name, coro)
                return coro # So we can chain decorators
            return unnamed

    def get_command_tag(self, server=None):
        if server:
            #Check if server has custom tag
            if False:
                raise NotImplementedError()
            elif self.command_tag is not None:
                return self.command_tag
            else:
                if server.me.nick:
                    return server.me.nick[0].lower() + "!"
                else:
                    return self.api.user.name[0].lower() + "!"
        else:
            return self.command_tag

    def is_command(self, msg):
        return msg.content.startswith(self.get_command_tag(server=msg.server))

    def get_commands(self, msg):
        content = msg.content
        if self.command_tag:
            content = content[len(self.command_tag):]
        else:
            content = content[2:]

        args = content.split(" ")
        if args[0] in self.commands:
            for cmd in self.commands[args[0]]:
                yield (cmd, args[1:])

    def load_all_extensions(self, directory):
        for file_path in next(os.walk(directory))[2]:
            full_path = os.path.join(directory, file_path)
            self.load_extension(full_path)

    def load_extension(self, ext_file_path):
        spec = importlib.util.spec_from_file_location("dbot.ext", ext_file_path)
        mod = importlib.util.module_from_spec(spec)

        self.loading_commands = {}

        spec.loader.exec_module(mod)

        loaded_commands = self.loading_commands
        self.loading_commands = None

        print("Loaded module")
        print(loaded_commands)

        self.extensions[mod.ExtInfo.name] = {
            "info": mod.ExtInfo,
            "file_path": ext_file_path,
            "module": mod,
            "commands": loaded_commands,
            "is_enabled": False
        }

        return mod.ExtInfo.name

    def enable_extension(self, ext_name):
        ext = self.extensions[ext_name]

        for key, value in ext["commands"].items():
            if key not in self.commands:
                self.commands[key] = []
            self.commands[key].extend(value)

        if ext["info"].enable_func is not None:
            ext["info"].enable_func()
        ext["is_enabled"] = True
        return ext["is_enabled"]

    def disable_extension(self, ext_name):
        ext = self.extensions[ext_name]

        ext["is_enabled"] = False

        if ext["info"].disable_func is not None:
            ext["info"].disable_func()

        for key, value in ext["commands"].items():
            if key in self.commands:
                for func in value:
                    self.commands[key].remove(func)

    def reload_extension(self, ext_name):
        ext = self.extensions[ext_name]
        was_enabled = ext["is_enabled"]
        success = False
        try:
            if ext["is_enabled"]:
                self.disable_extension(ext_name)

            self.load_extension(ext["file_path"])
            success = True
        except Exception:
            traceback.print_exc()

        if was_enabled:
            self.enable_extension(ext_name)
        return success

    def format_doc_string(self, docstring, server=None):
        return docstring.format(
            command_tag=self.get_command_tag(server=server)
        )

    async def on_message(self, msg):
        if msg.author != self.api.user:
            if self.is_command(msg):
                await self.handle_command(msg)
            else:
                pass
                # await self.api.send_message(msg.server, "Command not found")

    async def handle_command(self, msg):
        cmd_count = 0
        for cmd, args in self.get_commands(msg):
            # try:
            await cmd(msg, *args)
            # except TypeError as e:
            #     error_message = "Invalid Syntax: ```{}```".format(
            #         self.format_doc_string(getdoc(cmd), server=msg.server)
            #     )
            #     await self.api.send_message(msg.server, error_message)
            cmd_count += 1

        if cmd_count == 0:
            await self.api.send_message(msg.server, "Command not found.")


    async def on_ready(self):
        histring = "Hi! I'm {}#{}. Let me join your server using this link:"
        user = self.api.user

        print(histring.format(user.display_name, user.discriminator))
        print(oauth2_url.format(
            bot_id="263096588656836628",
            scope="bot",
            permissions=0
        ))


    async def on_server_join(self, server):
        logger.info("joined server: <{}|{}>".format(server.name, server.id))

    async def on_server_remove(self, server):
        logger.info("left server: <{}|{}>".format(server.name, server.id))

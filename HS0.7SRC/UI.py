import threading
import os
import shutil
import json
import time
import rich
import random
import sys

from pyfiglet import figlet_format as ascii_text
from rich.console import Console, Group
from rich.panel import Panel
from rich.align import Align
from rich.columns import Columns
from rich.live import Live


class Response:
    def anim(self, text, typ):
        self.writing = True

        count = 0

        with Live("", refresh_per_second=144) as live:
            if typ == "loading":
                c3 = f"rgb({int((rc1[0] + rc2[0]) / 2)},{int((rc1[1] + rc2[1]) / 2)},{int((rc1[2] + rc2[2]) / 2)})"
                c4 = f"rgb({int(((rc1[0] * 2) + rc2[0]) / 3)},{int(((rc1[1] * 2) + rc2[1]) / 3)},{int(((rc1[2] * 2) + rc2[2]) / 3)})"

                while not self.stop_event.is_set():
                    if "Iteration" in text:
                        txt = text + random.choice([
                                " - thinking...", " - cogitating...", " - reasoning...", 
                                " - analyzing...",  " - considering...",  " - deliberating...", 
                                " - processing...", " - formulating...", " - evaluating..."
                            ]
                        )
                    else: txt = text

                    for x in range(len(txt)):
                        if self.stop_event.is_set():
                            live.update("")
                            return
                        if 0 <= count < 10:    asci = "▀  "
                        elif 10 <= count < 20: asci = "▄  "
                        elif 20 <= count < 30: asci = " ▀ "
                        elif 30 <= count < 40: asci = " ▄ "
                        elif 40 <= count < 50: asci = "   "
                        output = ""

                        for y, char in enumerate(txt):
                            color = c1
                            if (x - 2) == y or (x + 2) == y: color = c4
                            if (x - 1) == y or (x + 1) == y: color = c3
                            if x == y: color = c2

                            output += f"[{color}]{char}[/{color}]"

                        time.sleep(0.1)
                        live.update(asci + output)

                        if count <= 50:
                            count += 1
                        else:
                            count = 0

                live.update("")
                self.writing = False
                return

            elif typ == "response":
                for i in range(len(text)):
                    live.update(f"[{c1}]{text[:i + 1]}[/{c1}]")
                    time.sleep(0.3 / len(text))

        print()
        self.writing = False
        return

    def __init__(self, max_iteration):
        self.max_iteration = max_iteration
        self.thread = None
        self.stop_event = threading.Event()
        self.writing = False

    def write(self, txt, typ):
        if self.thread and self.thread.is_alive():
            self.stop_event.set()
            self.thread.join(timeout=1)

        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=lambda: self.anim(txt, typ), daemon=True)
        self.thread.start()

def inputr(text=None, color=None):
    try:
        if text:
            if color:
                rich.print(f"[{color}]{text}[/{color}]", end="", flush=True)
            else:
                print(text, end="", flush=True)

        return input()

    except (KeyboardInterrupt, EOFError):
        return "/exit"


def folder_linked():
    error = False

    while True:
        if error:
            rich.print("[red]This path does not exist[/red]")

        link = inputr('enter your folder path ("None" for undo link): ', c1 )

        if os.path.exists(link):
            while True:
                gen_name = (
                    "GPT-5.6-LUNA?"
                    if metadata["gen_type"] == "api"
                    else "AI"
                )

                rich.print(
                    f"[{c1}]index folder with {gen_name} y/n "
                    f"(This could cost a lot of tokens)[/{c1}]"
                )

                match inputr("<< ", c1):
                    case "y": return link, True
                    case "n": return link, False

        elif link == "None":
            return None, None
        elif not link:
            continue
        elif link == "/exit":
            return
        else:
            error = True


def skills():
    error = False

    while True:
        if error:
            rich.print("[red]This path does not exist[/red]")

        link = inputr('link skills folder ("None" for undo skill path) << ', c1)

        if not link:
            continue

        elif link == "/exit" or link == "None":
            return

        else:
            if os.path.exists(link):
                return link

            else:
                error = True
                continue


def telegram():
    def enter_api():
        return inputr("telegram bot api key << ", c1)

    api_key = (
        metadata.get("tg_bot_api")
        if metadata.get("tg_bot_api")
        else enter_api()
    )

    if api_key != "/exit":
        rich.print(f"[{c1}]commands:\n  /run\n  /change_api[/{c1}]")

        while True:
            choose = inputr("<< ")

            for chs in ["/run", "/exit"]:
                if choose == chs:
                    return api_key, choose

            if choose == "/change_api":
                api_key = enter_api()

    else:
        return "/exit"


def main(model, link_folder, vision_mode, coder_mode, gen_type):
    model = os.path.basename(model)

    model = model.replace("-it", "")

    if "-QAT-Q" in model:
        model = model.split("-QAT-Q")[0]

    for x in range(10):
        if f"Q{x}_" in model:
            model = model.split(f"Q{x}_")[0]

    model = model.replace("-", " ")

    def render():
        right_panel_size = (
            shutil.get_terminal_size().columns - 53
        )

        os.system("cls")

        console.print(
            Panel(
                Columns(
                    [
                        Align.left(
                            Panel(
                                f"[{c1}]{ascii_text('holy\nspirit', font='ansi_regular')}[/{c1}]", width=48, height=14, border_style=c2
                            )
                        ),

                        Align.right(
                            Group(
                                Panel(
                                    Align.left(
                                        f"[{c1}]Fuck [bold][rgb(255,144,0)]claude[/rgb(255,144,0)][/bold]\nMade with ❤️ for [bold][rgb(36,150,255)]Ic[/rgb(36,150,255)]e[rgb(255,30,0)]l[/rgb(255,30,0)]a[rgb(36,150,255)]nd[/rgb(36,150,255)][/bold][/{c1}]"
                                    ),
                                    width=right_panel_size, height=4, border_style=c2
                                ),

                                Panel(
                                    Align.left(f"[{c1}]" f"Model: {model.upper()}\n" f"Vision Mode: {str(vision_mode)}; " f"Coder Mode: {coder_mode}\n" f"'/commands' to see actual commands" f"[/{c1}]"),
                                    width=right_panel_size, height=6,  border_style=c2 
                                ),

                                Panel(
                                    Align.left(f"[{c1}]Linked Folder: {link_folder}[/{c1}]"), width=right_panel_size, height=4, border_style=c2
                                )
                            )
                        )
                    ],
                    expand=True
                ),

                title=f"[{c1}]holy spirit 0.7 | CTRL+C for exit[/{c1}]", border_style=c2
            )
        )

    render()

console = Console()

try:
    with open("metadata/metadata.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)

        c1 = metadata["colors"].get("color1")
        c2 = metadata["colors"].get("color2")

        def parse_rgb(color):
            color = color.replace("rgb(", "")
            color = color.replace(")", "")

            return tuple(
                int(x.strip())
                for x in color.split(",")
            )

        rc1 = parse_rgb(c1)
        rc2 = parse_rgb(c2)

except (FileNotFoundError, KeyError, ValueError):
    c1 = "rgb(255,255,255)"
    c2 = "rgb(125,125,125)"

    rc1 = (255, 255, 255)
    rc2 = (125, 125, 125)
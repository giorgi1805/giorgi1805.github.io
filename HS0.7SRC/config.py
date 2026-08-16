import json, os, sys
from platform import version, system, machine
from psutil import virtual_memory
import GPUtil
from wmi import WMI
import requests, json
import UI

def optional_data():
    with open("metadata/metadata.json", "r", encoding="utf-8") as f: 
        metadata = json.load(f) 

    if not "Machine" in metadata: 
        ram = virtual_memory()

        for cpu in WMI().Win32_Processor():
            for gpu in GPUtil.getGPUs():
                metadata["GPU"] = gpu.name
                try: metadata["VRAM"] = str(round(gpu.memoryTotal / 1024)) + "GB"
                except ZeroDivisionError: metadata["VRAM"] = None
            
            metadata["OS"]            = system()
            metadata["OS_version"]    = version()
            metadata["Machine"]       = machine()
            metadata["Processor"]     = cpu.Name
            metadata["RAM_total"]     = f"{round(ram.total / (1024**3), 2)*1000}MB"
            metadata["RAM_available"] = f"{round(ram.available / (1024**3), 2)*1000}MB"

        ip = requests.get("https://api.ipify.org").text
        metadata["IP"] = ip

        ip_data = requests.get(f"https://ipapi.co/{ip}/json/").json()
        if "country_name" in ip_data and "city" in ip_data:
            metadata["country"] = ip_data["country_name"]
            metadata["city"] = ip_data["city"]
        
        with open("metadata/metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)

def load_data():
    try:
        with open("metadata/metadata.json", "r", encoding="utf-8") as f:
            metadata = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        while True:
            ui = UI
            gen_type = ui.inputr("enter generate type ('local' or 'api') << ", ui.c1)

            if gen_type == "/exit": 
                ui.clear()
                sys.exit()

            if gen_type == "local": 
                model = ui.inputr("enter model path (.gguf) << ")
                break 
            else: 
                if not os.environ["OPENAI_API_KEY"].strip(): 
                    os.system(f'setx OPENAI_API_KEY "{ui.inputr("Enter Your OpenAI API-key << ")}"', ui.c1)
                    os.system('cls') 
                    print("[red]NEED TO RESTART TERMINAL[/red]")
                    sys.exit()
                model = "gpt-5.6-luna"
                break 

        metadata = {
            "model": model,
            "vision_mode": False,
            "max_iteration": 10,
            "folder_linked": "None",
            "coder_mode": False, 
            "gen_type": gen_type,
            "tg_bot_api": None
        }

        try:
            os.mkdir("metadata")
        except FileExistsError: 
            pass 
        
        with open("metadata/metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
            
    optional_data()
    return (
        metadata.get("model"),
        metadata.get("vision_mode"),
        metadata.get("max_iteration"),
        metadata.get("folder_linked") if os.path.exists(str(metadata.get("folder_linked"))) else None,
        metadata.get("coder_mode"),
        metadata.get("gen_type"),
        metadata.get("tg_bot_api")
    )

def save(model=None, vision_mode=None, max_iteration=None, folder_linked=None, coder_mode=None, gen_type=None, tg_bot_api=None):
    try:
        with open("metadata/metadata.json", "r", encoding="utf-8") as f:
            metadata = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        metadata = {}

    if model:                 metadata["model"]              =              model
    if vision_mode != None:   metadata["vision_mode"]        =        vision_mode
    if max_iteration != None: metadata["max_iteration"]      =      max_iteration
    if coder_mode != None:    metadata["coder_mode"]         =         coder_mode
    if gen_type:              metadata["gen_type"]           =           gen_type
    if tg_bot_api:            metadata["tg_bot_api"]         =         tg_bot_api
    metadata["folder_linked"]                                =      folder_linked

    with open("metadata/metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)
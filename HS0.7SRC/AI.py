import parsing, json, re, math, os, time, sys, getpass
from tool_call.classic import Classic 
from tool_call.coder import CoderMode
from tool_call.vision import VisionMode as CVision 
from gguf import GGUFReader
from multiprocessing import Process, Queue, Event

def error(erno): 
    os.system('cls') 
    print(f"\033[31mHS SYSTEM {erno}\033[0m")
    os._exit(1) 

class Start: 
    def truncate(self, value, limit=1399):
        if isinstance(value, str):
            if len(value) > limit:
                return f"{value[:limit]} ...{len(value) - limit} characters more"
            return value

        if isinstance(value, list): 
            return [self.truncate(item, limit) for item in value]

        if isinstance(value, dict): 
            return {key: self.truncate(val, limit) for key, val in value.items()}

        return value

    def load_history(self, prompt, reasoning, tool_call, response, system, iteration, model):
        try: tool_call = json.loads(tool_call) if tool_call else None
        except (json.JSONDecodeError, TypeError):    tool_call = None

        if isinstance(tool_call, dict):
            tool_call = {
                **tool_call,
                "args": self.truncate(tool_call.get("args")),
                "kwargs": self.truncate(tool_call.get("kwargs")),
            }

        elif isinstance(tool_call, list):
            tool_call = self.truncate(tool_call)

        if iteration == 0:
            self.history.append({
                "iteration №1": {
                    "prompt":          prompt, 
                    "ai_reasoning":    reasoning, 
                    "ai_response":     {
                        "tool_call": tool_call, 
                        "response":  response
                    }, 
                    "return":         system, 
                    "model":           {
                        "type": self.gen_type, 
                        "name": model
                    }
                }
            })
        else:
            self.history.append({
                f"iteration №{iteration + 1}": {
                    "ai_reasoning":    reasoning, 
                    "ai_response":     {
                        "tool_call":   tool_call, 
                        "response":    response
                    }, 
                    "return":          system,
                }
            })

        with open("metadata/history.json", "w", encoding="utf-8") as f: 
            json.dump(self.history, f, indent=4, ensure_ascii=False)

    def get_result(self, block=True, timeout=None):
        try:
            result = self.AI.output_queue.get(block=block, timeout=timeout)
            
            if result[0] == "error":
                raise Exception(f"{result}")

            if result[0] == "result":
                _, th, tc, rp = result
                return th, tc, rp

        except KeyboardInterrupt:
            self.stop_generation()
            return None, None, "[red][bold]generation iterrupted[/bold][/red]"
        
    def run(self, prompt):   
        mode = 0
        if not hasattr(self, "AI"): 
            self.AI = AI(self.gen_type, self.model)
        
        if not self.AI.is_loaded(): 
            yield "loading AI...", "loading"

        while not self.AI.is_loaded(): 
            time.sleep(0.01)

        if self.vision_mode: 
            if "/vision" in prompt: mode = 1
        if self.coder_mode: 
            if "/coder" in prompt:  mode = 2 

        instructions = None 
        
        for iteration in range(self.max_iteration):
            yield f"Iteration №{iteration + 1}", "loading"

            if iteration > 2:
                if (
                        self.history[iteration - 1][f"iteration №{iteration}"].get("return") == [''] 
                    and self.history[iteration - 2][f"iteration №{iteration - 1}"].get("return") == ['']
                ): # impostor syndrome
                    self.history = []
                    yield "[bold]AI agent has finished its work[/bold]", "response"
                    return

            if not mode:    instructions = self.classic_instructions 
            if mode == 1:   instructions = self.vision_instructions 
            elif mode == 2: instructions = self.coder_instructions

            if iteration:
                instructions = instructions.replace("<iteration>", str(iteration + 1))
                instructions = instructions.replace("HISTORY: <NONE>", ("HISTORY: " + str(self.history)))
                instructions = instructions.replace("**prompt**", "")
            else:instructions = instructions.replace("<iteration>", "first")

            if mode == 1 and self.vision_mode: 
                instructions = instructions.replace("<screenshot>", self.ocr.return_json())

            if self.gen_type == "api": 
                content = (instructions + "\n" + prompt) if not iteration else instructions
            else:
                content = [{"role": "user", "content": (instructions + "\n" + prompt) if not iteration else instructions}]

            try: 
                try:
                    self.AI.generate(content) 
                except KeyboardInterrupt: 
                    self.AI.stop_generation()
                    return 

                reasoning, tool_call, response = self.get_result()
            except Exception as e: 
                yield "[red]ERROR[/red]", "response"
                error(e) 

            if tool_call:
                if mode == 0:   system = parsing.run(Classic(), tool_call)
                elif mode == 1: system = parsing.run(CVision(), tool_call)
                elif mode == 2: system = parsing.run(CoderMode(), tool_call) 

                if isinstance(system, str): 
                    system = [system]
            else: system = [""]

            self.load_history(prompt, reasoning, tool_call, response, system, iteration, self.model)

            data = self.history[iteration][f"iteration №{iteration + 1}"]
            if data["ai_response"].get("response"): 
                yield data["ai_response"].get("response"), "response"
                if not iteration and not data["ai_response"].get("tool_call", None):
                    return

            try:
                if data.get("return") == ["__classic mode__"]:  yield "AI agent environment transfered to [bold]classic mode[/bold]", "response"; mode = 0
                if data.get("return") == ["__vision mode__"]:   yield "AI agent environment transfered to [bold]vision mode[/bold]", "response";  mode = 1
                if data.get("return") == ["__coder mode__"]:    yield "AI agent environment transfered to [bold]coder mode[/bold]", "response";   mode = 2
                if data.get("return") == ['__clear history__']: self.history = [{f"iteration {iteration}": {f"in previous iteration you cleaned history to avoid polluting the context window, note: {system[0][1] if system[0][1] else None}"}}]
            except TypeError: pass

            try:                                          tool = data["ai_response"]["tool_call"][0].get("tool") if data["ai_response"]["tool_call"] else None
            except (KeyError, TypeError, AttributeError): tool = data["ai_response"]["tool_call"].get("tool") if data["ai_response"]["tool_call"] else None
            
            if tool == "end":
                self.history = []
                yield "[bold]AI agent has finished its work[/bold]", "response"
                return  

    def read(self, path): 
        try: 
            with open(path, "r", encoding="utf-8") as f: return f.read()
        except FileNotFoundError: return "" 

    def replacements(self, text):
        fld = self.read("metadata/folder_linked_data.txt")
        skl = self.read("metadata/skills.txt")

        def get_volume():
            try:
                from pycaw.pycaw import AudioUtilities
                return int((AudioUtilities.GetSpeakers().EndpointVolume.GetMasterVolumeLevelScalar()) * 100)
            except OSError: 
                import pythoncom
                pythoncom.CoInitialize()
                from pycaw.pycaw import AudioUtilities
                volume = int((AudioUtilities.GetSpeakers().EndpointVolume.GetMasterVolumeLevelScalar()) * 100)
                pythoncom.CoUninitialize()
                return volume
            
        return (text
            .replace("___",             ("- *switch_to_vision_mode()*" if self.vision_mode else ""))
            .replace("____",            ("- *switch_to_coder_mode()* <- **important. if the question is related to programming (When you use it, you are transferred to another environment more suitable for programming)**" if self.folder_linked else ""))
            .replace("<windows_user>",  f"Windows username: {getpass.getuser()}")
            .replace("<os>",            f"OS: {self.metadata['OS']}")
            .replace("<os_version>",    f"OS Version: {self.metadata['OS_version']}")
            .replace("<machine>",       f"Machine: {self.metadata['Machine']}")
            .replace("<processor>",     f"Processor: {self.metadata['Processor']}")
            .replace("<gpu>",           f"GPU: {self.metadata['GPU']}")
            .replace("<vram>",          f"VRAM: {self.metadata['VRAM']}")
            .replace("<ram_total>",     f"Total RAM: {self.metadata['RAM_total']}")
            .replace("<volume>",        f"Audio Volume: {get_volume()}%")
            .replace("<ip>",            f"IP: {self.metadata['IP']}")
            .replace("<country>",       f"Country: {self.metadata['country']}" if self.metadata.get("country") else "")
            .replace("<city>",          f"City: {self.metadata['city']}" if self.metadata.get("city") else "")
            .replace("<folder_linked>", (("Folder Linked: \n (When using tool-call, be sure to mark the full link of the marked folder (ONLY WITH '\\' IN PATH))" + fld) if fld else "Folder Linked: None") if self.folder_linked else "Folder Linked: None")
            .replace("<skills>",        f"Skills: \n {skl}" if skl else "")
            .replace("- switch_to_tool_call_mode() - switched your environment to classic tool-call mode", "" if self.coder_mode else "- switch_to_tool_call_mode() - switched your environment to classic tool-call mode ")
        )

    def load(self, model, vision_mode, max_iteration, folder_linked, coder_mode, gen_type):
        with open("metadata/metadata.json", "r", encoding="utf-8") as f:              self.metadata =         json.load(f)
        with open("instructions/instructions.md", "r", encoding="utf-8") as f:        self.classic_instructions = f.read()
        with open("instructions/vision_instructions.md", "r", encoding="utf-8") as f: self.vision_instructions =  f.read()
        with open("instructions/coder_instructions.md", "r", encoding="utf-8") as f:  self.coder_instructions =   f.read()

        (self.max_iteration, self.history, self.vision_mode, self.coder_mode, self.folder_linked, self.model, self.gen_type) = (
            max_iteration,        [],          vision_mode,     coder_mode,       folder_linked,     model,      gen_type    
        ) 

        if self.vision_mode:
            import ocr
            self.ocr = ocr

        self.classic_instructions, self.coder_instructions, self.vision_instructions = (
            self.replacements(self.classic_instructions), self.replacements(self.coder_instructions), self.replacements(self.vision_instructions)
        )

def load_parameters(model):
    try:
        with open("metadata/load_data.json","r",encoding="utf-8") as f:
            data= json.load(f)
    except FileNotFoundError:
        data= {}

    name = os.path.basename(model)
    cached = data.get(name)

    if cached and cached.get("version") == 2:
        return cached["ctx"], cached["n_threads"], cached["gpu_layers"]

    try:
        with open("metadata/metadata.json", "r", encoding="utf-8") as f: metadata = json.load(f)
    except FileNotFoundError: metadata = {}

    def parse_memory(value,unit):
        try: return float(str(value).replace(unit,"").strip())
        except (TypeError,ValueError): return 0.0

    vram_gb, ram_gb = parse_memory(metadata.get("VRAM", "0GB"), "GB"), parse_memory(metadata.get("RAM_available", "0MB"), "MB") / 1024
    model_size = os.path.getsize(model)

    reader = GGUFReader(model)

    def val(key):
        field = reader.fields.get(key)
        if not field:
            return None
        value = field.contents()
        if isinstance(value, (list, tuple)):
            return value[0] if value else None
        return value

    arch = str(val("general.architecture"))
    kv_heads, layers, q_heads, head_dim  = (
        (val(f"{arch}.block_count") or 0), 
        (val(f"{arch}.attention.head_count") or 0), (val(f"{arch}.attention.head_count_kv") or q_heads), 
        (val(f"{arch}.attention.key_length") or val(f"{arch}.attention.head_dim"))
    )   
    if not head_dim and q_heads:
        embed_len= val(f"{arch}.embedding_length")
        if embed_len: head_dim = embed_len // q_heads

    if not layers or not kv_heads or not head_dim:
        error("something went wrong...")

    if vram_gb > 0:
        available_vram = vram_gb * 1024 ** 3
        estimated_model_gpu = available_vram * 0.8
        gpu_layers = min(layers, max(0, int(layers * (estimated_model_gpu / model_size))))
        if gpu_layers >= layers: gpu_layers = -1

    n_threads = max(1, (os.cpu_count() or 1) -1)

    cpu_model_size = model_size * (1 if gpu_layers == 0 else max(0, (layers-gpu_layers) ) / layers)
    available_ram = max(0, ram_gb * 1024 ** 3 - cpu_model_size)

    kv_bytes = 2 * layers * kv_heads * head_dim * 2
    max_ctx = min(int(available_ram / kv_bytes) if kv_bytes else 2048, 131072)

    if max_ctx < 1:
        ctx = 256
    else:
        ctx = 2 ** int(math.log2(max_ctx))
        ctx = max(256, min(ctx, 131072))

    data[name] = { 
        "ctx": ctx,
        "n_threads": n_threads,
        "gpu_layers": gpu_layers
    }

    with open("metadata/load_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return ctx, n_threads, gpu_layers

client = None

def run(gen_type, model, input_, output, stop_event, loaded):
    try:
        if not loaded.is_set():
            if gen_type == "local":
                from llama_cpp import Llama

                n_ctx, n_threads, n_gpu_layers = load_parameters(model)
                client = Llama(model_path=model, n_ctx=n_ctx, verbose=False, n_threads=n_threads, use_mmap=True, use_mlock=False, n_gpu_layers=n_gpu_layers)
            else:
                from openai import OpenAI
                client = OpenAI()

            loaded.set()

        while True:
            try:
                task = input_.get()
            except KeyboardInterrupt:
                break

            if not task:
                break

            content, rid = task
            stop_event.clear()

            try:
                text = ""
                if gen_type == "local":
                    request = client.create_chat_completion(messages=content, stream=True )

                    for chunk in request:
                        if stop_event.is_set():
                            text += "\n[red][bold]generation iterrupted[/red][/bold]"
                            break

                        delta = chunk["choices"][0]["delta"]

                        if "content" in delta:
                            text += delta["content"]

                else:
                    request = client.responses.create(model=model, input=content, stream=True)

                    for event in request:
                        if stop_event.is_set():
                            text += "\n[red][bold]generation iterrupted[/red][/bold]"
                            break

                        if event.type == "response.output_text.delta":
                            text += event.delta

                def extract(t, tag):
                    pattern = rf"<{tag}>(.*?)<(?:/{tag}|{tag})>"
                    match = re.search(pattern, t, re.DOTALL)
                    return match.group(1).strip() if match else None

                output.put((
                    "result",
                    extract(text, "reasoning"),
                    extract(text, "tool_call"),
                    extract(text, "response")
                ))

            except Exception as e:
                import traceback
                output.put(("error", type(e).__name__, str(e), traceback.format_exc()))

    except Exception:
        import traceback
        output.put(("fatal", type(Exception).__name__, "Worker crashed", traceback.format_exc()))

class AI:
    def __init__(self, gen_type, model):
        self.gen_type = gen_type
        self.model = model
        self.input_queue = Queue()
        self.output_queue = Queue()
        self.loaded = Event()
        self.stop_event = Event()

        self.process = Process(
            target=run,
            args=(self.gen_type, self.model, self.input_queue, self.output_queue, self.stop_event, self.loaded),
            daemon=True 
        )
        self.process.start()

    def generate(self, prompt):
        self.input_queue.put((prompt, time.time()))

    def is_loaded(self): 
        return self.loaded.is_set()
    
    def stop_generation(self):
        self.stop_event.set()
        
    def shutdown(self):
        self.input_queue.put(None)
        self.process.join()
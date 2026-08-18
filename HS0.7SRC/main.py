import sys, os, time, config
import threading
from rich import print

class Main: 
    def match_request(self, request):
        match request: 
            case "/switch_to_api":
                self.gen_type = "api" 
                if not os.environ["OPENAI_API_KEY"].strip(): 
                    api = self.ui.inputr(("Enter Your OpenAI API-key << ", self.ui.c1))
                    os.system(f'setx OPENAI_API_KEY "{api}"')
                    os.system('cls') 
                    print("[red]NEED TO RESTART TERMINAL[/red]")
                    sys.exit()
                yield "/reset"
            
            case "/switch_to_local": 
                self.gen_type = "local" 
                self.model = self.ui.inputr("Enter Model Path (.gguf) << ")
                yield "/reset"

            case "/model": 
                not_exists = False
                while True: 
                    model = None
                    if not_exists: print("[red]this model didn't exists[/red]")
                    model = self.ui.inputr(("Choose Your OpenAI Model << " if self.gen_type == "api" else "Enter Model Path (.gguf) << "), self.ui.c1)
                    if model != "/exit": 
                        if self.gen_type == "local": 
                            if os.path.exists(model):
                                self.model = model 
                                break
                            else: not_exists = True
                        else: 
                            self.model = model 
                        self.load_ai()
                        break
                    else:
                        print()
                        yield "/reset"
                        return
                yield "/reset"

            case "/max_iteration": 
                int_error = False 
                zero_error = False 
                save = True
                while True: 
                    if int_error:  print("[red]integer value only[/red]")
                    if zero_error: print("[red]minimum 1 iteration[/red]")
                    
                    i = self.ui.inputr("enter max iteration: ", self.ui.c1)
                    if i == "/exit":
                        save = False
                        break 
                    try: 
                        i = int(i) 
                    except:
                        int_error = True 
                        continue 

                    if i == 0:
                        zero_error = True 
                        continue 

                    if save: self.max_iteration = i 
                    yield "/reset"
                    return
                yield "/reset"
                
            case "/exit":
                self.config_save()
                os.system('cls')
                sys.exit()

            case "/vision_mode": 
                self.vision_mode = not self.vision_mode 
                yield "/reset"
            
            case "/coder_mode":
                if not self.folder_linked and not self.coder_mode: 
                    link, index = self.ui.folder_linked()
                    
                    if index:  folder_index.Indexing(link).run() 
                    elif link: folder_linked.FolderLinked(link)

                    self.folder_linked = link

                self.coder_mode = not self.coder_mode
                yield "/reset"

            case "/link_folder": 
                link, index = self.ui.folder_linked()
                
                if   index: folder_index.Indexing(link).run() 
                elif link:  folder_linked.FolderLinked(link)
                else: os.remove("metadata/folder_linked_data.txt")
                self.folder_linked = link
                yield "/reset"
                
            case "/author": 
                self.ui.notes("Made by [bold]giorgi1805[/bold] with ❤️ for [bold][rgb(36,150,255)]Ic[/rgb(36,150,255)]e[rgb(255,30,0)]l[/rgb(255,30,0)]a[rgb(36,150,255)]nd[/rgb(36,150,255)][/bold]", title="author")
                return

            case "/commands": 
                txt = f"""[{self.ui.c1}][bold]
                \nCommands:\n {"/switch_to_local" if self.gen_type == "api" else "/switch_to_api"}\n /link_folder\n /max_iteration\n /model\n /vision_mode\n /coder_mode\n /skills\n /telegram\n /reset
                [/bold][{self.ui.c1}]"""
                print(txt)

            case "/skills": 
                link = self.ui.skills() 
                if link: skills.skills_save(link)
                else:
                    try: os.remove("metadata/skills.txt")
                    except FileNotFoundError: pass
                self.skill_path = link 
                yield "/reset"

            case "/reset": yield "/reset"

            case "/telegram": 
                while True: 
                    api, choose = self.ui.telegram() 
                    self.tg_api_bot = api
                    if choose == "/run": 
                        self.config_save() 
                        threading.Thread(target=lambda: telegram.run_bot(api, self.match_request, self.model), daemon=True).start()
                        yield "running: [green]true[/green]", "response"
                        break
                    elif choose == "/exit": 
                        return 
                    elif choose == "/change_api": 
                        continue
            case _:  
                for text in self.AI.run(request):
                    yield text

    def run(self): 
        while True:
            reset = False
            self.ui.main(self.model, self.folder_linked, self.vision_mode, self.coder_mode, self.gen_type) 
            self.load_ai()
            while True:
                request = self.ui.inputr("<< ", self.ui.c1)
                
                if not request: 
                    continue

                resp = self.match_request(request)
                
                wr = self.ui.Response(self.max_iteration)
                for res in resp: 
                    if res:
                        if res == "/reset": 
                            reset = True 
                            break 
                        try: 
                            rs, typ = res 
                            wr.write(rs, typ)
                        except KeyboardInterrupt: 
                            self.AI.AI.stop_generation()
                if reset: break 

                while wr.writing: 
                    try: time.sleep(0.01)
                    except KeyboardInterrupt: 
                        wr.stop_event.set()
                        
            self.config_save()

    def load_ai(self):
        self.AI = AI.Start()
        self.AI.load(self.model, self.vision_mode, self.max_iteration, self.folder_linked, self.coder_mode, self.gen_type)
        
    def config_save(self): 
        config.save(self.model, self.vision_mode, self.max_iteration, self.folder_linked, self.coder_mode, self.gen_type, self.tg_api_bot)

    def config_load(self): 
        global skills, telegram, folder_linked, folder_index, AI
        self.model, self.vision_mode, self.max_iteration, self.folder_linked, self.coder_mode, self.gen_type, self.tg_api_bot = config.load_data() 

        if self.gen_type == "local": 
            if not os.path.exists(self.model): 
                
                model = input("Enter Model Path (.gguf) << ")
                if model != "/exit": 
                    self.model = model 
                else:
                    sys.exit() 

                config.save()
        import skills, telegram
        import folder_index, folder_linked
        import AI 


    def __init__(self):
        self.config_load() 
        self.load_ai()
        
        import UI
        self.ui = UI

if __name__ == "__main__": 
    Main().run()

import os, re, json, parsing
from folder_linked import FolderLinked

class IndexParsing: 
    @staticmethod
    def index(path, description): 
        return {path: description}

class Indexing: 
    def __init__(self, folder_path):
        self.folder_path = folder_path

        with open("instructions/index_instructions.md", "r", encoding="utf-8") as f: 
            self.instructions = f.read()
        try:
            with open("metadata/metadata.json", "r", encoding="utf-8") as f: 
                self.metadata = json.load(f) 
        except FileNotFoundError:
            self.metadata = {}

    def extract(self, text):
        text = re.sub(r"<reasoning>.*?</reasoning>", "", text, flags=re.DOTALL)
        text = text.replace("<response>", "").replace("</response>", "").strip()

        json_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL)
        if json_match: text = json_match.group(1)

        text = re.sub(r'\}\s*\{', '}, {', text)
        
        text = text.strip()
        if text.startswith("{") and text.endswith("}"):
            text = f"[{text}]"
            
        return text

    def tree(self, index_dict, current_folder, depth=0, max_depth=5, max_files=20):
        if depth > max_depth:
            return f"{'    ' * depth}|-- ...\n"

        result = []
        try:
            items = sorted(os.listdir(current_folder))
        except Exception as e:
            return f"{'    ' * depth}|-- [ERROR: {e}]\n"

        for i, name in enumerate(items):
            if i >= max_files:
                result.append(f"{'    ' * depth}|-- ... ({len(items) - max_files} more)")
                break

            full_path = os.path.join(current_folder, name)
            rel_path = os.path.normpath(os.path.relpath(full_path, self.folder_path))
            prefix = "    " * depth

            if os.path.isfile(full_path):
                result.append(f"{prefix}|-- {name}")
                result.append(f"{prefix}    |-- DESCRIPTION")
                desc = index_dict.get(rel_path) or index_dict.get(name) or index_dict.get(os.path.normpath(full_path))
                
                if desc:
                    for line in str(desc).split('\n'):
                        result.append(f"{prefix}        | {line}")
                else:
                    result.append(f"{prefix}        | No description")
            else:
                result.append(f"{prefix}|-- {name}/")
                nested_tree = self.tree(index_dict, full_path, depth + 1, max_depth, max_files)
                result.extend(nested_tree.splitlines())
                
        return "\n".join(result)

    def generate(self, instructions):
        text = ""
        if self.metadata["gen_type"] == "api": 
            from openai import OpenAI
            text = OpenAI().responses.create(model="gpt-5.6-luna", input=instructions).output_text 
        else:
            from llama_cpp import Llama
            from AI import load_parameters
            ctx, threads, gpu_layers = load_parameters(self.metadata.get("model"))
            AI = Llama(model_path=self.metadata.get("model"), n_ctx=ctx, n_threads=threads, n_gpu_layers=gpu_layers, verbose=False)
            text = AI.create_chat_completion(messages=[{"role": "user", "content": instructions}])
            text = text["choices"][0]["message"]["content"]
        return text
    
    def run(self):
        FolderLinked(self.folder_path, max_depth=50, max_files=100)

        path_tree = ""
        with open("metadata/folder_linked_data.txt", "r", encoding="utf-8") as f:
            path_tree = f.read()

        instructions = (self.instructions
            .replace("<path_tree>", path_tree)
        )

        system = parsing.run(IndexParsing(), self.extract(self.generate(instructions)))
        
        normalized_index = {}
        if isinstance(system, list):
            for item in system:
                if isinstance(item, dict):
                    for k, v in item.items():
                        normalized_index[os.path.normpath(k)] = v

        tree = self.tree(normalized_index, self.folder_path)

        with open("metadata/folder_linked_data.txt", "w", encoding="utf-8") as f:
            f.write(self.folder_path + "\n" + tree)
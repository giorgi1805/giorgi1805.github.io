import os

class FolderLinked:
    def return_path(self, path=".", depth=0, max_depth=5, max_files=20):
        tree = os.listdir(path)

        full_text = ""
        count = 0
        elements = []

        for i, file in enumerate(tree):
            if i >= max_files:
                full_text += f"|-- ... ({len(tree) - max_files} more)\n"
                break

            full_path = os.path.join(path, file)

            if os.path.isfile(full_path):
                full_text += f"|-- {file}\n"
                elements.append(file)

            else:
                full_text += f"|-- {file}/\n"

                if depth >= max_depth:
                    full_text += "    |-- ...\n"
                    continue

                nested, count_, elements_ = self.return_path(full_path, depth + 1, max_depth, max_files)
                count += count_

                for element in elements_:
                    elements.append(f"{file}/{element}")

                for line in nested.splitlines():
                    full_text += f"    {line}\n"

            count += 1

        return full_text, count, elements

    def __init__(self, path, depth=0, max_depth=5, max_files=20): 
        text, elements_count, elements = self.return_path(path, depth=depth, max_depth=max_depth, max_files=max_files)
        self.return_text = path + "\n" + text

        if elements_count <= max_files:
            for file in elements: 
                self.return_text += self.read_file(f"{path}/{file}")

        with open("metadata/folder_linked_data.txt", "w", encoding="utf-8") as f: 
            f.write(self.return_text) 


    def read_file(self, path):
        with open(path, "r", encoding="utf-8") as f: 
            try:
                file = f.read().strip()
            except UnicodeDecodeError: return f"'''{path}''' \nUnicodeDecodeError while trying to open file"
            return f"'''{path}''' \n{file if file else "[Empty File]"}"
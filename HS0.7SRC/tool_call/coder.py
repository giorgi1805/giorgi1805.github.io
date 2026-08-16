import contextlib
import io
import subprocess
import os
from tool_call.tools import read_file 

class CoderMode: 
    @staticmethod
    def python_code(code):
        output = io.StringIO()

        try:
            with contextlib.redirect_stdout(output):
                local_vars = {}
                exec(code, {}, local_vars)

            return {"result": output.getvalue()}

        except Exception as e:
            return f"Error executing code: {e}"

    @staticmethod
    def file_read(file): 
        return read_file.run(file)

    @staticmethod
    def create_file(path, code, is_binary=False):
        with open(path, "wb" if is_binary else "w", encoding=None if is_binary else "utf-8") as f: 
            f.write(code)
        return {
            "status": f"success, file created in {path}",
            "size": os.path.getsize(path) 
        }, 

    @staticmethod
    def edit_code(file, start_line, end_line, text):
        with open(file, "r", encoding="utf-8") as f:
            lines = f.read().split("\n")

        while len(lines) <= end_line:
            lines.append("")

        edit_lines = text.split("\n")
        while len(edit_lines) <= end_line - start_line:
            edit_lines.append("")

        count = 0
        for line in range(start_line, end_line):
            lines[line] = edit_lines[count]
            count += 1

        with open(file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return "success"

    @staticmethod
    def delete_file(file):
        os.remove(file)
        return f"success, removed {file}"
    
    @staticmethod
    def cmd(command): 
        result = subprocess.run(command, shell=True, capture_output=True)
        if result.stdout:
            return result.stdout.decode("utf-8")
        
    @staticmethod
    def end(comment=None): 
        return "end", comment if comment else None
    
    @staticmethod
    def switch_to_classic_mode(): 
        return "__classic mode__"

    @staticmethod
    def switch_to_vision_mode(): 
        return "__vision mode__"
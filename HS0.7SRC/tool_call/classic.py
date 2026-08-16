import contextlib, io
import webbrowser 
from ddgs import DDGS
import subprocess, os
from tool_call.tools import file_search, read_file, link_requests
from pycaw.pycaw import AudioUtilities

class Classic: 
    @staticmethod
    def open_website(url): 
        webbrowser.open(url)
        return {"status": f"success opening site by url: {url}"}
    
    @staticmethod
    def link_request(url):
        return link_requests.run(url)

    @staticmethod
    def file_read(file): 
        return read_file.run(file) 
    
    @staticmethod
    def ddgs(query, max_results=5):
        text = ""
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            for r in results:
                text += f" <TITLE> {r['title']} </TITLE>\n"
                text += f" <LINK> {r['href']} </LINK>\n"
                text += f" <BODY> {r['body']} </BODY>\n"
                text += "\n"
        return {
            "status": "success", 
            "result": text.strip()
        }
    
    @staticmethod
    def python_code(code):
        output = io.StringIO()

        try:
            with contextlib.redirect_stdout(output):
                local_vars = {}
                exec(code, {}, local_vars)
            return output.getvalue()

        except Exception as e:
            return f"Error executing code: {e}"
    
    @staticmethod
    def set_system_volume(percentage):
        try:
            speakers = AudioUtilities.GetSpeakers()
            volume = speakers.EndpointVolume
            volume.SetMasterVolumeLevelScalar((float(percentage) / 100.0), None)
        except Exception as e:
            return f"Error setting volume: {e}"
        return f"success, volume: {percentage}"

    @staticmethod
    def create_file(path, text=None, is_binary=False): 
        with open(path, "wb" if is_binary else "w", encoding=None if is_binary else "utf-8") as f: 
            f.write(text)
        return {
            "status": f"success, file created in {path}",
            "size": os.path.getsize(path) 
        }, 

    @staticmethod
    def file_search(query, limit=15):
        result = file_search.Search().run(query, limit=limit)
        return {
            "status": "success", 
            "amount": len(result),
            "result": result
        }

    @staticmethod
    def cmd(command): 
        result = subprocess.run(command, shell=True, capture_output=True)
        if result.stdout:
            return result.stdout.decode("utf-8")
        return "success"

    @staticmethod
    def end(): 
        return "end"

    @staticmethod
    def clear_history(note=""):  return "__clear history__", note
    
    @staticmethod
    def switch_to_vision_mode(): return "__vision mode__"

    @staticmethod
    def switch_to_coder_mode():  return "__coder mode__"
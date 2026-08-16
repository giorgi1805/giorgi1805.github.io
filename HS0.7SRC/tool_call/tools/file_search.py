import ctypes
import sys, os
import subprocess
import psutil

def run_everything(path_to_exe):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'Everything.exe':
            return 
        
    subprocess.Popen([path_to_exe, "-startup"], creationflags=subprocess.CREATE_NO_WINDOW)

class Search:
    def run(self, query, limit=5):
        self.everything_dll.Everything_SetSearchW(query)
        self.everything_dll.Everything_SetMax(limit)
        self.everything_dll.Everything_QueryW(True)
        num_results = self.everything_dll.Everything_GetNumResults()
        
        results = []
        buffer = ctypes.create_unicode_buffer(260)
        
        for i in range(num_results):
            self.everything_dll.Everything_GetResultFullPathNameW(i, buffer, 260)
            results.append(buffer.value)
            
        return results
    
    def __init__(self):
        run_everything("everything\\Everything.exe")
        self.everything_dll = ctypes.WinDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), "everything", "Everything64.dll"))
        self.everything_dll.Everything_SetSearchW.argtypes = [ctypes.c_wchar_p]
        self.everything_dll.Everything_QueryW.argtypes = [ctypes.c_bool]
        self.everything_dll.Everything_GetNumResults.restype = ctypes.c_uint32
        self.everything_dll.Everything_GetResultFullPathNameW.argtypes = [ctypes.c_uint32, ctypes.c_wchar_p, ctypes.c_uint32]

if __name__ == "__main__":
    while True:
        try:
            request = input("<< ")
            if not request: continue
            
            results = Search().run(request)
            for f in results:
                print(f)
            print()
                
        except KeyboardInterrupt:
            sys.exit()
import os 

def return_files(path): 
    result = "" 

    for file in os.listdir(path): 
        result += path + "\\" + file + ":" + "\n"
        with open(f"{path}\\{file}", "r", encoding="utf-8") as f: 
            _file = f.read().split("\n")
            for line in _file: 
                result += (" " * 4) + line + "\n"
            
    return result

def skills_save(path): 
    with open("metadata/skills.txt", "w", encoding="utf-8") as f: 
        f.write("The user marked a folder with skills that might be useful to you. \n" + return_files(path))

if __name__ == "__main__": 
    skills_save(input("<< "))
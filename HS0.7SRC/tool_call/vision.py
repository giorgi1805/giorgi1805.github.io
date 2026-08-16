import time, pyautogui

class VisionMode:
    @staticmethod
    def cursor_pos(x, y, duration=0):
        pyautogui.moveTo(x, y, duration=duration)
        return f"success, cursor position: (X: {x}, Y: {y})"
    
    @staticmethod
    def type_on_keyboard(text): 
        pyautogui.write(text)

    @staticmethod
    def click(side): 
        match side: 
            case "left": pyautogui.leftClick()
            case "middle": pyautogui.middleClick()
            case "right": pyautogui.rightClick()
        return f"success"

    @staticmethod
    def switch_to_classic_mode(): 
        return "__classic mode__"
    
    @staticmethod
    def switch_to_coder_mode(): 
        return "__coder mode__"

    @staticmethod
    def time_sleep(sec): 
        time.sleep(sec)
        return f"{sec} have passed"
    
    @staticmethod
    def end(): 
        return "end"
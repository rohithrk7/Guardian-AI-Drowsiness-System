import threading
import pyttsx3
import time
import winsound

is_speaking = False
speech_lock = threading.Lock()
last_beep_time = 0

def play_beep():
    """Play a short high-pitched continuous beep for pre-warning, heavily throttled"""
    global last_beep_time
    current_time = time.time()
    # Play a beep maximum once per second to avoid thread overload
    if current_time - last_beep_time > 1.0:
        last_beep_time = current_time
        def run_beep():
            winsound.Beep(1200, 400) # frequency 1200 Hz, duration 400ms
        t = threading.Thread(target=run_beep)
        t.daemon = True
        t.start()

is_speaking = False
speech_lock = threading.Lock()

def speak_warning(message):
    """
    Uses the pyttsx3 library to speak warning messages aloud on a background thread.
    Prevents overwhelming the audio channel using a speech lock flag.
    """
    global is_speaking
    with speech_lock:
        if is_speaking:
            return
        is_speaking = True
        
    def run_speech():
        global is_speaking
        # Engine is initialized locally inside thread to avoid COM context errors
        local_engine = pyttsx3.init()
        local_engine.setProperty('rate', 160) # Modest speaking pace for clarity
        local_engine.say(message)
        local_engine.runAndWait()
        
        with speech_lock:
            # Add a small delay so repeated warnings aren't instantly back-to-back
            is_speaking = False

    t = threading.Thread(target=run_speech)
    t.daemon = True
    t.start()

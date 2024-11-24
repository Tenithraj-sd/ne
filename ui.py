import eel
import time
import os
import subprocess
import signal
from threading import Thread

# Initialize eel (point to the folder where your HTML/JS files are)
#eel.init("web")  # Ensure the 'web' folder contains your index.html and other files

eel.init(os.path.join(os.path.dirname(__file__), "web")) 
# State variables
i="index.html"


script_process = None
is_running = False

@eel.expose
def start_bot():
    """Starts the bot with a countdown."""
    global is_running
    if is_running:
        eel.update_status("Bot is already running.")
        return

    is_running = True
    eel.update_button("Stop Bot")  # Update button text
    countdown_thread = Thread(target=run_countdown)
    countdown_thread.start()


def run_countdown():
    """Handles the countdown and starts the bot process."""
    global is_running, script_process
    for i in range(5, -1, -1):
        if not is_running:
            eel.update_status("Bot has been stopped.")
            return
        eel.update_status(f"Starting bot in {i} seconds...")
        time.sleep(1)

    if is_running:
        eel.update_status("Bot is now running...")
        try:
            script_path = '/home/tenith/kkkk/BOT/bot.py'  # Update this with your bot's script path
            if not os.path.exists(script_path):
                eel.update_status("Error: Bot script not found.")
                stop_bot()
                return
            script_process = subprocess.Popen(["python3", script_path])
        except Exception as e:
            eel.update_status(f"Error: {str(e)}")
            stop_bot()


@eel.expose
def stop_bot():
    """Stops the bot if it's running."""
    global is_running, script_process
    is_running = False
    if script_process:
        try:
            os.kill(script_process.pid, signal.SIGTERM)
            script_process = None
            eel.update_status("Bot has been stopped.")
        except Exception as e:
            eel.update_status(f"Error: {str(e)}")
    else:
        eel.update_status("No bot is currently running.")
    eel.update_button("Start Bot")  # Update button text


# Start the eel application
if __name__ == "__main__":
    eel.start(i, size=(573, 484))  # Start Eel with the HTML interface

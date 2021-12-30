import sys
import threading
import webbrowser

from .__init__ import create_app

if __name__ == "__main__":

    # For now if any option is passed from CLI, the app will run in debug mode
    if len(sys.argv) > 1:
        mode = "debug"
        create_app(mode).run()

    else:
        mode = "deploy"
        threading.Thread(target=create_app(mode).run).start()
        webbrowser.open("http://127.0.0.1:5000/")

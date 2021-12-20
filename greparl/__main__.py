import threading
import webbrowser

from .__init__ import create_app

create_app().run()
# threading.Thread(target=create_app().run).start()
# webbrowser.open("http://127.0.0.1:5000/")

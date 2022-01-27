import sys
import os
import threading
import webbrowser

from .__init__ import create_app

requirements = {
    "models":"https://aristotleuniversity-my.sharepoint.com/:u:/g/personal/grammenot_office365_auth_gr/EQEWl2-R7n9EnREy6VUDKesBFRaFfdMKeLiVIBblMMYKcA?e=wxaswN",
    "index":"https://aristotleuniversity-my.sharepoint.com/:u:/g/personal/grammenot_office365_auth_gr/EQEWl2-R7n9EnREy6VUDKesBFRaFfdMKeLiVIBblMMYKcA?e=wxaswN",
    "tfidf":"https://aristotleuniversity-my.sharepoint.com/:u:/g/personal/grammenot_office365_auth_gr/EQEWl2-R7n9EnREy6VUDKesBFRaFfdMKeLiVIBblMMYKcA?e=wxaswN",
    "groups":"https://aristotleuniversity-my.sharepoint.com/:u:/g/personal/grammenot_office365_auth_gr/EQEWl2-R7n9EnREy6VUDKesBFRaFfdMKeLiVIBblMMYKcA?e=wxaswN",
    "similarity":"https://aristotleuniversity-my.sharepoint.com/:u:/g/personal/grammenot_office365_auth_gr/EQEWl2-R7n9EnREy6VUDKesBFRaFfdMKeLiVIBblMMYKcA?e=wxaswN",
    "lsa":"https://aristotleuniversity-my.sharepoint.com/:u:/g/personal/grammenot_office365_auth_gr/EQEWl2-R7n9EnREy6VUDKesBFRaFfdMKeLiVIBblMMYKcA?e=wxaswN",
    "speeches.csv":"https://aristotleuniversity-my.sharepoint.com/personal/papadopo_office365_auth_gr/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fpapadopo%5Foffice365%5Fauth%5Fgr%2FDocuments%2FGreek%5FParliament%5FProceedings%5F1989%5F2020%2Ezip&parent=%2Fpersonal%2Fpapadopo%5Foffice365%5Fauth%5Fgr%2FDocuments"
}

def main():
    for req, url in requirements.items():

        # Check for datafile requirements
        if not os.path.exists(req):
            print("-"*10)
            print(f"Error: {req} was not found!")
            print("1. Download the resource from:")
            print(url)
            print("2. Extract it (if needed)")
            print("3. Move it in:")
            print(os.getcwd())
            input("4. Run me again from the above path")
            print("-"*10)
            exit()

    # For now if any option is passed from CLI, the app will run in debug mode
    if len(sys.argv) > 1:
        mode = "debug"
        create_app(mode).run()

    else:
        mode = "deploy"
        threading.Thread(target=create_app(mode).run).start()
        webbrowser.open("http://127.0.0.1:5000/")

if __name__ == "__main__":
    main()

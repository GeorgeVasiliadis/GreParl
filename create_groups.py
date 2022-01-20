from greparl.SearchEngine.preprocessing.group import *
from greparl.SearchEngine.backend.speech_file import SpeechFile

speech_file = SpeechFile("speeches.csv")
create_groups(speech_file, [speaker_name, party])

print("OK")

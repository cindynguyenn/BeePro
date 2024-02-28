import sys
import threading
import PySimpleGUI as sg
from subprocess import call
import time
from datetime import datetime
import sounddevice as sd
from scipy.io.wavfile import write
import subprocess
import os
import dropbox
from dropbox.files import WriteMode

recording = False

dbx = dropbox.Dropbox(oauth2_access_token='sl.BbD7Dtp5MtGlNhQ_oj0s6gcg8YGyRCJ1DpFEnWnk0y_62PujhNqv-ZrYF4HoeGS6WkkUspNS6ug1YJhC76OGXZA7gJudye9KynXxCmgJvXpJFBsrcPvwsWeWVD14jGCIJ85Wppw',
                      oauth2_refresh_token='u77r2SJGMoQAAAAAAAAAAdva7MuROT8Fxj2d-d4PUDAJiXsk4MU6TLvuhm2NDNP2',
                      app_key='ptcoj6p8oukktaz',
                      app_secret='lp06df558e8052v')


directory_to_watch = "/home/pi/Desktop/BeePro"

def upload_to_dropbox(file_name, full_file_path):
    full_file_path = os.path.join(directory_to_watch, file_name)
    try:
        with open(full_file_path, 'rb') as f:
            file_contents = f.read()
        dbx.files_upload(file_contents, '/' + file_name, mode=WriteMode('overwrite'))
        
        # Delete the file
        os.remove(full_file_path)
        
        print(f"Success! Uploaded and deleted {file_name}!")
    except Exception as e:
        print(f"An error occurred with file {file_name}: {e} - Couldn't Upload to DropBox, saved locally.")
    

def record_audio(event, duration, iterations):
    global recording
    fs = 4000
    file_number = 1
          
    i = 0      
    while event != 'Quit' and recording:
        while i in range(iterations):
            now = datetime.now()
            date_string = now.strftime("%m-%d-%Y")
            time_string = now.strftime("%H-%M-%S")
            file_name = f"Beehive{file_number}-{date_string}-{time_string}.wav"                #file_name = "Beehive" + str(file_number) + "-" + date_string + "-" + time_string[0:5] + ".wav"
            print("          ")
                
            print(f"-> Recording File [{file_number}]...")
            myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
            sd.wait()
            write(file_name, fs, myrecording)

            print(f"File saved as {file_name}")
            print(f"{file_number} file(s) recorded in this session so far. Length: {duration} seconds.\n")
                
            file_number += 1
            if event == 'R/U to Google Drive' and recording == True:
                print("-> Saving on Google Drive...")
                print("--------------------------------------------------------------")                    
                call("./googleUpload", shell=True)
                    
            if event == 'R/U to DropBox' and recording == True:
                print("        ")
                print("-> Uploading to DropBox & getting ready to Delete...")
                print("--------------------------------------------------------------")                    
                upload_to_dropbox(file_name, directory_to_watch)
            
            if recording == False:
                break;
                
        i += 1
            
            

class Unbuffered(object):
    def __init__(self, window):
        self.window = window

    def write(self, data):
        self.window.write_event_value("OUT", data)

    def writelines(self, datas):
        self.window.write_event_value("OUT", ''.join(datas))

sg.theme('DarkBlue2')

frame_layout = [[sg.Multiline("", size=(80, 20), autoscroll=True, key='-OUTPUT-', background_color="#111111",
                              text_color="#FFFFFF")]]
layout = [
    [sg.Frame("Output Console", frame_layout)],
    [sg.Text('Duration (in seconds)'), sg.InputText(key='newTime', size=(6,1)), sg.Button('Set')],
    [sg.Text('Iterations'), sg.InputText(key = 'newIteration', size=(6,1)), sg.Button('Iterate')],
    [sg.Button("R/U to Google Drive"), sg.Button('R/U to DropBox'), sg.Button("Run Locally"), sg.Button('Open ML'), sg.Button('Stop'), sg.Button('Quit')]
]

window = sg.Window("BeePro - Version 3.0", layout, finalize=True)
sys.stdout, sys.stderr = Unbuffered(window), Unbuffered(window)
duration = 0
print(" - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
print(" |           __          . '  '  .   ")
print(" |        _/__)         .     .              .    Welcome to BeePro.")
print(" |     (8|)_}}--  .        .               .       Linux Version 3.0  ")
print(" |        `\__)     ' .  .  '  '  .   .  '    ")
print(" - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")

print("-> NOTE: Please set a duration time BEFORE running.\n")
# QUIT BUTTON ---------------------------------------------------------------------------------------------------------
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == 'Quit':
        recording = False  # Stop recording if we're quitting
        print("Quitting Program...")
        call("./closeTerm", shell=True)
        break
# RUN LOCALLY OR GOOGLE UPLOAD ----------------------------------------------------------------------------------------
    elif event in ['Run Locally', 'R/U to Google Drive']:
        if not values ['newTime'] or not values ['newIteration']:
            print("Please set both duration and iterations before starting recording.")
            continue
        recording = True  # Start recording
        duration = int(values['newTime'])
        iterations = int(values['newIteration'])
        threading.Thread(target=record_audio, args=(event, duration, iterations), daemon=True).start()
# DURATION SET BUTTON -------------------------------------------------------------------------------------------------
    elif event == 'Set':
        duration = int(values['newTime'])
        print("--> Duration has been set to: ", duration, "seconds" )
# ITERATION BUTTON ----------------------------------------------------------------------------------------------------
    elif event == 'Iterate':
        iterations = int(values['newIteration'])
        print("--> You have set", iterations, "iterations")
# STOP BUTTON ---------------------------------------------------------------------------------------------------------     
    elif event == 'Stop':  # New event handler for the 'Stop' button
        recording = False  # Stop recording
        print("Recording stopped, next recording will be the final file.")
        time.sleep(1)
        print("STOPPED SESSION...")
# ---------------------------------------------------------------------------------------------------------------------
    elif event == "OUT":
        window['-OUTPUT-'].update(values["OUT"], append=True)
# MACHINE LEARNING ----------------------------------------------------------------------------------------------------
    elif event == 'Open ML':
        print("Running and Uploading to ML. -> Function coming soon.")
# RUN AND UPLOAD TO DROPBOX -------------------------------------------------------------------------------------------
    elif event == 'R/U to DropBox':
        print("\nRunning and Uploading to DropBox. Starting...")
        if not values ['newTime'] or not values ['newIteration']:
            print("Please set both duration and iterations before starting recording.")
            continue
        recording = True  # Start recording
        duration = int(values['newTime'])
        print("--> Duration has been set to: ", duration, "seconds" )
        threading.Thread(target=record_audio, args=(event, duration, iterations), daemon=True).start()
# ---------------------------------------------------------------------------------------------------------------------
sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__
window.close()

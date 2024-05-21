import sys
import threading
import PySimpleGUI as sg
from subprocess import call
import time
from datetime import datetime, date
import sounddevice as sd
from scipy.io.wavfile import write
import subprocess
import os
import dropbox
from dropbox.files import WriteMode
recording = False
# ***********NEED TO FIX R/U TO GOOGLE DRIVE********************
dbx = dropbox.Dropbox(oauth2_access_token='sl.BbD7Dtp5MtGlNhQ_oj0s6gcg8YGyRCJ1DpFEnWnk0y_62PujhNqv-ZrYF4HoeGS6WkkUspNS6ug1YJhC76OGXZA7gJudye9KynXxCmgJvXpJFBsrcPvwsWeWVD14jGCIJ85Wppw',
                      oauth2_refresh_token='u77r2SJGMoQAAAAAAAAAAdva7MuROT8Fxj2d-d4PUDAJiXsk4MU6TLvuhm2NDNP2',
                      app_key='ptcoj6p8oukktaz',
                      app_secret='lp06df558e8052v')
directory_to_watch = "C:/Users/CSUF/Desktop/VSCODE/AUDIO"
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
    
def record_audio(event, duration, fs):
    global recording
    file_number = 1
                    
    while event != 'Quit' and recording:
        now = datetime.now()
        date_string = now.strftime("%m-%d-%Y")
        time_string = now.strftime("%H-%M-%S")
        file_name = f"Beehive{file_number}-{date_string}-{time_string}.wav"                
        
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
                
def record_hourly(event, duration, fs):
    global recording
    file_number = 1

                        
    while event != 'Quit' and recording:
        now = datetime.now()
        current_date = now.date()
        
        if now.minute == 0 and now.second == 0:  # Check if it's the beginning of an hour
            date_string = now.strftime("%m-%d-%Y")
            time_string = now.strftime("%H-%M-%S")
            file_name = f"Beehive{file_number}-{date_string}-{time_string}.wav"                
            
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

def record_start(event, duration, fs, start_time, end_time):
    global recording
    file_number = 1

    while event != 'Quit' and recording:
        now = datetime.now()
        date_string = now.strftime("%m-%d-%Y")
        time_string = now.strftime("%H-%M-%S")
        current_time = now.strftime("%H:%M:00")

        if current_time == start_time.strftime("%H:%M:00"):
            file_name = f"Beehive{file_number}-{date_string}-{time_string}.wav"                

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
        elif current_time == end_time.strftime("%H:%M:00"):
            print("Recording has finished.")
            recording = False

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
    [sg.Text('Desired Sample Rate'), sg.InputText(key = 'sampleRate', size=(6,1)), sg.Button('Set Sample Rate')],
    [sg.Button("R/U to Google Drive"), sg.Button('R/U to DropBox'), sg.Button("Run Continuously"), sg.Button("Run Hourly"), sg.Button('Open ML'), sg.Button('Stop'), sg.Button('Quit')]
    [sg.Text('Start Time (HH:MM)'), sg.InputText(key = 'startTime', size=(10,1)), sg.Text('End Time (HH:MM)'), sg.InputText(key = 'endTime', size=(10,1)), sg.Button('Set Time')],
    [sg.Text('Start Date (MM/DD/YYYY)'), sg.InputText(key = 'startDate', size=(10,1)), sg.Text('End Date (MM/DD/YYYY)'), sg.InputText(key = 'endDate', size=(10,1)), sg.Button('Set Date')],
    [sg.Button("R/U to Google Drive"), sg.Button('R/U to DropBox'), sg.Button("Run Continuously"), sg.Button("Run Hourly"), sg.Button("Start"), sg.Button('Open ML'), sg.Button('Stop'), sg.Button('Quit')]
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
current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%m-%d-%Y %H:%M:%S")
print("The current date and time is:", formatted_datetime)
# QUIT BUTTON ---------------------------------------------------------------------------------------------------------
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == 'Quit':
        recording = False  # Stop recording if we're quitting
        print("Quitting Program...")
        call("./closeTerm", shell=True)
        break
# RUN CONTINUOUSLY OR GOOGLE UPLOAD ----------------------------------------------------------------------------------------
    elif event in ['Run Continuously', 'R/U to Google Drive']:
        if not values ['newTime'] or not values ['sampleRate']: #or not values ['startTime'] or not values ['endTime']:
            print("Please set a duration and sample rate before starting recording.")
            continue
        recording = True  # Start recording
        duration = int(values['newTime'])
        fs = int(values['sampleRate'])
        # start_time = datetime.strptime(values['startTime'], '%H:%M'.time())
        # end_time = datetime.strptime(values['endTime'], '%H:%M'.time())
        threading.Thread(target=record_audio, args=(event, duration, fs), daemon=True).start()
# RECORD EVERY HOUR ----------------------------------------------------------------------------------------------------
    elif event in ['Run Hourly']:
        if not values ['newTime'] or not values ['sampleRate']:
            print("Please set a duration and sample rate before starting recording.")
            continue
        print("You have chosen to record hourly.")
        recording = True  # Start recording
        duration = int(values['newTime'])
        fs = int(values['sampleRate'])
        threading.Thread(target=record_hourly, args=(event, duration, fs), daemon=True).start()
# START AND END TIME ---------------------------------------------------------------------------------------------------
    elif event in ['Start']:
        if not values ['newTime'] or not values ['sampleRate'] or not values ['startTime'] or not values ['endTime']:
            print("Please set a duration, sample rate, start time, and end time before starting recording.")
            continue
        print("RECORDING SHORTLY...")
        recording = True  # Start recording
        duration = int(values['newTime'])
        fs = int(values['sampleRate'])
        start_time = datetime.strptime(values['startTime'], '%H:%M')
        end_time = datetime.strptime(values['endTime'], '%H:%M')
        # start_date = datetime.strptime(values['startDate'], '%m/%d/%Y')
        # end_date = datetime.strptime(values['endDate'], '%m/%d/%Y')
        threading.Thread(target=record_start, args=(event, duration, fs, start_time, end_time), daemon=True).start()
# DURATION SET BUTTON -------------------------------------------------------------------------------------------------
    elif event == 'Set':
        duration = int(values['newTime'])
        print("--> Duration has been set to: ", duration, "seconds" )
# SAMPLE RATE SET BUTTON ----------------------------------------------------------------------------------------------
    elif event == 'Set Sample Rate':
        fs = int(values['sampleRate'])
        print ("--> Your desired sample rate is: ", fs)
# SET TIME BUTTON -----------------------------------------------------------------------------------------------------
    # elif event == 'Set Time':
    #     start_time_str = values['startTime'] + ':00'
    #     end_time_str = values['endTime'] + ':00'
    #     # This will parse the time strings into datetime objects.
    #     start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
    #     end_time = datetime.strptime(end_time_str, '%H:%M:%S').time()
    #     print ("--> Start time has been set to:", start_time, "and end time has been set to:", end_time)
    elif event == 'Set Time':
        start_time_str = values['startTime'] + ':00'
        end_time_str = values['endTime'] + ':00'
        # This will parse the time strings into datetime objects.
        start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
        end_time = datetime.strptime(end_time_str, '%H:%M:%S').time()
        print ("--> Start time has been set to:", start_time, "and end time has been set to:", end_time)
# DATE SET BUTTON -----------------------------------------------------------------------------------------------------
    elif event == 'Set Date':
        start_date_str = values['startDate']
        end_date_str = values['endDate']
        # This will parse the date strings into datetime objects.
        start_date = datetime.strptime(start_date_str, '%m/%d/%Y').time()
        end_date = datetime.strptime(end_date_str, '%m/%d/%Y').time()
        print ("--> Start date has been set to:", start_date, "and end date has been set to:", end_date)
# STOP BUTTON ---------------------------------------------------------------------------------------------------------     
    elif event == 'Stop':  # New event handler for the 'Stop' button
        recording = False  # Stop recording
        print("\nRecording stopped, next recording will be the final file.")
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
        if not values ['newTime'] or not values ['sampleRate']: #or not values ['startTime'] or not values ['endTime']:
            print("Please set a duration and sample rate before starting recording.")
            continue
        recording = True  # Start recording
        duration = int(values['newTime'])
        fs = int(values['sampleRate'])
        # start_time = datetime.strptime(values['startTime'], '%H:%M'.time())
        # end_time = datetime.strptime(values['endTime'], '%H:%M'.time())
        print("--> Duration has been set to: ", duration, "seconds" )
        threading.Thread(target=record_audio, args=(event, duration, fs), daemon=True).start()
# ---------------------------------------------------------------------------------------------------------------------
sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__
window.close()

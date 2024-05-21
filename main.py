# ============================================================================================================================================
# Program Name: "BeePro4.0"                                                                                                                  =
# Program Description: This program is an improved version of BeePro3.0, which is used to record .wav files. The user will be prompted to    =
#                      the duration and sample rate of the files. Then, they will be granted several different options to take the next      =
#                      course of action as to how they would like to record (continuously, hourly, or set a start and end time/date).        =
# ============================================================================================================================================

# ============================================================================================================================================
# Author Information:                                                                                                                        =
#   Author Name: Cindy Nguyen                                                                                                                =
#                Carlos Gunera                                                                                                               =
#   Author Email: ciindynguyen@csu.fullerton.edu                                                                                             =
#                 cgunera@csu.fullerton.edu                                                                                                  =
#                                                                                                                                            =
# Program Information:                                                                                                                       =
#   Program Name: BeePro4.0                                                                                                                  =
#   Program Languages: python                                                                                                                =
#   Assemble: python3 BeePro4.0                                                                                                              =
#   Date of last update: 04/24/2024                                                                                                          =
#   Comments reorganized: 05/20/2024                                                                                                         =
#                                                                                                                                            =
# Purpose:                                                                                                                                   =
#   The purpose of this program is to record .wav audio files from beehives. The GUI has now changed to a CLI, whereas BeePro3.0 was using   =
#   PySimpleGUI.                                                                                                                             =
#                                                                                                                                            =
# Notes:                                                                                                                                     = 
#   - Start and end time work, but do not loop. This has yet to be implemented                                                               =
#   - A function to record_start needs to be added for start and end time.                                                                   =
#   - The start and end date portion of the code still needs to be figured out/worked on.                                                    =
# ============================================================================================================================================

# ===== Begin code area ======================================================================================================================

# Headers and Libraries
import sys
import threading
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

# the Dropbox that audios will automatically get uploaded to
dbx = dropbox.Dropbox(oauth2_access_token='sl.BbD7Dtp5MtGlNhQ_oj0s6gcg8YGyRCJ1DpFEnWnk0y_62PujhNqv-ZrYF4HoeGS6WkkUspNS6ug1YJhC76OGXZA7gJudye9KynXxCmgJvXpJFBsrcPvwsWeWVD14jGCIJ85Wppw',
                      oauth2_refresh_token='u77r2SJGMoQAAAAAAAAAAdva7MuROT8Fxj2d-d4PUDAJiXsk4MU6TLvuhm2NDNP2',
                      app_key='ptcoj6p8oukktaz',
                      app_secret='lp06df558e8052v')

# Directory that recordings will go into. Will need to change for each Pi.
directory_to_watch = "C:/Users/cindy/Desktop/VSCODE/save-the-bees-main"

# ===== upload_to_dropbox ====================================================================================================================
# Purpose: This function will upload the files to the specified dropbox above.                                                               =
# ============================================================================================================================================
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
    
# ===== record_audio =========================================================================================================================
# Purpose: This function will take care of recording the .wav audio files. It will keep track of the file numbers, the date, and the time.   =
#          While it is recording, if you are connected to WiFi then it will automatically upload to the DropBox.                             =
# ============================================================================================================================================
def record_audio(duration, fs):
    global recording
    file_number = 1
                    
    while recording:
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
        print("        ")
        print("-> Uploading to DropBox & getting ready to Delete...")
        print("--------------------------------------------------------------")                    
        upload_to_dropbox(file_name, directory_to_watch)
        
        if not recording:
            break  # Exit the loop when recording is stopped
                
# ===== record_hourly ========================================================================================================================
# Purpose: This function is similar to record_audio, but it will record every hour.                                                          =
# ============================================================================================================================================
def record_hourly(duration, fs):
    global recording
    file_number = 1
                        
    while recording:
        now = datetime.now()
        current_date = now.date()
        
        if now.minute == 0 and now.second == 0:  # Check if it's the beginning of an hour. If it is, then it will record
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
            print("        ")
            print("-> Uploading to DropBox & getting ready to Delete...")
            print("--------------------------------------------------------------")                    
            upload_to_dropbox(file_name, directory_to_watch)
                
# ===== record_start =========================================================================================================================
# Purpose: This function will record at the given start and end time from the user.                                                          =
# ============================================================================================================================================
def record_start(duration, fs, start_time, end_time):
    global recording
    file_number = 1
    
    while recording:
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
            print("        ")
            print("-> Uploading to DropBox & getting ready to Delete...")
            print("--------------------------------------------------------------")                    
            upload_to_dropbox(file_name, directory_to_watch)
        elif current_time == end_time.strftime("%H:%M:00"):
            print("Recording has finished.")
            recording = False

# ===== main =================================================================================================================================
def main():
    
    print(" - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    print(" |           __          . '  '  .   ")
    print(" |        _/__)         .     .              .    Welcome to BeePro.")
    print(" |     (8|)_}}--  .        .               .       Linux Version 4.0  ")
    print(" |        `\__)     ' .  .  '  '  .   .  '    ")
    print(" - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")

    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%m-%d-%Y %H:%M:%S")
    print("The current date and time is:", formatted_datetime)
    
    # Prompt the user to enter the duration of the recording and the sample rate in hertz.=
    print("Set the following parameters before recording: ")
    duration = int(input("Enter the duration (in seconds): "))
    fs = int(input("Enter the desired sample rate (hertz): "))
    
    global recording
    
    # Display menu or options for user to choose from
    print("1. Display options again")
    print("2. Change the sample rate")
    print("3. Set Start and End Time (HH:MM)")
    print("4. Set Start and End Date (MM/DD/YYYY)")
    print("5. R/U to Dropbox")
    print("6. Run Continuously & R/U to Google Drive")
    print("7. Run Hourly")
    print("8. Stop")
    print("9. Quit")
        
    # This will continuously run until the user terminates the program or quits.
    while True:
        choice = input("Enter your choice: ")

    # DISPLAY OPTIONS ------------------------------------------------------------------------------------------------------------------------
        if choice == '1':
            print("1. Display options again")
            print("2. Change the sample rate")
            print("3. Set Start and End Time (HH:MM)")
            print("4. Set Start and End Date (MM/DD/YYYY)")
            print("5. R/U to Dropbox")
            print("6. Run Continuously & R/U to Google Drive")
            print("7. Run Hourly")
            print("8. Stop")
            print("9. Quit")
    # CHANGE SAMPLE RATE ---------------------------------------------------------------------------------------------------------------------
        elif choice == '2':
            fs = int(input("Enter the desired sample rate: "))
    # SET START/END TIME ---------------------------------------------------------------------------------------------------------------------
        elif choice == '3':
            start_time_str = input("Enter start time (HH:MM): ") + ':00'
            end_time_str = input("Enter end time (HH:MM): ") + ':00'
            start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
            end_time = datetime.strptime(end_time_str, '%H:%M:%S').time()
            print ("--> Start time has been set to:", start_time, "and end time has been set to:", end_time)
    # SET START/END DATE ---------------------------------------------------------------------------------------------------------------------
        elif choice == '4':
            start_date_str = input("Enter start date (MM/DD/YYYY): ")
            end_date_str = input("Enter end date (MM/DD/YYYY): ")
            start_date = datetime.strptime(start_date_str, '%m/%d/%Y')
            end_date = datetime.strptime(end_date_str, '%m/%d/%Y')
            print ("--> Start date has been set to:", start_date.strftime('%m/%d/%Y'), "and end date has been set to:", end_date.strftime('%m/%d/%Y'))
    # RUN AND UPLOAD TO DROPBOX --------------------------------------------------------------------------------------------------------------
        elif choice == '5':
            recording = True 
            # Target = Function to Run
            # Args = Function Parameters
            threading.Thread(target=record_audio, args=(duration, fs), daemon=True).start() 
    # RUN CONTINUOUSLY AND UPLOAD TO DROPBOX -------------------------------------------------------------------------------------------------
        elif choice == '6':
            print("RECORDING SHORTLY...")
            if not recording:
                recording = True
                threading.Thread(target=record_audio, args=(duration, fs), daemon=True).start()
            else:
                print("Recording is already in progress.")
    # RECORD EVERY HOUR ----------------------------------------------------------------------------------------------------------------------
        elif choice == '7':
            print("You have chosen to record hourly.")
            if not recording:
                recording = True
                threading.Thread(target=record_hourly, args=(duration, fs), daemon=True).start()
    # STOP RECORDING -------------------------------------------------------------------------------------------------------------------------
        elif choice == '8':
            recording = False
            print("\nRecording stopped, next recording will be the final file.")
            time.sleep(1)
            print("STOPPED SESSION...")
    # QUIT PROGRAM ---------------------------------------------------------------------------------------------------------------------------
        elif choice == '9':
            recording = False 
            print("Quitting Program...")
            break
    # INVALID CHOICE -------------------------------------------------------------------------------------------------------------------------
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

# ============================================================================================================================================
# Program Name: "BeePro4.2"                                                                                                                  =
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
#   Program Name: BeePro4.2                                                                                                                  =
#   Program Languages: python                                                                                                                =
#   Assemble: python3 BeePro4.2.py                                                                                                           =
#   Date of last update: 12/23/2024                                                                                                          =
#   Comments reorganized: 12/23/2024                                                                                                         =
#                                                                                                                                            =
# Purpose:                                                                                                                                   =
#   The purpose of this program is for the crontab scheduler. This script is expected to run upon reboot.                                    =
#                                                                                                                                            =
# ============================================================================================================================================

# ===== Begin code area ======================================================================================================================

# Headers and Libraries
import sys
import threading
from subprocess import call
import time
from datetime import datetime, date
import sounddevice as sd
#sd.default.device = 1
from scipy.io.wavfile import write
import subprocess
import os
import dropbox
from dropbox.files import WriteMode
import shutil
import glob

recording = False

# the Dropbox that audios will automatically get uploaded to
dbx = dropbox.Dropbox(oauth2_access_token='sl.B7z7a04s9IBWQG8uF8-gOnGPFma9GB0dB6Q5cXxDTAVY2Av6-2k8rYz4Kvd7fnnSoSUkok_K848WiexQtMHlYXwZR6Aqwv6V-kpYsYqNQjlkDCWfaf0kvjtkwOlh0pmGNYkn_thVE8x2',
                      oauth2_refresh_token='MjxH2b0hqvgAAAAAAAAAASqfaQrRyqUWIKS9Dy6hG6JO0Tq8M-2-pnvL2zgJXEzI',
                      app_key='ikerpv0y7y18rwh',
                      app_secret='k7r1mm0p6afss5f')

# Directory that recordings will go into. Will need to change for each Pi.
directory_to_watch = "/media/rpi2/RPi2/BP-mic1/Recording"
source_directory = "/media/rpi2/RPi2/BP-mic1"


# ===== upload_to_dropbox ====================================================================================================================
# Purpose: This function will upload the files to the specified dropbox above. Ther recordings get deleted from the Pi once it has been      =
#          uploaded. WiFi connection is required.                                                                                            =
# ============================================================================================================================================
# def upload_to_dropbox(file_name, full_file_path):
#     full_file_path = os.path.join(directory_to_watch, file_name)
#     try:
#         with open(full_file_path, 'rb') as f:
#             file_contents = f.read()
#         dbx.files_upload(file_contents, '/' + file_name, mode=WriteMode('overwrite'))
#         
#         # Delete the file
#         os.remove(full_file_path)
#         
#         print(f"Success! Uploaded and deleted {file_name}!")
#     except Exception as e:
#         print(f"An error occurred with file {file_name}: {e} - Couldn't Upload to DropBox, saved locally.")
    
# ===== record_audio =========================================================================================================================
# Purpose: This function will take care of recording the .wav audio files. It will keep track of the file numbers, the date, and the time.   =
#          When it is done recording, it will save it locally.                                                                               =
# ============================================================================================================================================
def record_audio(beehive, duration, fs):
    global recording
    file_number = 1
                    
    while recording:
        now = datetime.now()
        date_string = now.strftime("%m-%d-%Y")
        time_string = now.strftime("%H-%M-%S")
        # File name includes the name of the Beehive, date, and time of recording 
        file_name = f"{beehive}{file_number}-{date_string}-{time_string}.wav"                  
        
        print(f"-> Recording File [{file_number}]...")
        myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        write(file_name, fs, myrecording)

        print(f"File saved as {file_name}")
        print(f"{file_number} file(s) recorded in this session so far. Length: {duration} seconds.\n")
            
        file_number += 1
        
        move_files(source_directory, file_name, directory_to_watch)
        
        if not recording:
            break  # Exit the loop when recording is stopped
        

        
# ===== record_dropbox =======================================================================================================================
# Purpose: This function will take care of recording the .wav audio files. It will keep track of the file numbers, the date, and the time.   =
#          While it is recording, if you are connected to WiFi then it will automatically upload to the DropBox.                             =
# ============================================================================================================================================
# def record_dropbox(beehive, duration, fs):
#     global recording
#     file_number = 1
#                     
#     while recording:
#         now = datetime.now()
#         date_string = now.strftime("%m-%d-%Y")
#         time_string = now.strftime("%H-%M-%S")
#         # File name includes the name of the Beehive, date, and time of recording 
#         file_name = f"{beehive}{file_number}-{date_string}-{time_string}.wav"                  
#         
#         print(f"-> Recording File [{file_number}]...")
#         myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
#         sd.wait()
#         write(file_name, fs, myrecording)
# 
#         print(f"File saved as {file_name}")
#         print(f"{file_number} file(s) recorded in this session so far. Length: {duration} seconds.\n")
#             
#         file_number += 1
#         
#         move_files(source_directory, file_name, directory_to_watch)
# 
#         # This code below will upload the recordings to Dropbox. 
#         print("        ")
#         print("-> Uploading to DropBox & getting ready to Delete...")
#         print("--------------------------------------------------------------")                    
#         upload_to_dropbox(file_name, directory_to_watch)
#         
#         if not recording:
#             break  # Exit the loop when recording is stopped
#         
def move_files(source_directory, file_pattern, destination_directory):
    # Ensure the destination directory exists
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    # Construct the pattern path
    pattern = os.path.join(source_directory, file_pattern)
    
    # List all files matching the pattern
    files_to_move = glob.glob(pattern)
    
    # Move each file to the destination directory
    for file_path in files_to_move:
        # Construct the destination path for each file
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(destination_directory, file_name)
        
        try:
            shutil.move(file_path, dest_path)
            print(f"Moved: {file_path} -> {dest_path}")
        except Exception as e:
            print(f"Error moving file {file_path}: {e}")
                
# ===== record_hourly ========================================================================================================================
# Purpose: This function is similar to record_audio, but it will record every hour.                                                          =
# ============================================================================================================================================
# def record_hourly(beehive, duration, fs):
#     global recording
#     file_number = 1
#                         
#     while recording:
#         now = datetime.now()
#         current_date = now.date()
#         
#         if now.minute == 0 and now.second == 0:  # Check if it's the beginning of an hour. If it is, then it will record
#             date_string = now.strftime("%m-%d-%Y")
#             time_string = now.strftime("%H-%M-%S")
#             file_name = f"{beehive}{file_number}-{date_string}-{time_string}.wav"               
#             
#             print(f"-> Recording File [{file_number}]...")
#             myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
#             sd.wait()
#             write(file_name, fs, myrecording)
# 
#             print(f"File saved as {file_name}")
#             print(f"{file_number} file(s) recorded in this session so far. Length: {duration} seconds.\n")
#                 
#             file_number += 1
#             print("        ")
#             print("-> Uploading to DropBox & getting ready to Delete...")
#             print("--------------------------------------------------------------")                    
#             upload_to_dropbox(file_name, directory_to_watch)
#                 
# ===== record_start =========================================================================================================================
# Purpose: This function will record at the given start and end time from the user.                                                          =
# ============================================================================================================================================
def record_start(beehive, duration, fs, start_time, end_time):
    global recording
    file_number = 1
    
    while recording:
        now = datetime.now()
        date_string = now.strftime("%m-%d-%Y")
        time_string = now.strftime("%H-%M-%S")
        current_time = now.strftime("%H:%M:00")
                    
        if current_time == start_time.strftime("%H:%M:00"):
            file_name = f"{beehive}{file_number}-{date_string}-{time_string}.wav"             
            
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
        # If the current time is the end time, it will stop recording.
        elif current_time == end_time.strftime("%H:%M:00"):
            print("Recording has finished.")
            recording = False

# ===== main =================================================================================================================================
def main():
    
    print(" - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    print(" |           __          . '  '  .   ")
    print(" |        _/__)         .     .              .    Welcome to BeePro.")
    print(" |     (8|)_}}--  .        .               .       Linux Version 4.1  ")
    print(" |        `\__)     ' .  .  '  '  .   .  '    ")
    print(" - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")

    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%m-%d-%Y %H:%M:%S")
    print("The current date and time is:", formatted_datetime)
    
    # Prompt the user to enter the duration of the recording and the sample rate in hertz.=
    #print("Set the following parameters before recording: ")
    #beehive = input("Enter the name of the beehive you are recording: ")
    #duration = int(input("Enter the duration (in seconds): "))
    #fs = int(input("Enter the desired sample rate (hertz): "))
    
    beehive = "MH1B_"
    duration = 6
    fs = 44100
        
    global recording
    
    # Display menu or options for user to choose from
#     print("1. Display options again")
#     print("2. Change the sample rate")
#     print("3. Set Start and End Time (HH:MM)")
#     print("4. Set Start and End Date (MM/DD/YYYY)")
#     print("5. R/U to Dropbox")
#     print("6. Run Continuously & R/U to Google Drive")
#     print("7. Run Hourly")
#     print("8. Stop")
#     print("9. Quit")
    
    while True:
        print("RECORDING SHORTLY...")
        if not recording:
            recording = True
            threading.Thread(target=record_audio, args=(beehive, duration, fs), daemon=True).start()
        else:
            print("Recording is already in progress.")
            
        time.sleep(60)
        
    # This will continuously run until the user terminates the program or quits.
#     while True:
#         #choice = input("Enter your choice: ")
#         #choice = sys.stdin.readline().strip()
#         #choice = choice.strip("'")
#         #print(f"'{repr(choice)}'")
#         #time.sleep(60000)
# 
#     # DISPLAY OPTIONS ------------------------------------------------------------------------------------------------------------------------
#         if choice == '1':
#             print("1. Display options again")
#             print("2. Change the sample rate")
#             print("3. Set Start and End Time (HH:MM)")
#             print("4. Set Start and End Date (MM/DD/YYYY)")
#             print("5. R/U to Dropbox")
#             print("6. Run Continuously & Upload Locally")
#             print("7. Run Hourly")
#             print("8. Stop")
#             print("9. Quit")
#     # CHANGE SAMPLE RATE ---------------------------------------------------------------------------------------------------------------------
#         elif choice == '2':
#             fs = int(input("Enter the desired sample rate: "))
#     # SET START/END TIME ---------------------------------------------------------------------------------------------------------------------
#         elif choice == '3':
#             start_time_str = input("Enter start time (HH:MM): ") + ':00'
#             end_time_str = input("Enter end time (HH:MM): ") + ':00'
#             start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
#             end_time = datetime.strptime(end_time_str, '%H:%M:%S').time()
#             print ("--> Start time has been set to:", start_time, "and end time has been set to:", end_time)
#     # SET START/END DATE ---------------------------------------------------------------------------------------------------------------------
#         elif choice == '4':
#             start_date_str = input("Enter start date (MM/DD/YYYY): ")
#             end_date_str = input("Enter end date (MM/DD/YYYY): ")
#             start_date = datetime.strptime(start_date_str, '%m/%d/%Y')
#             end_date = datetime.strptime(end_date_str, '%m/%d/%Y')
#             print ("--> Start date has been set to:", start_date.strftime('%m/%d/%Y'), "and end date has been set to:", end_date.strftime('%m/%d/%Y'))
#     # RUN AND UPLOAD TO DROPBOX --------------------------------------------------------------------------------------------------------------
#         elif choice == '5':
#             recording = True 
#             # Target = Function to Run
#             # Args = Function Parameters
#             threading.Thread(target=record_dropbox, args=(beehive, duration, fs), daemon=True).start() 
#     # RUN CONTINUOUSLY AND UPLOAD TO DROPBOX -------------------------------------------------------------------------------------------------
#         elif choice == '6':
#             print("RECORDING SHORTLY...")
#             if not recording:
#                 recording = True
#                 threading.Thread(target=record_audio, args=(beehive, duration, fs), daemon=True).start()
#             else:
#                 print("Recording is already in progress.")
#     # RECORD EVERY HOUR ----------------------------------------------------------------------------------------------------------------------
#         elif choice == '7':
#             print("You have chosen to record hourly.")
#             if not recording:
#                 recording = True
#                 threading.Thread(target=record_hourly, args=(beehive, duration, fs), daemon=True).start()
#     # STOP RECORDING -------------------------------------------------------------------------------------------------------------------------
#         elif choice == '8':
#             recording = False
#             print("\nRecording stopped, next recording will be the final file.")
#             time.sleep(1)
#             print("STOPPED SESSION...")
#     # QUIT PROGRAM ---------------------------------------------------------------------------------------------------------------------------
#         elif choice == '9':
#             recording = False 
#             print("Quitting Program...")
#             break
#     # INVALID CHOICE -------------------------------------------------------------------------------------------------------------------------
#         else:
#             print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()


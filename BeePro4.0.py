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

# REMINDER FOR SELF
# START AND END TIME WORK, BUT DO NOT LOOP. HAS NOT BEEN IMPLEMENTED YET
# ADD OPTION TO RECORD_START FOR START AND END TIME
# FIGURE OUT START AND END DATE PORTION OF CODE
# maybe fix r/u to drpobox and google drive. make separate functions so error does not show up while we are waiting on wifi?
# FIX THE NAMING PATH!!

recording = False

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
                
def record_hourly(duration, fs):
    global recording
    file_number = 1
                        
    while recording:
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
            print("        ")
            print("-> Uploading to DropBox & getting ready to Delete...")
            print("--------------------------------------------------------------")                    
            upload_to_dropbox(file_name, directory_to_watch)
                
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
    
    print("Set the following parameters before recording: ")
    duration = int(input("Enter the duration (in seconds): "))
    fs = int(input("Enter the desired sample rate: "))
    
    global recording
    
    # Display menu or options
    print("1. Display options again")
    print("2. Change the sample rate")
    print("3. Set Start and End Time (HH:MM)")
    print("4. Set Start and End Date (MM/DD/YYYY)")
    print("5. R/U to Dropbox")
    print("6. Run Continuously & R/U to Google Drive")
    print("7. Run Hourly")
    print("8. Stop")
    print("9. Quit")
        
    while True:
        
        choice = input("Enter your choice: ")
        
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
        elif choice == '2':
            fs = int(input("Enter the desired sample rate: "))
        elif choice == '3':
            start_time_str = input("Enter start time (HH:MM): ") + ':00'
            end_time_str = input("Enter end time (HH:MM): ") + ':00'
            start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
            end_time = datetime.strptime(end_time_str, '%H:%M:%S').time()
            print ("--> Start time has been set to:", start_time, "and end time has been set to:", end_time)
        elif choice == '4':
            start_date_str = input("Enter start date (MM/DD/YYYY): ")
            end_date_str = input("Enter end date (MM/DD/YYYY): ")
            start_date = datetime.strptime(start_date_str, '%m/%d/%Y')
            end_date = datetime.strptime(end_date_str, '%m/%d/%Y')
            print ("--> Start date has been set to:", start_date.strftime('%m/%d/%Y'), "and end date has been set to:", end_date.strftime('%m/%d/%Y'))
        elif choice == '5':
            recording = True 
            threading.Thread(target=record_audio, args=(duration, fs), daemon=True).start()
        elif choice == '6':
            print("RECORDING SHORTLY...")
            if not recording:
                recording = True
                threading.Thread(target=record_audio, args=(duration, fs), daemon=True).start()
            else:
                print("Recording is already in progress.")
        elif choice == '7':
            print("You have chosen to record hourly.")
            if not recording:
                recording = True
                threading.Thread(target=record_hourly, args=(duration, fs), daemon=True).start()
        elif choice == '8':
            recording = False
            print("\nRecording stopped, next recording will be the final file.")
            time.sleep(1)
            print("STOPPED SESSION...")
        elif choice == '9':
            recording = False 
            print("Quitting Program...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

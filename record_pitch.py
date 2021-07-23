import threading
import numpy as np
import pyaudio
import sys
import aubio
import datetime
import time
from easytello import tello

# Some constants for setting the PyAudio and the
# Aubio.
BUFFER_SIZE = 1024
CHANNELS = 1
FORMAT = pyaudio.paFloat32
METHOD = "default"
SAMPLE_RATE = 44100
HOP_SIZE = BUFFER_SIZE // 2
PERIOD_SIZE_IN_FRAME = HOP_SIZE
SECONDS_IN_MINUT = 60
PITCH_TIMEFRAME = 2
VOLUME_TIMEFRAME = 800000
PITCH_THESHHOLD = 0.0
pitchList = [35, 45, 55, 65, 75, 85]  # [D2,A2,G3,F4,E5,C6]
PITCH_COUNTER_THRESH = 10
VOLUME_THRESH = 100.0
MOVING_DISTANCE = 20
INITIAL_TAKEOFF = 30
MINIMUM_BATTERY = 30


def main(args):
    txt_file = open("Recording.txt", "r+")
    txt_file.truncate(0)
    txt_file.close()

    txt_file = open("Recording.txt", "a")
    x = threading.Thread(target=active_listening, args=(txt_file,), daemon=True)
    x.start()
    user_input(txt_file)


def user_input(file):
    while True:
        command = input("Enter close:")
        if command == "close":
            file.write("EOF")
            file.close()
            sys.exit()


def active_listening(txt_file):
    # Initiating PyAudio object.
    pA = pyaudio.PyAudio()
    # Open the microphone stream.
    mic = pA.open(format=FORMAT, channels=CHANNELS,
                  rate=SAMPLE_RATE, input=True,
                  frames_per_buffer=PERIOD_SIZE_IN_FRAME)

    # setup pitch
    tolerance = 0.8
    win_s = 4096  # fft size
    hop_s = BUFFER_SIZE  # hop size
    pitch_o = aubio.pitch("default", win_s, hop_s, SAMPLE_RATE)
    pitch_o.set_unit("midi")
    pitch_o.set_tolerance(tolerance)

    # Infinite loop!
    pitch_past = datetime.datetime.now()
    volume_past = datetime.datetime.now()
    pitch_list = []
    pitch_counter = [0, 0, 0, 0, 0, 0]
    while True:

        # Always listening to the microphone.
        data = mic.read(BUFFER_SIZE)
        # Convert into number that Aubio understand.
        samples = np.frombuffer(data, dtype=aubio.float_type)

        # Finally get the pitch.
        # pitch = pDetection(samples)[0]
        signal = np.frombuffer(data, dtype=np.float32)

        pitch = pitch_o(signal)[0]
        confidence = pitch_o.get_confidence()

        if pitch > PITCH_THESHHOLD:
            pitch_list.append(pitch)
            txt_file.write(str(pitch) + "\n")

        #  -------------------PITCH-------------------
        pitch_present = datetime.datetime.now()
        pitch_time_difference = pitch_present - pitch_past

        # Finally print the pitch and the volume if time length threshold passed.
        if divmod(pitch_time_difference.total_seconds(), SECONDS_IN_MINUT)[1] >= PITCH_TIMEFRAME:
            txt_file.write("-1 \n")

            # if no pitch was detected then do not print pitches
            if len(pitch_list) != 0:
                for value in pitch_list:

                    # round values to closest pre defined pitch value
                    index = int(value) // 10 - 3

                    # check if value is within range
                    if 0 <= index <= 5:
                        pitch_counter[index] += 1
            print(pitch_counter)
            max_value = max(pitch_counter)
            max_value_index = pitch_counter.index(max_value)

            # if max value counter is higher than threshold then print pitch
            if max_value > PITCH_COUNTER_THRESH:
                pass
                print("pitch is " + str(pitchList[max_value_index]))

            else:
                pass
                print("No pitch is detected ")

            # reset values of pitch_list and pitch counter
            pitch_list = []
            pitch_counter = [0, 0, 0, 0, 0, 0]
            pitch_past = pitch_present


if __name__ == "__main__": main(sys.argv)

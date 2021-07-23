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
    my_drone = tello.Tello()
    recordings = open("Recording.txt", "r")
    x = threading.Thread(target=active_listening, args=(my_drone, recordings,), daemon=True)
    x.start()
    user_input(recordings, my_drone, )


def user_input(file, my_drone):
    while True:
        command = input("Enter close:")
        if command == "close":
            file.close()
            my_drone.land()
            sys.exit()


def active_listening(my_drone, recordings):
    pitch_past = datetime.datetime.now()
    pitch_list = []
    pitch_counter = [0, 0, 0, 0, 0, 0]
    height = [1, 0, 0, 0, 0, 0]

    battery = my_drone.get_battery()
    if battery < MINIMUM_BATTERY:
        print("Battery  is too low !!!! battery :" + str(my_drone.get_battery()))
        return
    print("Battery :" + str(my_drone.get_battery()))

    time.sleep(2)

    my_drone.takeoff()
    time.sleep(1)
    my_drone.up(INITIAL_TAKEOFF)
    time.sleep(1)
    while True:
        line = recordings.readline()

        if line == "EOF":
            sys.exit()
        pitch = float(line)

        if pitch > PITCH_THESHHOLD:
            pitch_list.append(pitch)

        if pitch == -1:

            # if no pitch was detected then do not print pitches
            if len(pitch_list) != 0:
                for value in pitch_list:

                    # round values to closest pre defined pitch value
                    index = int(value) // 10 - 3

                    # check if value is within range
                    if 0 <= index <= 5:
                        pitch_counter[index] += 1
            # print(pitch_list)
            print(pitch_counter)

            max_value = max(pitch_counter)
            max_value_index = pitch_counter.index(max_value)

            # get current height
            height_index = height.index(max(height))

            # if max value counter is higher than threshold then print pitch
            if max_value > PITCH_COUNTER_THRESH:
                pass
                print("pitch is " + str(pitchList[max_value_index]))
                # check which direction to move
                difference = (max_value_index - height_index) * MOVING_DISTANCE
                if difference != 0:
                    if difference > 0:
                        my_drone.up(difference)
                    elif difference < 0:
                        my_drone.down(-difference)
                    time.sleep(1)
                    my_drone.forward(MOVING_DISTANCE)
                    time.sleep(1)
                height[height_index] = 0
                height[max_value_index] = 1
            else:
                pass
                print("No pitch is detected ")

            # reset values of pitch_list and pitch counter
            pitch_list = []
            pitch_counter = [0, 0, 0, 0, 0, 0]


if __name__ == "__main__": main(sys.argv)

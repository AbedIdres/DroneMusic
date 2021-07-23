# This is a simple demonstration on how to stream
# audio from microphone and then extract the pitch
# and volume directly with help of PyAudio and Aubio
# Python libraries. The PyAudio is used to interface
# the computer microphone. While the Aubio is used as
# a pitch detection object. There is also NumPy
# as well to convert format between PyAudio into
# the Aubio.


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
    x = threading.Thread(target=active_listening, args=(my_drone,), daemon=True)
    x.start()
    x.join()

    dance(my_drone)


def dance(my_drone):
    while 1:
        command = input("Enter command, UP, DOWN, LEFT , RIGHT , LAND , FORWARD , BACK , TAKEOFF:")
        if command == "UP":
            my_drone.up(MOVING_DISTANCE)
        elif command == "DOWN":
            my_drone.down(MOVING_DISTANCE)
        elif command == "LEFT":
            my_drone.left(MOVING_DISTANCE)
        elif command == "RIGHT":
            my_drone.right(MOVING_DISTANCE)
        elif command == "LAND":
            my_drone.land()
        elif command == "FORWARD":
            my_drone.forward(MOVING_DISTANCE)
        elif command == "BACK":
            my_drone.back(MOVING_DISTANCE)
        elif command == "TAKEOFF":
            my_drone.takeoff()
            my_drone.wait(1)
            my_drone.up(INITIAL_TAKEOFF)

        my_drone.wait(1)


def active_listening(my_drone):
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
    height = [1, 0, 0, 0, 0, 0]

    battery = my_drone.get_battery()
    if battery < MINIMUM_BATTERY:
        print("Battery  is too low !!!! battery :" + str(my_drone.get_battery()))
        return
    print("Battery :" + str(my_drone.get_battery()))
    time.sleep(2)

    my_drone.takeoff()

    while True:

        # Always listening to the microphone.
        data = mic.read(BUFFER_SIZE)
        # Convert into number that Aubio understand.
        samples = np.frombuffer(data, dtype=aubio.float_type)

        # Finally get the pitch.
        # pitch = pDetection(samples)[0]
        signal = np.frombuffer(data, dtype=np.float32)

        pitch = pitch_o(signal)[0]

        if pitch > PITCH_THESHHOLD:
            pitch_list.append(pitch)

        #  -------------------PITCH-------------------
        pitch_present = datetime.datetime.now()
        pitch_time_difference = pitch_present - pitch_past

        # Finally print the pitch and the volume if time length threshold passed.
        if divmod(pitch_time_difference.total_seconds(), SECONDS_IN_MINUT)[1] >= PITCH_TIMEFRAME:

            # if no pitch was detected then do not print pitches
            if len(pitch_list) != 0:
                for value in pitch_list:

                    # round values to closest pre defined pitch value
                    index = int(value) // 10 - 3

                    # check if value is within range
                    if 0 <= index <= 5:
                        pitch_counter[index] += 1

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

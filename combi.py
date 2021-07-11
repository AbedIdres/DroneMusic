# This is a simple demonstration on how to stream
# audio from microphone and then extract the pitch
# and volume directly with help of PyAudio and Aubio
# Python libraries. The PyAudio is used to interface
# the computer microphone. While the Aubio is used as
# a pitch detection object. There is also NumPy
# as well to convert format between PyAudio into
# the Aubio.

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
pitchList = [35, 45, 55, 65, 75, 85]
PITCH_COUNTER_THRESH = 3
VOLUME_THRESH = 100.0
MOVING_DISTANCE = 15


def main(args):
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
    height = [0, 1, 0, 0, 0, 0]

    volume_list = []
    volume_power = 0
    my_drone = tello.Tello()
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
        confidence = pitch_o.get_confidence()

        if pitch > PITCH_THESHHOLD:
            pitch_list.append(pitch)
        # Compute the energy (volume)
        # of the current frame.
        volume = np.sum(samples ** 2) / len(samples)
        volume *= 100000
        volume_list.append(volume)

        # Format the volume output so it only
        # displays at most six numbers behind 0.
        volume = "{:6f}".format(volume)
        # print(str(volume))

        ############################VOLUME############################
        volume_present = datetime.datetime.now()
        volume_time_difference = volume_present - volume_past



        if volume_time_difference.microseconds > VOLUME_TIMEFRAME:
            if len(volume_list) != 0:
                volume_average = sum(volume_list) / len(volume_list)
            else:
                volume_average = 0
            #print(volume_list)
            #print("volume_average = " + str(volume_average))
            if volume_average > VOLUME_THRESH and volume_power < 10:
                volume_power = volume_power + 1
                print("Added 1 to volume power, now its " + str(volume_power))
            else:
                if volume_power > 0:
                    volume_power = volume_power // 3
                    print("subtracted 1 to volume power, now its " + str(volume_power))
            volume_list = []
            volume_past = volume_present




        ############################PITCH############################

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
            # print(pitch_list)
            # print(pitch_counter)
            # print(" volume = {} / pitch = {} / confidence  ={}".format(str(volume),pitch,confidence))
            max_value = max(pitch_counter)
            max_value_index = pitch_counter.index(max_value)
            # if max value counter is higher than threshold then print pitch

            # get current height
            height_index = height.index(max(height))





            if max_value > PITCH_COUNTER_THRESH:
                pass
                print("pitch is " + str(pitchList[max_value_index]))
                # check which direction to move
                difference = (max_value_index - height_index) * MOVING_DISTANCE
                if difference > 0:
                    my_drone.up(difference)
                elif difference < 0:
                    my_drone.down(-difference)

                height[height_index] = 0
                height[max_value_index] = 1
            else:
                pass
                print("No pitch is detected ")
            # reset values of pitch_list and pitch counter
            pitch_list = []
            pitch_counter = [0, 0, 0, 0, 0, 0]
            pitch_past = pitch_present


def dance(my_drone):

    my_drone.takeoff()

    while 1:
        command = input("Enter command, UP, DOWN, LEFT , RIGHT , LAND , FORWARD , BACK:")
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
        else:
            my_drone.flip(360)

        my_drone.wait(2)

if __name__ == "__main__": main(sys.argv)

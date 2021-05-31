# This is a simple demonstration on how to stream
# audio from microphone and then extract the pitch
# and volume directly with help of PyAudio and Aubio
# Python libraries. The PyAudio is used to interface
# the computer microphone. While the Aubio is used as
# a pitch detection object. There is also NumPy
# as well to convert format between PyAudio into
# the Aubio.
import aubio
import numpy as np
import pyaudio
import sys

import pyaudio
import aubio

# Some constants for setting the PyAudio and the
# Aubio.
BUFFER_SIZE             = 1024
CHANNELS                = 1
FORMAT                  = pyaudio.paFloat32
METHOD                  = "default"
SAMPLE_RATE             = 44100
HOP_SIZE                = BUFFER_SIZE//2
PERIOD_SIZE_IN_FRAME    = HOP_SIZE



def main(args):

    # Initiating PyAudio object.
    pA = pyaudio.PyAudio()
    # Open the microphone stream.
    mic = pA.open(format=FORMAT, channels=CHANNELS,
        rate=SAMPLE_RATE, input=True,
        frames_per_buffer=PERIOD_SIZE_IN_FRAME)

#     # Initiating Aubio's pitch detection object.
#     pDetection = aubio.pitch(METHOD, BUFFER_SIZE,
#         HOP_SIZE, SAMPLE_RATE)
#     # Set unit.
#     pDetection.set_unit("Hz")
#     # Frequency under -40 dB will considered
#     # as a silence.
#     pDetection.set_silence(-40)
#

    
    # setup pitch
    tolerance = 0.8
    win_s = 4096 # fft size
    hop_s = BUFFER_SIZE # hop size
    pitch_o = aubio.pitch("default", win_s, hop_s, SAMPLE_RATE)
    pitch_o.set_unit("midi")
    pitch_o.set_tolerance(tolerance)
    
    # Infinite loop!
    while True:

        # Always listening to the microphone.
        data = mic.read(BUFFER_SIZE)
        # Convert into number that Aubio understand.
        samples = np.fromstring(data,
            dtype=aubio.float_type)
            
        # Finally get the pitch.
        #pitch = pDetection(samples)[0]
        signal = np.fromstring(data, dtype=np.float32)

        pitch = pitch_o(signal)[0]
        confidence = pitch_o.get_confidence()
            
        # Compute the energy (volume)
        # of the current frame.
        volume = np.sum(samples**2)/len(samples)
        # Format the volume output so it only
        # displays at most six numbers behind 0.
        volume = "{:6f}".format(volume)

        # Finally print the pitch and the volume.
        print(str(volume))
        print(" volume = {} / pitch = {} / confidence  ={}".format(str(volume),pitch,confidence))

if __name__ == "__main__": main(sys.argv)


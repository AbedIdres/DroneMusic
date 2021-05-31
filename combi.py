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

import datetime

# Some constants for setting the PyAudio and the
# Aubio.
BUFFER_SIZE             = 1024
CHANNELS                = 1
FORMAT                  = pyaudio.paFloat32
METHOD                  = "default"
SAMPLE_RATE             = 44100
HOP_SIZE                = BUFFER_SIZE//2
PERIOD_SIZE_IN_FRAME    = HOP_SIZE
SECONDS_IN_MINUT        = 60
LENGTH_OF_TIME          = 5
THESHHOLD               = 0.0
pitchList               = [35,45,55,65,75,85]
PITCH_COUNTER_THRESH    = 3

def main(args):

    # Initiating PyAudio object.
    pA = pyaudio.PyAudio()
    # Open the microphone stream.
    mic = pA.open(format=FORMAT, channels=CHANNELS,
        rate=SAMPLE_RATE, input=True,
        frames_per_buffer=PERIOD_SIZE_IN_FRAME)

    
    # setup pitch
    tolerance = 0.8
    win_s = 4096 # fft size
    hop_s = BUFFER_SIZE # hop size
    pitch_o = aubio.pitch("default", win_s, hop_s, SAMPLE_RATE)
    pitch_o.set_unit("midi")
    pitch_o.set_tolerance(tolerance)
    
    # Infinite loop!
    past = datetime.datetime.now()
    pitchlist=[]
    pitchcounter=[0,0,0,0,0,0]
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
        
        if(pitch >  THESHHOLD):
            pitchlist.append(pitch)
        # Compute the energy (volume)
        # of the current frame.
        volume = np.sum(samples**2)/len(samples)
        # Format the volume output so it only
        # displays at most six numbers behind 0.
        volume = "{:6f}".format(volume)
        
        
        present = datetime.datetime.now()
        difference = present - past
        
        # Finally print the pitch and the volume if time length threshold passed.
        if(divmod(difference.total_seconds(), SECONDS_IN_MINUT)[1] >= LENGTH_OF_TIME):
            #print(" volume = {} / pitch = {} / confidence  ={}".format(str(volume),pitch,confidence))
            
            print(pitchlist)
            
            #if no pitch was detected then do not print pitches
            if(len(pitchlist) != 0):
                for value in pitchlist:
                    
                    #round values to clossest pre defined pitch value
                    index = int(value)//10 -3
                    
                    #check if value is within range
                    if(index>=0 and index <=5):
                        pitchcounter[index] += 1
            print(pitchcounter)
            max_value = max(pitchcounter)
            max_value_index=pitchcounter.index(max_value)
            #if max value counter is heigher than threshold then print pitch
            if(max_value > PITCH_COUNTER_THRESH):
                print("pitch is " + str(pitchList[max_value_index]))
                
            #reset values of pitchlist and pitch counter
            pitchlist=[]
            pitchcounter=[0,0,0,0,0,0]
            past = present

if __name__ == "__main__": main(sys.argv)


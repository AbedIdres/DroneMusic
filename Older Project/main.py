import os
from pocketsphinx import LiveSpeech, get_model_path
from easytello import tello

model_path = get_model_path()
my_drone = tello.Tello()

speed = 30


#put your wake up code here
#this code will go once when you say wake up at the beggining
def funWakeUp():
    print("Hey Adham :) ")
    my_drone.takeoff()
    return

#put your right code here
def funcRight():
    # put your right code here
    print("sure, going right!")
    my_drone.right(speed)
    
    #my_drone.cw(50)
    return

#put your left code here
def funcLeft():
    # put your left code here
    print("sure, going left!")
    my_drone.forward(speed)
    #my_drone.cw(90)

    return

#put your up code here
def funcUp():
    # put your up code here
    print("sure, going up!")
    my_drone.up(speed)
    #my_drone.cw(90)
    return

#put your down code her
def funcDown():
    # put your down code here
    print("sure, going down!")
    my_drone.down(speed)
    #my_drone.cw(90)
    return





def funSleep():
    print("Bye Adham :( ")
    my_drone.land()
    return



# check if the drone is a wake
def checkWakeUp(word):
    if 'WAKE UP' == word:
        return True
    return False

# check if the drone is a wake
def checkSleep(word):
    if 'SLEEP' == word:
        return True
    return False


#parse the word
def parseVoice(word):

    if 'RIGHT' == word:
        funcRight()
    elif 'LEFT' == word:
        funcLeft()
    elif 'DOWN' == word:
        funcDown()
    elif 'UP' == word:
        funcUp()
    else:
        print("sorry did not recognize the word! :(")
    return 1


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    #this varibale must be the file path for the two file ( languagemodel (lm) , dictionry (dic))
    files_path = '/home/pi/Desktop/my_project/with_wake_up_1'

    speech = LiveSpeech(lm=files_path + '/commands.lm', dic=files_path + '/commands.dic',
                        hmm=os.path.join(model_path, 'en-us'),
                        buffer_size=1048, sampling_rate=16000)
    

    print("Commands: right , left , down , up")
    print("Just wake me up to start")
    

    

    while True:
        wakeup = False
        for phrase in speech:
            word = str(phrase)
            wakeup = checkWakeUp(word)
            if wakeup:
                funWakeUp()
                break

        for phrase in speech:
            
            word = str(phrase)
            print("You Said: " + word)

            if checkSleep(word):
                funSleep()
                break
            
            parseVoice(word)
            print("Listening...")

            



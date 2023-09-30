# Authors (chronological order)
# Jessica Vipin (2023)  - initial version
# Kevin Awoufack (2023) 
# Elias Pinter (2023)

import tkinter as tk
import picamera
import datetime
import os
from subprocess import call
from time import sleep
from os import system
from pynput.keyboard import Key, Listener
import time

class VRuler(tk.Canvas):
    '''Vertical Ruler'''

    def __init__(self, master, width, height, offset=0):
        super().__init__(master, width=width, height=height)
        self.offset = offset

        step = 10

        # start at `step` to skip line for `0`
        for y in range(step, height, step):
            if y % 50 == 0:
                # draw longer line with text
                self.create_line(0, y, 13, y, width=2)
                self.create_text(20, y, text=str(y), angle=90)
            else:
                self.create_line(2, y, 7, y)

        self.position = self.create_line(0, 0, 50, 0, fill='red', width=2)

    def set_mouse_position(self, y):
        y -= self.offset
        self.coords(self.position, 0, y, 50, y) 

class HRuler(tk.Canvas):
    '''Horizontal Ruler'''

    def __init__(self, master, width, height, offset=0):
        super().__init__(master, width=width, height=height)
        self.offset = offset

        step = 10
        # start at `step` to skip line for `0`
        for x in range(step, width, step):
            if x % 50 == 0:
                # draw longer line with text
                self.create_line(x, 0, x, 13, width=2)
                self.create_text(x, 20, text=str(x/50))
            else:
                self.create_line((x, 2), (x, 7))

        self.position = self.create_line(0, 0, 0, 50, fill='red', width=2)

    def set_mouse_position(self, x):
        x -= self.offset
        self.coords(self.position, x, 0, x, 50) 

def motion(event):
    x, y = event.x, event.y
    hr.set_mouse_position(x)
    vr.set_mouse_position(y)

def click(event):
    print(event.x, event.y)

x = 0
y = 0
w = 1
h = 1
stop = False
b=62

image = 1
video = 1
session = str(datetime.datetime.now()).replace(" ","")
session = session.replace("-","")
session = session.replace(":","")
session = session.replace(".","")
#os.mkdir("/home/pi/video")

#set up the camera to HD
#camera = picamera.PiCamera()
#camera.framerate = 30
#camera.iso = 800
#camera.sharpness = 100
#camera.brightness = 62
#camera.shutter_speed = int(1e6 / 10)
#camera.exposure_mode = 'off'



# initialize the camera and grab a reference to the raw camera capture
camera = picamera.PiCamera()
camera.resolution = (1920, 1080)
camera.framerate = 30
camera.sharpness = 100


def on():
    #allows for live preview of the microscope
    camera.start_preview(fullscreen=False, window=(200,200,640,480))
def off():
    global root
    #turn off preview
    camera.stop_preview()
    root.destroy()
              
def take_picture():
    global image
    global session
    filename = "/home/pi/video/" +str(session) +str(image) + ".jpg"
    image += 1
    camera.capture(filename)

def timelapse():
    global video
    global session
    tlminutes = 2*60 #set this to the number of minutes you wish to run your timelapse camera
    secondsinterval = 0.1 #number of seconds delay between each photo taken
    fps = 6 #frames per second timelapse video
    numphotos = int((tlminutes*60)/secondsinterval) #number of photos to take
    folderName = str(session) +str(image)
    print("number of photos to take = ", numphotos)

    dateraw= datetime.datetime.now()
    datetimeformat = dateraw.strftime("%Y-%m-%d_%H:%M")
    print("RPi started taking photos for your timelapse at: " + datetimeformat)
    
    #system('rm /home/pi/Timelapse/*.jpg') #delete all photos in the Pictures folder before timelapse start
    os.mkdir("/home/pi/Timelapse/" +str(session) +str(image))
    
    for i in range(numphotos):
        camera.capture('/home/pi/Timelapse/' + folderName + '/image{0:06d}.jpg'.format(i))
        sleep(secondsinterval)
    print("Done taking photos.")
    print("Please standby as your timelapse video is created.")
    
    system('ffmpeg -framerate {fpss} -pattern_type glob -i "/home/pi/Timelapse/{folder}/image*.jpg" -c:v libx264 /home/pi/Timelapse/{folder}/out.mp4'.format(fpss=fps, folder=folderName))
    #system('convert -delay 1 -loop 0 /home/pi/Timelapse/{folder}/image*.jpg animation.gif'.format(foler= str(session)+str(image)))
    #system('rm -rf /home/pi/Pictures/*.jpg')
    print('Timelapse video is complete. Video saved as /home/pi/Timelapse/'+folderName+'/out.mp4')
    video+=1

    
def start_video():
    global video
    global session
    filename = "/home/pi/video/"+str(session)+str(video) + ".h264"
    camera.start_recording(filename)
    
def stop_video():
    camera.stop_recording()
    global video
    global session
    sess_vid = str(session)+ str(video)
    filename = "/home/pi/video/"+ sess_vid + ".h264"
    system('ffmpeg -framerate {fr} -i /home/pi/video/{name}.h264 -c copy /home/pi/video/{name}.mp4'.format(name=sess_vid, fr=camera.framerate))
    video +=1
    
def up():
    global x,y,w,h
    if y > 0:
        y -= 0.25 / 10
        y = max(0, y)
    camera.zoom = (x, y, w, h)

def down():
    global x,y,w,h
    if y < 1:
        y += 0.25 / 10
        y = min(1-h,y)
    camera.zoom = (x, y, w, h)

def left():
    global x,y,w,h
    if x > 0:
        x -= 0.25 / 10
        x = max(0, x)
    camera.zoom = (x, y, w, h)

def right():
    global x,y,w,h
    if x < 1:
        x += 0.25 / 10
        x = min(1-w, x)
    camera.zoom = (x, y, w, h)

def increase_width():
    global x,y,w,h
    if w<1:
        w +=0.25/10
        w = min(1-x,w)
    camera.zoom = (x, y, w, h)
    
def decrease_width():
    global x,y,w,h
    if w>0:
        w -=0.25/10
        w = max(0,w)
    camera.zoom = (x, y, w, h)

def increase_height():
    global x,y,w,h
    if h<1:
        h +=0.25/10
        h = min(1-y,h)
    camera.zoom = (x, y, w, h)
    
def decrease_height():
    global x,y,w,h
    if h>0:
        h -=0.25/10
        h = max(0,h)
    camera.zoom = (x, y, w, h)
def brighter():
    global b
    b+=2
    camera.brightness = b
def darker():
    global b
    b-=2
    camera.brightness = b
    
    
#gui build out
window =tk.Tk()
window.title('Raspberry Pi Microscope Recorder')
window.geometry("640x480+1250+150")
btn_camera_on = tk.Button(
    text='Camera ON',
    width = 20,
    height = 1,
    bg='green',
    fg='white',
    command = on,
    )
btn_camera_off = tk.Button(
    text='Camera OFF',
    width = 20,
    height = 1,
    bg='red',
    fg='white',
    command = off,
    )
btn_take_picture = tk.Button(
    text='Take Picture',
    width = 20,
    height = 1,
    bg='black',
    fg='white',
    command = take_picture,
    )
btn_start_video = tk.Button(
    text='Start Recording',
    width = 20,
    height = 1,
    bg='green',
    fg='white',
    command = start_video,
    )

btn_stop_video = tk.Button(
    text='Stop Recording',
    width = 20,
    height = 1,
    bg='red',
    fg='white',
    command = stop_video,
    )
btn_up = tk.Button(
    text='Up',
    width = 10,
    height = 1,
    bg='teal',
    fg='white',
    command = up,
    )
btn_down = tk.Button(
    text='Down',
    width = 10,
    height = 1,
    bg='teal',
    fg='white',
    command = down,
    )
btn_left = tk.Button(
    text='<-- left',
    width = 10,
    height = 1,
    bg='teal',
    fg='white',
    command = left,
    )
btn_right = tk.Button(
    text='right -->',
    width = 10,
    height = 1,
    bg='teal',
    fg='white',
    command = right,
    )
btn_increase_height = tk.Button(
    text='Height',
    width = 10,
    height = 1,
    bg='DodgerBlue',
    fg='white',
    command = increase_height,
    )
btn_decrease_height = tk.Button(
    text='Height',
    width = 10,
    height = 1,
    bg='DodgerBlue',
    fg='white',
    command = decrease_height,
    )
btn_increase_width = tk.Button(
    text='Width',
    width = 10,
    height = 1,
    bg='RoyalBlue',
    fg='white',
    command = increase_width,
    )
btn_decrease_width = tk.Button(
    text='Width',
    width = 10,
    height = 1,
    bg='RoyalBlue',
    fg='white',
    command = decrease_width,
    )
btn_brighter = tk.Button(
    text='Brighter',
    width = 20,
    height = 1,
    bg='Gold',
    fg='black',
    command = brighter,
    )
btn_darker = tk.Button(
    text='Darker',
    width = 20,
    height = 1,
    bg='Chocolate',
    fg='white',
    command = darker,
    )
btn_timelapse = tk.Button(
    text='timelapse',
    width = 20,
    height = 1,
    bg='Black',
    fg='yellow',
    command = timelapse,
    )


btn_camera_on.place(x=125,y=0)
btn_camera_off.place(x=325,y=0)
btn_take_picture.place(x=225,y=30)
btn_start_video.place(x=125,y=60)
btn_stop_video.place(x=325,y=60)
btn_up.place(x=275,y=100)
btn_down.place(x=275,y=130)
btn_left.place(x=175,y=115)
btn_right.place(x=375,y=115)
btn_brighter.place(x=125,y=175)
btn_darker.place(x=325,y=175)
btn_timelapse.place(x=225, y=290)
tk.Label(window,text="Zoom OUT :",font=("Helvetica",20),fg='Grey').place(x=155,y=215)
btn_increase_height.place(x=325,y=215)
btn_increase_width.place(x=425,y=215)
tk.Label(window,text="Zoom IN :",font=("Helvetica",20),fg='Grey').place(x=175,y=250)
btn_decrease_height.place(x=325,y=250)
btn_decrease_width.place(x=425,y=250)


root = tk.Tk()
root['bg'] = 'black'
root.geometry("700x555+130+110")

vr = VRuler(root, 25, 1000)#, offset=25)
vr.place(x=0, y=28)

hr = HRuler(root, 2000, 25)#, offset=25)
hr.place(x=28, y=0)

c = tk.Canvas(root, width=2000, height=2000)
c.place(x=28, y=28)

#root.bind('<Motion>', motion) # it needs offset=28 if there is no Canvas
#root.bind('<Button-1>', click)
c.bind('<Motion>', motion)
c.bind('<Button-1>', click)

root.mainloop()
window.mainloop()

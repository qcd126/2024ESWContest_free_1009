import RPi.GPIO as GPIO
import time
import cv2
import numpy as np
import os
from Image_tcp_clientsv4 import ClientSocket
import customtkinter
from PIL import Image, ImageTk
import threading



pin = 16
in1Pin = 10
in2Pin = 9
in3Pin = 11
isDetected = False

webcam = cv2.VideoCapture(0)

webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 880)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1000)
webcam.set(cv2.CAP_PROP_EXPOSURE, 150)
webcam.set(cv2.CAP_PROP_BRIGHTNESS, 100)
evt = threading.Event()

evt.clear()

class App(customtkinter.CTk):
    temp = 0
    def __init__(self):
        super().__init__()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.temp=screen_height
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        self.title("알약 검출")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
       
        self.frame_up = customtkinter.CTkFrame(master=self, fg_color="", corner_radius=0)
        self.frame_up.grid(row=0, rowspan=1, column=0, columnspan=1, padx=0, pady=0, sticky="nsew")
        self.frame_down = customtkinter.CTkFrame(master=self, fg_color="", corner_radius=0)
        self.frame_down.grid(row=1, rowspan=1, column=0, columnspan=1, padx=0, pady=0, sticky="nsew")
        
        self.button = customtkinter.CTkButton(master=self, text="Start", command=self.button_event)
        self.button.grid(row=1, rowspan=1, column=0, columnspan=1, padx=0, pady=0, sticky="")
        #self.button_event()
        

    def button_event(self):
        evt.wait()
        img_size = self.temp/3
        before_path="Original.jpg"
        self.before_img = customtkinter.CTkImage(light_image=Image.open(f"{before_path}"), dark_image=Imagew.open(f"{before_path}"), size=(img_size, img_size))
        self.before_img = customtkinter.CTkLabel(master=self, image=self.before_img, text="")
        self.before_img.grid(padx=0, pady=0, sticky="nsw", row=0, column=0)
        
        after_path="label_result.jpg"
        self.after_img = customtkinter.CTkImage(light_image=Image.open(f"{after_path}"), dark_image=Image.open(f"{after_path}"), size=(img_size, img_size))
        self.after_img = customtkinter.CTkLabel(master=self, image=self.after_img, text="")
        self.after_img.grid(padx=0, pady=0, sticky="ns", row=0, column=0)
        
        mark_path="last_result.jpg"
        self.mark_img = customtkinter.CTkImage(light_image=Image.open(f"{mark_path}"), dark_image=Image.open(f"{mark_path}"), size=(img_size, img_size))
        self.mark_img = customtkinter.CTkLabel(master=self, image=self.mark_img, text="")
        self.mark_img.grid(padx=0, pady=0, sticky="nse", row=0, column=0)
        self.update()
        evt.clear()
        self.button_event()
    

def setup():
    global p

    
    
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
   
    GPIO.setup(in1Pin, GPIO.OUT)
    GPIO.setup(in2Pin, GPIO.OUT)
    GPIO.setup(in3Pin, GPIO.OUT)
    GPIO.setup(pin, GPIO.OUT)
    p = GPIO.PWM(pin, 50)
    p.start(0)
    #p.start(0)
    

def loop():
    global p
    try:
        while True:
            
            if not webcam.isOpened():
                print("Could not open webcam")
                exit()
            
            status, frame = webcam.read()
            
            frame = frame[:, 100:700]
            frame = frame[:, 30:570]

            bgrLower = np.array([220, 220, 220])
            bgrUpper = np.array([255, 255, 255])
            forward()
            
            if status:
                detectFlage = 0
                img_mask = cv2.inRange(frame, bgrLower, bgrUpper)
                if img_mask.any() > 0 :
                    #print("Pill")
                    #GPIO.output(in3Pin,True)
                    #cv2.waitKey(1000)
                    
                    #GPIO.output(in3Pin,False)
                    
                    
                    
                    
                    #cv2.waitKey(1000)
                    status, frame = webcam.read()
                    status, frame = webcam.read()

               

                    
                    for i in range(0, 100):
                        if i == 1:
                            GPIO.output(in3Pin,False)
                        status, frame = webcam.read()
                    

                    frame = frame[:, 100:700]
                    frame = frame[:, 30:570]
                    
                    cv2.imwrite("/home/white/Desktop/py/Original.jpg", frame)
                    
                    TCP_IP = '220.69.240.148'
                    TCP_PORT = 21000
                    client = ClientSocket(TCP_IP, TCP_PORT)
                    isDetected = client.run()
                    print(isDetected)
                    evt.set()
                    
                    GPIO.output(in3Pin,True)
                    cv2.waitKey(1500)
                    
                    if(isDetected == True):                    
                        p.ChangeDutyCycle(10)
                        time.sleep(0.61)
                        p.ChangeDutyCycle(0)
                    
                    for i in range(0, 30):
                        status, frame = webcam.read()
                    #status, frame = webcam.read()
                    frame = frame[:, 100:700]
                    frame = frame[:, 30:570]
                    cv2.waitKey(3000)
                    
                    GPIO.output(in3Pin,False)
                    a = input()
                    ###########################################################
                    ####################43라인변경##############################
                    ###########################################################
                    #while detectFlage <= 1000:
                    #    detectFlage += 1
                    #    print(detectFlage)
                    #cv2.waitKey(1)
                    
                    #img_mask = cv2.inRange(frame, bgrLower, bgrUpper)
                    
                    
                else:
                    GPIO.output(in3Pin,True)
                    #evt.set()
                    #print("No pill")
                    
                    

                cv2.imshow("Webcam", frame)
                    
                    
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                GPIO.cleanup()
                break
            
        webcam.release()
        cv2.destroyAllWindows()
        GPIO.output(in3Pin,False)

    except KeyboardInterrupt:
        print("HEllo")
        GPIO.output(in3Pin,False)
        #GPIO.cleanup()
    finally:   # 정리 작업을 위해 finally 블록 사용
        GPIO.output(in3Pin,False)
        GPIO.output(in2Pin,False)
        GPIO.output(in1Pin,False)
        GPIO.cleanup()   # cleanup() 함수가 정의되어 있지 않으므로 필요에 따라 구현해야 함

def forward():
    
    # 모터 작동 로직 구현 (핀 상태 설정 등)
    GPIO.output(in1Pin, GPIO.HIGH)
    GPIO.output(in2Pin, GPIO.LOW)
def backward():
    # 모터 정지 로직 구현 (핀 상태 설정 등)
    GPIO.output(in1Pin,False)
    GPIO.output(in2Pin,False)

def run():
    app =App()
    app.mainloop()

if __name__ == '__main__':
    setup()
    
    try:
        UI = threading.Thread(target=run)
        UI.start()
        loop()
    
    except KeyboardInterrupt:
        
        GPIO.output(in3Pin,False)
        pass
    
    finally:   # 정리 작업을 위해 finally 블록 사용
         GPIO.cleanup()   # cleanup() 함수가 정의되어 있지 않으므로 필요에 따라 구현해야 함




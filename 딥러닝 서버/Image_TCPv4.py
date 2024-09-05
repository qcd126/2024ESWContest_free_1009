import cv2
import numpy
import socket
import threading
import base64
import os
import torch
import matplotlib.pyplot as plt
from torchvision.transforms import Compose, Grayscale, ToTensor
from model import UNet16
from PIL import Image

class ServerSocket:

    def __init__(self, ip, port, model):
        self.model = model
        self.TCP_IP = ip
        self.TCP_PORT = port
        self.socketOpen()
        while(1):
            self.socketListen()
            self.receiveImages()
        #self.receiveThread = threading.Thread(target=self.receiveImages)
        #self.receiveThread.start()
        #self.receiveImages()

    def socketClose(self):
        self.conn.close()
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is close')
       
    def socketOpen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.TCP_IP, self.TCP_PORT))
        
    def socketListen(self):
        self.sock.listen(1)
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is open')
        self.conn, self.addr = self.sock.accept()
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is connected with client')
	
	
    def receiveImages(self):
      try:
        length = self.recvall(self.conn, 64)
        length1 = length.decode('utf-8')
        print(int(length1))
        stringData = self.recvall(self.conn, int(length1))
        data = numpy.frombuffer(base64.b64decode(stringData), numpy.uint8)
        decimg = cv2.imdecode(data, 1)
        print("good")
        cv2.imwrite("input/Test.jpg", decimg)
        os.system("sudo python3 background_remove.py --input_path input --output_text_path output --yolo_label 1 --png_path output")
        print("Good")
        img =cv2.imread('output/Test_.png', cv2.IMREAD_UNCHANGED)
        cv2.imwrite('output/Test.jpg', img)
        img = cv2.imread('output/Test.jpg')

        encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
        result, imgencode = cv2.imencode('.jpg', img, encode_param)
        data = numpy.array(imgencode)
        stringData = base64.b64encode(data)
        length = str(len(stringData))
  
        self.conn.sendall(length.encode('utf-8').ljust(64))
        self.conn.send(stringData)
        #self.conn.send("I am a server".encode("utf-8"))
          
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        transform = Compose([ToTensor()])
        img = transform(img)
        img = img.unsqueeze(0)
        y = self.model(img)
        residual = torch.abs(img[0][0]-y[0][0])
        result = residual.detach().cpu().numpy()>0.02
        
        plt.plot([0, 10],[0, 10])
        plt.xlabel("X Label")
        plt.ylabel("Y Label")
        
        ax = plt.gca()
        ax.axes.xaxis.set_visible(False)
        ax.axes.yaxis.set_visible(False)
        plt.grid(True)
        plt.imshow(residual.detach().cpu().numpy()>0.0225)
        plt.savefig('output/Yeah.jpg', bbox_inches='tight')
        
        img = cv2.imread('output/Yeah.jpg')

        encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
        result, imgencode = cv2.imencode('.jpg', img, encode_param)
        data = numpy.array(imgencode)
        stringData = base64.b64encode(data)
        length = str(len(stringData))
  
        self.conn.sendall(length.encode('utf-8').ljust(64))
        self.conn.send(stringData)
      
        
        print((residual.detach().cpu().numpy()>0.0225).sum())
        if (residual.detach().cpu().numpy()>0.0225).sum()  > 100:
            self.conn.send("Detected".encode("utf-8"))
            print("Detected")
        else:
            self.conn.send("Pass".encode("utf-8")) 
            print("Pass")
      except:
        pass
          
        
        self.socketClose()
        cv2.destroyAllWindows()

    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf

def main():
    model = UNet16()
    model.load_state_dict(torch.load('./UNet16_Final_0.025.pt'))
    print("Hello World")
    model.eval()
    server = ServerSocket('0.0.0.0', 21000, model)

if __name__ == "__main__":
    main()

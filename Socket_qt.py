import sys
import threading
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QWaitCondition
from PyQt5.QtCore import QMutex
from PyQt5.QtCore import pyqtSignal


#socket lib
import socket
import time
import select

form_class = uic.loadUiType("Socket_qt.ui")[0]

MAX_CONNECTION = 1
Exit_Thread = False
            
class ReceiveThread(QThread):
    change_text = pyqtSignal('QString')
    Connect_Btn = pyqtSignal(bool)
    Disconnect_Btn = pyqtSignal(bool)
    def __init__(self, sock, role):
        QThread.__init__(self)
        self.cond = QWaitCondition()
        self.mutex = QMutex()
        self.conn = sock
        self.Myrole = role
        
    def __del__(self):
        self.wait()

    def run(self):
        cnt = 0;
        global Exit_Thread
        print("Receive QThread running!!")
        while not Exit_Thread:
            self.mutex.lock()
            do_read = False
            try:
                r, _, _ = select.select([self.conn], [], []) #check socket close condition
                do_read = bool(r)
            except socket.error:
                pass
                
            if do_read:
                try:
                    data = self.conn.recv(1024)
                    if not data:
                        print("not data")
                        break
                    data = str(data)
                    if(self.Myrole == "SERVER"):
                        data = "CLIENT : " + data
                    else:
                        data = "SERVER : " + data
                    #self.textBrowser.append(data) 
                    self.change_text.emit(data)
                    
                except:
                    pass
            self.mutex.unlock()
        print("Receive QThread Finish!!")
        self.Connect_Btn.emit(True)
        self.Disconnect_Btn.emit(False)
            
class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setupUi(self)
        self.pushButton_Connect.clicked.connect(self.Connect_btn_clicked)
        self.pushButton_Disconnect.clicked.connect(self.Disconnect_btn_clicked)
        self.pushButton_Send.clicked.connect(self.Send_btn_clicked)
        self.radioButton_Client.clicked.connect(self.Radio_btn_clicked)
        self.radioButton_Server.clicked.connect(self.Radio_btn_clicked)
        
        self.scroll_bar = self.textBrowser.verticalScrollBar()

        #Default Server
        self.radioButton_Server.setChecked(True)
        self.Myrole = "SERVER"

        #default address & Port
        self.lineEdit_Ipaddr.insert("192.168.43.254")
        self.lineEdit_Portnum.insert("50000")

        #BOOL Connected status
        self.Isconnected = False

        #Button Init status
        self.pushButton_Disconnect.setEnabled(False)

        #Socket server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = -1

        #Thread
        self.recv_th = -1
        self.send_th = -1

        
    def Connected_Loop(self):
        while self.Isconnected :
            print("loop")
            #TODO: Mss send / rcv


    def isNumber(self,s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def Connect_btn_clicked(self):
        print("Connect")
        IP_text = self.lineEdit_Ipaddr.text()
        IP_List=IP_text.split('.')
        int_cnt = 0
        global gb_conn
        for i in range(0,4):
            if self.isNumber(IP_List[i]):
                print("%s is number" % IP_List[i])
                int_cnt=int_cnt+1
            else:
                print("%s is not number" % IP_List[i])

        Port_text = self.lineEdit_Portnum.text()
        Port_num = -1
        if self.isNumber(Port_text):
            Port_num=int(Port_text)
            int_cnt = int_cnt+1
        
        if(int_cnt == 5):
            self.Isconnected = True
            print("connected!!")
            self.pushButton_Connect.setEnabled(False)
            self.pushButton_Disconnect.setEnabled(True)
            if(self.Myrole == "SERVER"):
                print("Server!!! / Port num : %s", Port_num)
                self.sock.bind((IP_text, Port_num))
                self.sock.listen(MAX_CONNECTION)
                print("listen!!!")
                self.conn, addr =self.sock.accept()
                print("Connected by ", addr)
                print(self.conn)
                #self.recv_th = threading.Thread(target = self.gettingMsg, args=(self.conn,))
                #self.recv_th.daemon = False
                #self.recv_th.start()
                
                self.recv_th = ReceiveThread(self.conn,self.Myrole)
                self.recv_th.start()
                self.recv_th.change_text.connect(self.textBrowser.append)
                self.recv_th.Connect_Btn.connect(self.pushButton_Connect.setEnabled)
                self.recv_th.Disconnect_Btn.connect(self.pushButton_Disconnect.setEnabled)
                
                #self.send_th = threading.Thread(target = self.test, args=())
                #self.send_th.start()
                
                #for test
                #self.send_th = Thread()
                #self.send_th.start()
                #self.send_th.change_text.connect(self.textBrowser.append)
                
                print("Server : Thread is running")
               
                
            else: #client
                print("Client!! / Port num : %s", Port_num)
                self.sock.connect((IP_text, Port_num))
                print(self.sock)
                #self.recv_th = threading.Thread(target = self.gettingMsg, args=(self.sock,)) 
                #self.recv_th.daemon = False
                #self.recv_th.start()
                
                self.recv_th = ReceiveThread(self.sock, self.Myrole)
                self.recv_th.start()
                self.recv_th.change_text.connect(self.textBrowser.append)
                self.recv_th.Connect_Btn.connect(self.pushButton_Connect.setEnabled)
                self.recv_th.Disconnect_Btn.connect(self.pushButton_Disconnect.setEnabled)
                
                #self.send_th = threading.Thread(target = self.sendingMsg, args=(self.sock,))
                #self.send_th.daemon = True
                #self.send_th.start()
                print("Client : Thread is running")
           
                
    def test(self):
        cnt = 0;
        while True:
            #print("Test Thread running %s" % cnt)
            self.textBrowser.append("Thread!!!! %s" % cnt)
            self.scroll_bar.setSliderPosition(self.scroll_bar.maximum())
            #self.scroll_bar.sliderPressed()
            cnt = cnt+1
            time.sleep(0.08)
        
                    
    def sendingMsg(self,conn):
        while self.Isconnected:    
            try:
                data = raw_input() #need to check socket close condition
                if not data:
                    break;
                data = data.encode("utf-8")
                conn.send(data)
            except:
                pass
        conn.close()
        print("Send Thread is finish") 
        
    def gettingMsg(self,conn):
        print(conn)
        while self.Isconnected:
            do_read = False
            try:
                r, _, _ = select.select([conn], [], []) #check socket close condition
                do_read = bool(r)
            except socket.error:
                pass
            if do_read:
                try:
                    data = conn.recv(1024)
                    if not data:
                        break
                    data = str(data)
                    if(self.Myrole == "SERVER"):
                        data = "CLIENT : " + data
                    else:
                        data = "SERVER : " + data
                    self.textBrowser.append(data)
                    self.scroll_bar.setSliderPosition(self.scroll_bar.maximum())
                    # self.scroll_bar.sliderPressed()
                    #print(data)
                    
                except:
                    pass
                
        conn.close()
        print("Receive Thread is finish")
        self.Disconnect_btn_clicked()
           

    def Disconnect_btn_clicked(self):
        print("Disconnect")
        global Exit_Thread
        self.Isconnected = False
        Exit_Thread = True;
        self.pushButton_Connect.setEnabled(True)
        self.pushButton_Disconnect.setEnabled(False)
        self.sock.close()
        if (self.Myrole == "SERVER"):
            self.conn.close()
        #self.send_th.quit()
        #self.recv_th.quit()

    def Send_btn_clicked(self):
        text = self.lineEdit_Message.text()
        self.textBrowser.append(text)
        text = text.encode("utf-8")
        if(self.Myrole == "SERVER"):
            self.conn.send(text)
        else:
            self.sock.send(text)
        self.lineEdit_Message.clear()
        print("Send")
        

    def Radio_btn_clicked(self):
        msg=""
        if self.radioButton_Client.isChecked():
            msg = "Client"
            self.Myrole = "CLIENT"
        elif self.radioButton_Server.isChecked():
            msg = "Server"
            self.Myrole = "SERVER"
        else:
            msg = "???"

        print(msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()

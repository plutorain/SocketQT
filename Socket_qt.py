import sys
import threading
from PyQt5.QtWidgets import *
from PyQt5 import uic

#socket lib
import socket
import time
import select

form_class = uic.loadUiType("Socket_qt.ui")[0]

MAX_CONNECTION = 1

        
class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setupUi(self)
        self.pushButton_Connect.clicked.connect(self.Connect_btn_clicked)
        self.pushButton_Send.clicked.connect(self.Send_btn_clicked)
        self.pushButton_Disconnect.clicked.connect(self.Disconnect_btn_clicked)
        self.radioButton_Client.clicked.connect(self.Radio_btn_clicked)
        self.radioButton_Server.clicked.connect(self.Radio_btn_clicked)

        #Default Server
        self.radioButton_Server.setChecked(True)
        self.Myrole = "SERVER"

        #default address & Port
        self.lineEdit_Ipaddr.insert("192.168.0.10")
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
                
                #self.send_th = threading.Thread(target = self.sendingMsg, args=(self.conn,))
                self.recv_th = threading.Thread(target = self.gettingMsg, args=(self.conn,))
                #self.send_th.daemon = True
                #self.recv_th.daemon = False
                #self.send_th.start()
                self.recv_th.start()
                print("Server : Thread is running")
               
                
            else: #client
                print("Client!! / Port num : %s", Port_num)
                self.sock.connect((IP_text, Port_num))
                #self.send_th = threading.Thread(target = self.sendingMsg, args=(self.sock,))
                self.recv_th = threading.Thread(target = self.gettingMsg, args=(self.sock,))
                #self.send_th.daemon = True
                #self.recv_th.daemon = False
                #self.send_th.start()
                self.recv_th.start()       
                print("Client : Thread is running")
           
                
                
                    
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
                    #print(data)
                    
                except:
                    pass
                
        conn.close()
        print("Receive Thread is finish")
        self.Disconnect_btn_clicked()
           

    def Disconnect_btn_clicked(self):
        print("Disconnect")
        self.Isconnected = False
        self.sock.close()
        if (self.Myrole == "SERVER"):
            self.conn.close()
        self.pushButton_Connect.setEnabled(True)
        self.pushButton_Disconnect.setEnabled(False)
        
        #self.send_th.quit()
        #self.recv_th.quit()

    def Send_btn_clicked(self):
        text = self.lineEdit_Message.text()
        text = text+'\r'
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

from socket import *
import threading
import sys
import pickle

connections = []
exit = ['q','quit','exit','leave']
cycle = True
udpSocket = socket(AF_INET, SOCK_DGRAM)

def tcpConection(conditionObj):
    global cycle
    tcpPort = 8888
    if len(sys.argv) > 1:
        serverName = sys.argv[1]
    else:
        print("Missing Server IP")
        serverName = '10.0.1.10' 
    tcpSocket = socket(AF_INET,SOCK_STREAM)
    tcpSocket.bind(('',tcpPort))

    tcpSocket.connect((serverName,tcpPort))
    message = "ott"

    try:
        tcpSocket.send(message.encode())
    except Exception as e:
        print(e)
        cycle = False
        closeReciever()
    
    r = threading.Thread(target=tcpReciver, args=(conditionObj,tcpSocket,))
    r.start()
    s = threading.Thread(target=tcpEmiter, args=(tcpSocket,))
    s.start()
    
    s.join()
    r.join()
    tcpSocket.close()

def tcpEmiter(tcpSocket):
    for line in sys.stdin:
        if line.rstrip().lower() in exit:
            global cycle
            cycle = False
            closeReciever()
            message = "Q"
            try:
                tcpSocket.send(message.encode())
            except Exception as e:
                print(e)
            break

def tcpReciver(conditionObj,tcpSocket):
    global cycle
    global connections
    while cycle:
        try:
            content = tcpSocket.recv(1024)
            try:
                content = content.decode()
            except:
                pass
        except Exception as e:
            print(e)
            cycle = False
            closeReciever()
            content = "1"
        if type(content) is bytes:
            with conditionObj:
                connections = pickle.loads(content)
                conditionObj.notify()
        else:
            if content == "-1":
                print("IP not found in trusted IP's list.")
                cycle = False
                closeReciever()
            elif content == "Q":
                cycle = False
                closeReciever()
                
def get_ip():
    s = socket(AF_INET,SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception as e:
        print(e)
        ip = "10.0.0.10"
        global cycle
        cycle = False
    finally:
        s.close()
    return ip

end = True
                
def udpEmiter(conditionObj):
    udpPort = 9999
    global udpSocket
    udpSocket.bind(('0.0.0.0',udpPort))
    global connections
    global cycle
    global end
    while cycle:
        try:
            msg, addr = udpSocket.recvfrom(2048)
        except Exception as e:
            print(e)
            cycle = False
        finally:
            with conditionObj:
                if connections == []:
                    conditionObj.wait()
                for node in connections:
                    try:
                        udpSocket.sendto(msg,(node,udpPort))
                    except Exception as e:
                        print(e)
                        cycle = False
    end = False
                
def closeReciever():
    global udpSocket
    udpPort = 9999
    
    closeSocket = socket(AF_INET, SOCK_DGRAM)
    global end
    msg = ""
    while end:
        try:
            closeSocket.sendto(msg.encode(),(get_ip(),udpPort))
        except Exception as e:
            print(e)
            end = False
    closeSocket.close()
    udpSocket.close()

cycle = True
  
if __name__ == "__main__":

    conditionObj = threading.Condition()

    # TCP connextion with server
    t = threading.Thread(target=tcpConection, args=(conditionObj,))
    t.start()

    # UDP connextions
    udp = threading.Thread(target=udpEmiter, args=(conditionObj,))
    udp.start()

    udp.join()
    t.join()

    # both threads completely executed
    print("Closing successfully")

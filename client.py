from pickle import PUT
from socket import*
import threading
import sys

cycle = True
exit = ['q','quit','exit','leave']
udpSocket = socket(AF_INET, SOCK_DGRAM)

def tcpConection():
    tcpPort = 8888
    if len(sys.argv) > 1:
        serverName = sys.argv[1]
    else:
        print("Missing Server IP")
        serverName = '10.0.1.10' 
    tcpSocket = socket(AF_INET,SOCK_STREAM)
    tcpSocket.bind(('',tcpPort))
    tcpSocket.connect((serverName,tcpPort))
    message = "Client"
    tcpSocket.send(message.encode())

    r = threading.Thread(target=tcpReciver, args=(tcpSocket,))
    r.start()
    s = threading.Thread(target=tcpEmiter, args=(tcpSocket,))
    s.start()
    
    s.join()
    r.join()

    tcpSocket.close()

def tcpEmiter(tcpSocket):
    global cycle
    global udpSocket
    while cycle:
        content = input("Press 'Q' to finish connection\n")
        if content.lower() in exit:
            cycle = False
            message = "Q"
            closeReciever()
            tcpSocket.send(message.encode())
        elif content == "Rick Roll":
            print("Never gonna give you up!\n")

def tcpReciver(tcpSocket):
    global cycle
    while cycle:
        try:
            content = tcpSocket.recv(1024).decode()
        except Exception as e:
            print(e)
            cycle = False
            closeReciever()
            content = "1"
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

def udpReciever():
    global udpSocket
    udpPort = 9999
    udpSocket.bind(('0.0.0.0',udpPort))

    global cycle
    global end
    while cycle:
        msg, addr = udpSocket.recvfrom(2048)
        print(msg.decode(),end="")
    end = False

def closeReciever():
    global udpSocket
    udpPort = 9999
    
    closeSocket = socket(AF_INET, SOCK_DGRAM)
    global end
    msg = ""
    while end:
        closeSocket.sendto(msg.encode(),(get_ip(),udpPort))
    closeSocket.close()
    udpSocket.close()
  
if __name__ == "__main__":
    # UDP connextions
    udp = threading.Thread(target=udpReciever)
    udp.start()

    # TCP connextion with server
    t = threading.Thread(target=tcpConection)
    t.start()

    udp.join()
    t.join()

    # both threads completely executed
    print("Closing successfully")

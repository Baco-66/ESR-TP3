from socket import *
import re
import pickle
from collections import defaultdict
import threading
import sys
import time
import base64
from copy import deepcopy

# driver code
actives = []
activesCl = []
graph = {}
new = {}
routes = []
neighbors = []
cycle = True
BUFF_SIZE = 65536

# Add a vertex to the dictionary
def add_vertex(v,g):
  if v not in g:
    g[v] = []

# Add an edge between vertex v1 and v2
def add_edge(v1, v2, g):
  if v1 in g and v2 in g:
    g[v1].append(v2)
    g[v2].append(v1)

#Função que lê ficheiro de texto com a topologia
def read():
    regex = re.compile(r'(([0-9]{1,3}\.){3}[0-9]{1,3})')
    with open("ips.txt") as f:
        for line in f:
            result = regex.split(line)
            add_vertex(result[1],graph)
    with open("arcos.txt") as l:
        for line in l:
            result = regex.split(line)
            add_edge(result[1], result[4], graph)

  
def new_graph():
    global actives
    global graph
    new = deepcopy(graph)
    for vertex in new:
        if vertex not in actives:
            new = remove_vertex(vertex, new)
    return new

def remove_vertex(v, n):
    r = dict(n)
    if v in r:
        if len(r[v]) > 1:
            master = distance_to(v,localIP,r)
            for n in r[v]:
                r[n].remove(v)
                if n != master:
                    add_edge(n,master,r)
            del r[v]
        else:
            r[r[v][0]].remove(v)
            del r[v]
    return r

  
def distance_to(v1, v2, g):
    dist = None
    result = None
    for n in g[v1]:
        newroute = BFS_SP(g, v2, n)
        if newroute:
            newdist = len(newroute)
            if dist is None:
                dist = newdist
                result = n
            elif dist > newdist:
                dist = newdist
                result = n  
    return result

def newRouts(localIP):
    global new
    global routes
    new = new_graph()
    newroutes = []      
    for client in activesCl:
            newroutes.append(BFS_SP(new, localIP, client))
    if routes != newroutes:
        routes = newroutes
        return True
    return False

def BFS_SP(grapho, start, goal):
    explored = []
    queue = [[start]]
    if start == goal:
        return 
    while queue:
        path = queue.pop(0)
        node = path[-1]
        if node not in explored:
            neighbours = grapho[node]
            for neighbour in neighbours:
                new_path = list(path)
                new_path.append(neighbour)
                queue.append(new_path)
                if neighbour == goal:
                    return new_path
            explored.append(node)
    return 

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

def tcpCreator(conditionObj,localIP):
    threads = []
    tcpPort = 8888
    tcpSocket = socket(AF_INET,SOCK_STREAM)
    tcpSocket.bind((localIP,tcpPort))
    tcpSocket.listen(1)
    global cycle
    while cycle:
        connectionSocket, addr = tcpSocket.accept()
        t = threading.Thread(target=tcpConection, args=(connectionSocket,addr,conditionObj,localIP,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
    
    tcpSocket.close()

def tcpConection(connectionSocket,addr,conditionObj,localIP):
    global actives
    global activesCl
    global routes
    cycle = True
    if addr[0] in graph.keys():
        conditionObj.acquire()
        actives.append(addr[0])
        try:
            content = connectionSocket.recv(1024).decode()
        except Exception as e:
            print(e)
            cycle = False
            conditionObj.release()
        if content == "ott":
            if newRouts(localIP):
                conditionObj.notify_all()
            conditionObj.release()
            event = threading.Event()
            r = threading.Thread(target=tcpReciver, args=(conditionObj,connectionSocket,event,))
            r.start()
            neighbors = []
            while cycle and not event.is_set():
                newneighbors = []
                for route in routes:
                    if route:
                        for i in range(len(route)):
                            if route[i] == addr[0] and route[i+1] not in newneighbors:
                                newneighbors.append(route[i+1])
                if neighbors != newneighbors:
                    neighbors = newneighbors
                    data = pickle.dumps(neighbors)
                    try:
                        connectionSocket.send(data)
                    except Exception as e:
                        print(e)
                        cycle = False
                with conditionObj: 
                    conditionObj.wait()
            r.join()
        elif content == "Client":
            activesCl.append(addr[0])
            if newRouts(localIP):
                conditionObj.notify_all()
            conditionObj.release()
            event = threading.Event()
            r = threading.Thread(target=tcpReciver, args=(conditionObj,connectionSocket,event,))
            r.start()
            reciever = ""
            while cycle and not event.is_set():
                newreciever = ""
                for route in routes:
                    if route:
                        if route[-1] == addr[0]:
                            newreciever = route[-2]
                            break
                if reciever != newreciever:
                    reciever = newreciever
                try:
                    connectionSocket.send(reciever.encode())
                except Exception as e:
                    print(e)
                    cycle = False
                with conditionObj: 
                    conditionObj.wait()
            activesCl.remove(addr[0])
            r.join()
        else:
            pass
        with conditionObj:  
            actives.remove(addr[0])
            if newRouts(localIP):
                conditionObj.notify_all()
    else:
        message = "-1"
        try:
            connectionSocket.send(message.encode())
        except Exception as e:
            print(e)
    connectionSocket.close()

def tcpReciver(conditionObj,connectionSocket,event):
    cycle = True
    while cycle:
        try:
            content = connectionSocket.recv(1024).decode()
        except Exception as e:
            print(e)
            content = "Q" 
        if content == "Q":
            try:
                connectionSocket.send(content.encode())
            except Exception as e:
                print(e)
            with conditionObj:
                cycle = False
                event.set()
                conditionObj.notify_all()

def udpEmiter(conditionObj):
    global neighbors
    global routes
    udp = threading.Thread(target=udpStream)
    udp.start()

    while cycle:
        newneighbors = []
        for route in routes:
            if route:
                if route[1] not in newneighbors:
                    newneighbors.append(route[1])
        if neighbors != newneighbors:
            neighbors = newneighbors
        with conditionObj:
            conditionObj.wait()
    udp.join()
        
def udpStream():
    global neighbors
    udpPort = 9999
    udpSocket = socket(AF_INET, SOCK_DGRAM)
    global cycle
    with open('Shrek.txt', 'r') as fo:
        while cycle:
            for line in fo:
                for node in neighbors:
                    udpSocket.sendto(line.encode(),(node,udpPort))
                time.sleep(0.125)
            fo.seek(0)

if __name__ == "__main__":
    read()
    localIP = get_ip()
    actives.append(localIP)

    conditionObj = threading.Condition()

    tcp = threading.Thread(target=tcpCreator, args=(conditionObj,localIP,))
    tcp.start()

    # UDP stuff
    udp = threading.Thread(target=udpEmiter, args=(conditionObj,))
    udp.start()

    tcp.join()
    udp.join()

    # both threads completely executed
    print("Closing successfully")
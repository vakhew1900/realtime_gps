from gpsdclient import GPSDClient
from datetime import datetime

import socket



def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def getCoordinate():

    location = ""
    # or as python dicts (optionally convert time information to `datetime` objects)
    with GPSDClient() as client:
        # print(client.dict_stream)
        
        for result in client.dict_stream(convert_datetime=True, filter=["TPV"]):
            lat = result.get("lat", "n/a")
            lon = result.get("lon", "n/a")
            if (isfloat(lat) and isfloat(lon)):
                break

    
    location = "{0},{1},157.0\n".format(lat, lon)

    return location


HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 22500  # The port used by the server


if __name__ == '__main__':
     
     actual_time = datetime.now()
     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     sock.connect((HOST, PORT))

     while(True):
        print("circle") 
        new_location = getCoordinate()
        new_time = datetime.now()
        delta = new_time - actual_time
        print("delta: " + str(delta.total_seconds()))
        if (delta.total_seconds() > 2):
            location = new_location
            actual_time = new_time
            sock.send(location.encode("utf-8"))
            # data = sock.recv(1024)
            # print(str(data))
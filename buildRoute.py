
from copy import deepcopy
import socket
import time

steps = 10

start_lat = 40.2
start_lon = 30.2

finish_lat = 50
finish_lon = 50


'''
create array of position between start and pos position
    start_pos -- start position. consist of lat and lon
    finish_pos -- finish position. consist of lat and lon
    
'''
def create_route(start_pos, finish_pos, steps):
    route = []

    delta_lat = (finish_pos['lat'] - start_pos['lat']) / steps
    delta_lon = (finish_pos['lon'] - start_pos['lon']) / steps

    actual_pos = deepcopy(start_pos)

    print(delta_lat)
    print(delta_lon)

    for i in range(steps - 1):
        pos = deepcopy(actual_pos)
        route.append(pos)
        actual_pos['lat'] += delta_lat
        actual_pos['lon'] += delta_lon


    route.append(finish_pos)

    return route

def send_route_to_sever(route, sleep_time):
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 22500  # The port used by the server

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    for point in route:
        height = 100
        str = '{0},{1},{2}\n'.format(point['lat'], point['lon'], height)
        sock.send(str.encode("utf-8"))
        time.sleep(sleep_time)




def main():
    start_pos = {'lat' : start_lat, 'lon' : start_lon}
    finish_pos = {'lat' : finish_lat, 'lon' : finish_lon}
    
    route = create_route(start_pos, finish_pos, steps)

    for point in route:
        print(point)

    send_route_to_sever(route, 3)

if __name__ == "__main__":
    main()
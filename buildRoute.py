
from copy import deepcopy
import socket
import time
import pandas as pd
import argparse



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
    
        str = '{0},{1},{2}\n'.format(point['lat'], point['lon'], point['height'])
        sock.send(str.encode("utf-8"))
        time.sleep(sleep_time)


def convert_to_csv(route):
    df = pd.DataFrame.from_dict(route) 
    dir = './'
    filename = dir + 'location.csv'
    df.to_csv(filename, index=False, header=True)

def main():

    

    parser = argparse.ArgumentParser(description='Run.py - GPS spoofing tool')

    parser.add_argument('-b', action="store", dest='start_pos', type=str, help='Start position in format lat,lon', default='40.2,30.2')
    parser.add_argument('-e', action="store", dest='finish_pos', type=str, help='Finish position in format lat,lon', default='40.2,30.2')
    parser.add_argument('-s', action="store", dest='steps', type=int, help='Steps count', default=20)
    parser.add_argument('--server', action="store_true", dest='start_server', help='start server', default = False)
    parser.add_argument('--csv', action="store_true", dest='convert_to_scv', help='Convertatioon to scv', default = False)
    parser.add_argument('-t', action="store", dest='time', type=int, help='time to sending  to server', default= 3)

    results = parser.parse_args()

    start_str = results.start_pos.split(",")
    print(start_str)

    start_lat = float(start_str[0])
    start_lon = float(start_str[1])

    finish_str = results.finish_pos.split(",")

    finish_lat = float(finish_str[0])
    finish_lon = float(finish_str[1])

    start_pos = {'lat' : start_lat, 'lon' : start_lon, 'height' : 100}
    finish_pos = {'lat' : finish_lat, 'lon' : finish_lon, 'height': 100}
    
    steps = int(results.steps)
    
    route = create_route(start_pos, finish_pos, steps)

    for point in route:
        print(point)

    if(results.convert_to_scv == True):
         convert_to_csv(route)

    if (results.start_server == True):
        send_route_to_sever(route, results.time)

if __name__ == "__main__":
    main()
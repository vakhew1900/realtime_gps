from gpsdclient import GPSDClient



# or as python dicts (optionally convert time information to `datetime` objects)
with GPSDClient() as client:
    # print(client.dict_stream)
    for result in client.dict_stream(convert_datetime=True, filter=["TPV"]):
        print("Latitude: %s" % result.get("lat", "n/a"))
        print("Longitude: %s" % result.get("lon", "n/a"))


import json
import requests
import socket
import threading

server_address = ('127.0.0.1', 5855)
error_msg = "info not found"

clients_record = [] 
clients_online = []  

access_key = '74a7073f2f0f04a5b72771ba2d23de25'

airport_code = input("Enter Airport Code: ")
print("Please wait \nRequesting Flight Record")

all_flights = []
arrival_flights = []
delayed_flights = []

params = {'access_key': access_key, 'arr_icao': airport_code, 'flight_status': "landed"}
api_result = requests.get('http://api.aviationstack.com/v1/flights', params)
response = api_result.json()
arrival_flights = response["data"]

params = {'access_key': access_key, 'arr_icao': airport_code, 'min_delay_arr': 1}
api_result = requests.get('http://api.aviationstack.com/v1/flights', params)
response = api_result.json()
delayed_flights = response["data"]

params = {'access_key': access_key, 'arr_icao': airport_code, 'limit': 100}
api_result = requests.get('http://api.aviationstack.com/v1/flights', params)
response = api_result.json()
all_flights = response["data"]
all_flights = arrival_flights + delayed_flights

print("Flight Record Received")

with open("group_2.json", "w") as file:
    json.dump(all_flights, file)

def option_1():
    result = {"IATA": "", "departure airport": "", "arrival time": "", "terminal": "", "gate": ""}
    flights = []
    for flight in arrival_flights:
        result["IATA"] = flight['flight']['iata']
        result["departure airport"] = flight['departure']['airport']
        result["arrival time"] = flight['arrival']['scheduled']
        result["terminal"] = flight['arrival']['terminal']
        result["gate"] = flight['arrival']['gate']
        flights.append(result)
    return flights

def option_2():
    result = {"IATA": "", "departure airport": "", "departure time": "", "estimated time arrival": "",
              "terminal": "", "gate": ""}
    flights = []
    for flight in delayed_flights:
        result["IATA"] = flight['flight']['iata']
        result["departure airport"] = flight['departure']['airport']
        result["departure time"] = flight['arrival']['scheduled']
        result["estimated time arrival"] = flight['arrival']['estimated']
        result["terminal"] = flight['arrival']['terminal']
        result["gate"] = flight['arrival']['gate']
        flights.append(result)
    return flights

def option_3(city_name):
    result = {"IATA": "", "departure airport": "", "departure time": "", "estimated time arrival": "",
              "terminal": "", "gate": ""}
    for flight in all_flights:
        if flight["departure"]["airport"] == city_name: 
           result["IATA"] = flight['flight']['iata']
           result["departure airport"] = flight['departure']['airport']
           result["departure time"] = flight['departure']['scheduled']
           result["estimated time arrival"] = flight['arrival']['estimated']
           result["terminal"] = flight['arrival']['terminal']
           result["gate"] = flight['arrival']['gate']
           return result 
    return False

def option_4(flight_no):
    result = {"IATA": "", "DATE": "", "departure airport": "", "departure gate": "", "departure terminal": "",
              "arrival airport": "", "arrival gate": "", "arrival terminal": "", "status": "", "departure time": "",
              "arrival time": "", "est arrival time": "", "delay": ""}
    for flight in all_flights:
        if flight["flight"]["number"] == flight_no: 
           result["IATA"] = flight['flight']['iata']
           result["DATE"] = flight['flight_date']

           result["departure airport"] = flight['departure']['airport']
           result["departure gate"] = flight['departure']['gate']
           result["departure terminal"] = flight['departure']['terminal']

           result["arrival airport"] = flight['arrival']['airport']
           result["arrival gate"] = flight['arrival']['gate']
           result["arrival terminal"] = flight['arrival']['terminal']

           result["status"] = flight['flight_status']
           result["departure time"] = flight['departure']['scheduled']
           result["arrival time"] = flight['arrival']['scheduled']
           result["est arrival time"] = flight['arrival']['estimated']
           result["delay"] = flight['arrival']['delay']
           return result

def search_database(option, selector):
    search_result = {}
    if option == '1':
        search_result = option_1()
    elif option == '2':
        search_result = option_2()
    elif option == '3':
        search_result = option_3(selector)
    elif option == '4':
        search_result = option_4(selector)
    return search_result

def thread_code(sock, client_id):
    try:
        client_name = sock.recv(1024).decode('ascii')
        user = {"name": client_name, "ID": client_id}

        clients_online.append(user)
        threading.currentThread().setName(client_name)
        print("[CONNECTED] Client ({}) - ID = {}".format(threading.currentThread().getName(), client_id))

        while True:
            msg = sock.recv(1024).decode('ascii')
            if msg == "Quit":
                break

            data = json.loads(msg)
            option = data["option"]
            selector = data["selector"]

            result = search_database(option, selector)
            if result:
                data = json.dumps(result)
                msg_size = len(data)
                sock.send(str(msg_size).encode("ascii"))
                sock.sendall(data.encode("ascii"))
            else:
                sock.send(error_msg.encode("ascii"))

    except ConnectionError:
        print("Something went wrong with the connection")

    print("{} client with id:{} have left the Server".format(client_name, client_id))
    clients_online.remove(user)

    if len(clients_online) >= 1:
        print("\nClients Online: ", clients_online)
    else:
        print("All clients left")

sock_p = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_p.bind(server_address)
sock_p.listen(3)

while True:
    try:
        sock, sockname = sock_p.accept()
        t = threading.Thread(target=thread_code, args=(sock, len(clients_record) + 1))
        t.start()
    except socket.error:
        break

print("All users have logged off")
print(10 * "=", "Server turned off", 10 * "=")

sock.close()

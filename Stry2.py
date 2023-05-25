import socket
import json
import requests
import threading

# Function to retrieve data from aviationstack API
def get_flight_data(arr_icao):
    url = "http://api.aviationstack.com/v1/flights"
    params = {
        "access_key":" b9acb93ff618f64e7f3def87788b939b ",
        "arr_icao": arr_icao,
        "flight_status": "active",
        "limit": 100
    }
    response = requests.get(url, params=params)
    data = response.json()
    with open(f"{arr_icao}.json", "w") as f:
        json.dump(data, f)
    return data

# Function to handle client requests
def handle_client(conn, addr , arr_icao, access_key) :
    print(f"New connection from {addr}")
    client_name = conn.recv(1024).decode("utf-8")
    print(f"{client_name} connected.")
    while True:
        try:
            request = conn.recv(1024).decode("utf-8")
            if request.startswith("ARRIVED"):
                # Extract arrived flights information from flight data
                
                flight_data = get_flight_data(arr_icao, access_key)
                if flight_data:
                    arrived_flights = [f for f in flight_data["data"] if f["flight_status"] == "landed"]
                    response = json.dumps(arrived_flights)
                else:
                    response = "Error retrieving flight data."
                # and send it to the client
                conn.sendall(response.encode("utf-8"))
            elif request.startswith("DELAYED"):
                # Extract delayed flights information from flight data
                flight_data = get_flight_data(arr_icao, access_key)
                if flight_data:
                    delayed_flights = [f for f in flight_data["data"] if f["flight_status"] == "delayed"]
                    response = json.dumps(delayed_flights)
                else:
                    response = "Error retrieving flight data."
                conn.sendall(response.encode("utf-8"))
            elif request.startswith("FROM"):
                # Extract flights from a specific airport information from flight data and send it to the client
                airport = request.split()[1].upper()
                flight_data = get_flight_data(arr_icao, access_key)
                if flight_data:
                    flights_from_airport = [f for f in flight_data["data"] if f["departure"]["airport"] == airport]
                    response = json.dumps(flights_from_airport)
                else:
                    response = "Error retrieving flight data."
                conn.sendall(response.encode("utf-8"))
            elif request.startswith("DETAILS"):
                 # Extract details of a particular flight information from flight data and send it to the client
                flight_number = request.split()[1].upper()
                flight_data = get_flight_data(arr_icao, access_key)
                if flight_data:
                    flight_details = [f for f in flight_data["data"] if f["flight"]["iata_number"] == flight_number]
                    response = json.dumps(flight_details)
                else:
                    response = "Error retrieving flight data."
                # ...
                conn.sendall(response.encode("utf-8"))
            elif request.startswith("QUIT"):
                # Close the connection with the client
                print(f"{client_name} disconnected.")
                conn.close()
                break
        except:
            print(f"{client_name} disconnected.")
            conn.close()
            break

# Main function to start the server
def start_server():
    # Get airport code from user input
     arr_icao = input("Enter airport code (ICAO): ").upper()

    # Start server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", 8080))
server_socket.listen(3)
print("Server started. Waiting for connections...")

    # Start accepting client connections
while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

# Start the server
start_server()
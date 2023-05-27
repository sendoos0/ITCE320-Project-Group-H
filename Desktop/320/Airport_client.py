import json
import re
import socket

print(25 * "*" + "\nThe client has started")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('127.0.0.1', 5855)
error_msg = "info not found"
menu = "menu:\n1- Arrived flights\n2- Delayed flights\n3- Flight coming from a specific city\n4- Information about a particular flight\n5- Quit"
selector = ""

def time_adjuster(time):
    [date, time] = re.split('T', time)
    time = time[0:5]
    return date, time

try:
    client_socket.connect(server_address)
    name = input("Enter a username: ") 
    client_socket.send(name.encode("ascii"))

    while True:
        print(menu)
        option = input("Select an option: ")

        if option == '1' or option == '2':
            is_valid_input = "Valid"
            data = {"option": option, "selector": selector}
            msg = json.dumps(data)
            client_socket.send(msg.encode("ascii"))

        elif option == "3":
            selector = input("Enter a city name: ")
            is_valid_input = "Valid"
            data = {"option": option, "selector": selector}
            msg = json.dumps(data)
            client_socket.send(msg.encode("ascii"))

        elif option == "4":
            selector = input("Enter a flight number: ")
            is_valid_input = "Valid"
            data = {"option": option, "selector": selector}
            msg = json.dumps(data)
            client_socket.send(msg.encode("ascii"))

        elif option == "5":
            client_socket.send("Quit".encode("ascii"))
            break
        else:
            print("Invalid option")
            is_valid_input = "Invalid"

        if is_valid_input == 'Valid':
            msg = client_socket.recv(1024).decode("ascii")
            if msg == error_msg:
                print(error_msg)
            else:
                data = b""
                while int(msg) - len(data) > 0:
                    data += client_socket.recv(1024)
                result = json.loads(data.decode("ascii"))

                if option == '1':
                    print("Arrived flights:")
                    n = 0 
                    for flight in result:
                        n += 1
                        print('Flight {}: '.format(n))
                        print("*" * 20)
                        print("Flight Code: {}".format(flight["IATA"]))
                        print("Departure Airport: {}".format(flight["departure airport"]))

                        date, time = time_adjuster(flight["arrival time"])
                        print("Arrival Date: {}".format(date))
                        print("Arrival Time: {}".format(time))

                        print("Terminal: {}".format(flight["terminal"]))
                        print("Gate: {}".format(flight["gate"]))
                        print("*" * 20)
                    print("Total Number of flights: ", n)

                elif option == '2':
                    print("Delayed Flights:")
                    n = 0
                    for flight in result:
                        n += 1
                        print('Flight {}: '.format(n))
                        print("*" * 20)
                        print("Flight Code: {}".format(flight["IATA"]))
                        print("Departure Airport: {}".format(flight["departure airport"]))

                        date, time = time_adjuster(flight["departure time"])
                        print("Departure Date: {}".format(date))
                        print("Estimated Time of Arrival: {}".format(time))

                        date, time = time_adjuster(flight["estimated time arrival"])
                        print("Estimated Date of Arrival: {}".format(date))
                        print("Estimated Time of Arrival: {}".format(time))

                        print("Terminal: {}".format(flight["terminal"]))
                        print("Gate: {}".format(flight["gate"]))
                        print("*" * 20)
                    print("Total Number of flights: ", n)

                elif option == '3':
                    print("Flight Information:")
                    print("*" * 20)
                    print("Flight Code: {}".format(result["IATA"]))
                    print("Departure Airport: {}".format(result["departure airport"]))

                    date, time = time_adjuster(result["departure time"])
                    print("Departure Date: {}".format(date))
                    print("Departure Time: {}".format(time))

                    date, time = time_adjuster(result["estimated time arrival"])
                    print("Estimated Date of Arrival: {}".format(date))
                    print("Estimated Time of Arrival: {}".format(time))

                    print("Terminal: {}".format(result["terminal"]))
                    print("Gate: {}".format(result["gate"]))
                    print("*" * 20)

                elif option == '4':
                    print("Flight Information:")
                    print("*" * 20)
                    print("Flight Code: {}".format(result["IATA"]))
                    print("Date: {}".format(result["DATE"]))

                    print("Departure Airport: {}\nDeparture Gate: {}\nDeparture Terminal: {}".format(
                        result["departure airport"], result["departure gate"], result["departure terminal"]))

                    print("Arrival Airport: {}\nArrival Gate: {}\nArrival Terminal: {}".format(
                        result["arrival airport"], result["arrival gate"], result["arrival terminal"]))

                    print("Flight Status: {}".format(result["status"]))

                    date, time = time_adjuster(result["departure time"])
                    print("Departure Date: {}".format(date))
                    print("Departure Time: {}".format(time))

                    date, time = time_adjuster(result["arrival time"])
                    print("Arrival Date: {}".format(date))
                    print("Arrival Time: {}".format(time))

                    date, time = time_adjuster(result["est arrival time"])
                    print("Estimated Date of Arrival: {}".format(date))
                    print("Estimated Time of Arrival: {}".format(time))

                    print("Delay: {}".format(result["delay"]))
                    print("*" * 20)

except ConnectionError:
    print("An error has occurred")

client_socket.close()

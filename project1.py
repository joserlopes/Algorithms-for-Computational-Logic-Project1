#!/usr/bin/python3
# alc24 - 19 - project1
# DO NOT remove or edit the lines above. Thank you.

import sys
from pysat.card import CardEnc, EncType
from pysat.examples.rc2 import RC2
from pysat.formula import WCNF
from pysat.pb import *

from datetime import datetime

base_city = None
n_cities = 0
n_flights = 0
cities = []
flights = []


def parse():
    global base_city
    global n_cities
    global n_flights
    lines = []

    for line in sys.stdin:
        if line != "\n":
            lines.append(line.strip())

    n_cities = int(lines[0])
    base_city = tuple(lines[1].split()) + (1,)
    cities.append(
        {
            "name": base_city[0],
            "airport": base_city[1],
            "nights": 0,
            "id": base_city[2],
        }
    )
    for city, id in zip(lines[2 : 2 + n_cities - 1], range(2, n_cities + 2)):
        info = city.split()
        cities.append(
            {
                "name": info[0],
                "airport": info[1],
                "nights": info[2],
                "id": id,
            }
        )
    n_flights = int(lines[2 + n_cities - 1])
    for flight, id in zip(
        lines[2 + n_cities : 2 + n_cities + n_flights], range(1, n_flights + 1)
    ):
        info = flight.split()
        flights.append(
            {
                "date": info[0],
                "og_airport": info[1],
                "dest_airport": info[2],
                "dep_time": info[3],
                "arr_time": info[4],
                "price": int(info[5]),
                "id": id,
            }
        )


def airport_to_clause(airport):
    for city in cities:
        if city["airport"] == airport:
            return city["id"]


def airport_to_city(airport):
    for city in cities:
        if city["airport"] == airport:
            return city


# flightA is the flight that's "after" "nights" nights
def after_k_nights(dateA, nights, dateB):
    date_format = "%d/%m"
    dateA = datetime.strptime(dateA, date_format)
    dateB = datetime.strptime(dateB, date_format)

    return (dateA - dateB).days == nights


wcnf = WCNF()

parse()

# City == left city
# City + n_cities == arrived at city
for i in range(1, n_cities * 2 + 1):
    # I must have left every city and arrived at every city
    wcnf.append([i])

# If I haven't left base city, I can't have left any other city
for i in range(2, n_cities + 1):
    wcnf.append([1, -i])

# If I have arrived at city base, I have to have arrived at every other city
for i in range(n_cities + 2, n_cities * 2 + 1):
    arrived_at_base_city = n_cities + 1
    wcnf.append([-arrived_at_base_city, i])

for i in range(n_flights):
    flightA = flights[i]
    idA = flightA["id"] + n_cities * 2
    og_city_clause = airport_to_clause(flightA["og_airport"])
    dest_city_clause = airport_to_clause(flightA["dest_airport"]) + n_cities
    # If I have left city i then ci must be true
    wcnf.append([-idA, og_city_clause])
    # If I have arrived at city j then c'i must be true
    wcnf.append([-idA, dest_city_clause])
    # Minimize cost of flights
    wcnf.append([-idA], weight=flightA["price"])
    for j in range(i + 1, n_flights):
        flightB = flights[j]
        idB = flightB["id"] + n_cities * 2
        if idA != idB:
            # If I have left a city, no more flights from that city can exist.
            if flightA["og_airport"] == flightB["og_airport"]:
                if ([-idA, -idB]) not in wcnf.hard:
                    wcnf.append([-idA, -idB])
            # If I have left a city, no more flights to that city can exist, except for base.
            if (
                flightA["og_airport"] == flightB["dest_airport"]
                and airport_to_city(flightA["og_airport"])["nights"] != 0
            ):
                if ([-idA, -idB]) not in wcnf.hard:
                    wcnf.append([-idA, -idB])
            # If I have arrived at a city, no more flights to that city can exist.
            if flightA["dest_airport"] == flightB["dest_airport"]:
                if ([-idA, -idB]) not in wcnf.hard:
                    wcnf.append([-idA, -idB])
            # If I have arrived at _base_ city. No more flights can be taken.
            if (
                airport_to_city(flightA["dest_airport"])["nights"] == 0
                and airport_to_city(flightB["dest_airport"])["nights"] == 0
            ):
                wcnf.append([-idA, -idB])

for city in cities:
    nights = int(city["nights"])
    # nights = None
    # if city["nights"] is not None:
    #     nights = int(city["nights"])
    for i in range(n_flights):
        flightA = flights[i]
        idA = flightA["id"] + n_cities * 2
        if flightA["dest_airport"] == city["airport"]:
            if all(
                map(
                    lambda x: not after_k_nights(x["date"], nights, flightA["date"])
                    if x["og_airport"] == city["airport"]
                    else True,
                    flights,
                )
            ):
                # This flight surely cannot be taken as there are no flights k nights after that depart from that same city
                wcnf.append([-idA])
        # All the flights that don't depart k nights after the one taken have to be false
        for j in range(i + 1, n_flights):
            flightB = flights[j]
            idB = flightB["id"] + n_cities * 2
            if flightA != flightB and city["nights"] is not None:
                if flightA["dest_airport"] == city["airport"]:
                    if flightA["dest_airport"] == flightB[
                        "og_airport"
                    ] and not after_k_nights(flightB["date"], nights, flightA["date"]):
                        wcnf.append([-idA, -idB])


# Number of flights has to be equal to the number of cities
lits = [i for i in range(n_cities * 2 + 1, n_flights + n_cities * 2 + 1)]
# print(lits)
enc = CardEnc.equals(
    lits=lits, bound=n_cities, top_id=wcnf.nv, encoding=EncType.seqcounter
)
for clause in enc.clauses:
    wcnf.append(clause)


def pretty_print_solution(solution):
    total_price = 0
    chosen_flights = ""
    for i in range(n_cities * 2, n_flights + n_cities * 2):
        if solution[i] > 0:
            flight = flights[i - n_cities * 2]
            date, og_city, dest_city, dep_time, flight_price = (
                flight["date"],
                airport_to_city(flight["og_airport"])["name"],
                airport_to_city(flight["dest_airport"])["name"],
                flight["dep_time"],
                flight["price"],
            )
            total_price += flight["price"]
            chosen_flights += (
                f"{date} {og_city} {dest_city} {dep_time} {flight_price}\n"
            )
    return f"{total_price}\n{chosen_flights}"


solver = RC2(wcnf)
# print(wcnf.hard)
# print(wcnf.soft)
solution = solver.compute()
# print(solution)
print(pretty_print_solution(solution), end="")

#!/usr/bin/python3
# alc24 - 19 - project1
# DO NOT remove or edit the lines above. Thank you.

import sys
from pysat.card import CardEnc, EncType
from pysat.examples.rc2 import RC2, RC2Stratified
from pysat.examples.lsu import LSU
from pysat.formula import WCNF, WCNFPlus

from datetime import datetime, timedelta

base_city = None
n_cities = 0
n_flights = 0
n_nights = 0
cities = []
flights = []

date_format = "%d/%m"


def parse():
    global base_city
    global n_cities
    global n_flights
    global n_nights
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
                "nights": int(info[2]),
                "id": id,
            }
        )
        n_nights += int(info[2])
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


# dateA is "after" _nights_ nights comparing to dateB
def after_k_nights(dateA, nights, dateB):
    dateA = datetime.strptime(dateA, date_format)
    dateB = datetime.strptime(dateB, date_format)

    return (dateA - dateB).days == nights


# dateA is more than "after" _nights_ nights comparing to dateB
def greater_than_k_nights(dateA, nights, dateB):
    dateA = datetime.strptime(dateA, date_format)
    dateB = datetime.strptime(dateB, date_format)

    return (dateA - dateB).days > nights


def date_difference(dateA, dateB):
    dateA = datetime.strptime(dateA, date_format)
    dateB = datetime.strptime(dateB, date_format)

    return dateA - dateB


wcnf = WCNFPlus()

parse()

# City == left city
# City + n_cities == arrived at city
for i in range(1, n_cities * 2 + 1):
    # I must have left every city and arrived at every city
    wcnf.append([i])

## NOTE: This next two set of clauses are what force the base city to be the first and the last!!

# If I haven't left base city, I can't have left any other city
for i in range(2, n_cities + 1):
    wcnf.append([1, -i])

# If I have arrived at city base, I have to have arrived at every other city
for i in range(n_cities + 2, n_cities * 2 + 1):
    arrived_at_base_city = n_cities + 1
    wcnf.append([-arrived_at_base_city, i])

same_og = {}
same_dest = {}
same_date = {}
first_day = flights[0]["date"]
last_day = flights[len(flights) - 1]["date"]
for i in range(n_flights):
    flightA = flights[i]
    idA = flightA["id"] + n_cities * 2
    og_airport = flightA["og_airport"]
    dest_airport = flightA["dest_airport"]
    og_city_clause = airport_to_clause(og_airport)
    dest_city_clause = airport_to_clause(dest_airport) + n_cities
    dateA = flightA["date"]
    cityA = airport_to_city(og_airport)
    dest_city = airport_to_city(dest_airport)
    max_date = (
        datetime.strptime(dateA, date_format) + timedelta(days=n_nights)
    ).strftime("%d/%m")
    nightsA = cityA["nights"]

    # If I have left city i then ci must be true
    wcnf.append([-idA, og_city_clause])
    # If I have arrived at city j then c'i must be true
    wcnf.append([-idA, dest_city_clause])
    # Minimize cost of flights
    wcnf.append([-idA], weight=flightA["price"])

    if og_airport not in same_og:
        same_og[og_airport] = [idA]
    else:
        same_og[og_airport].append(idA)

    if dest_airport not in same_dest:
        same_dest[dest_airport] = [idA]
    else:
        same_dest[dest_airport].append(idA)

    if dateA not in same_date:
        same_date[dateA] = [idA]
    else:
        same_date[dateA].append(idA)

    # I can't be leaving cities other than base at the first day...
    if nightsA != 0 and dateA == first_day:
        wcnf.append([-idA])

    # I can't be leaving the base city at the last day...
    if nightsA == 0 and dateA == last_day:
        wcnf.append([-idA])

    # If k nights haven't passed, I can't be going back to base
    if dest_city["nights"] == 0 and date_difference(dateA, first_day).days < n_nights:
        wcnf.append([-idA])

    # If I'm leaving base city, make sure to have at least n_nigths nights left
    if nightsA == 0 and date_difference(last_day, dateA).days < n_nights:
        wcnf.append([-idA])

    for j in range(i + 1, n_flights):
        flightB = flights[j]
        idB = flightB["id"] + n_cities * 2
        flightB_date = flightB["date"]
        if idA != idB:
            # If I have left a city, no more flights to that city can exist, except for base.
            if (
                flightA["og_airport"] == flightB["dest_airport"]
                and airport_to_city(flightA["og_airport"])["nights"] != 0
            ):
                wcnf.append([-idA, -idB])
            # If I take a flight to city A, then a flight from city A that is not k nights after can't be true
            nightsB = airport_to_city(dest_airport)["nights"]
            if flightA["dest_airport"] == flightB["og_airport"]:
                if not after_k_nights(flightB["date"], nightsB, flightA["date"]):
                    wcnf.append([-idA, -idB])

# Can only leave a city once
for x in same_og.values():
    enc = CardEnc.equals(lits=x, bound=1, top_id=wcnf.nv, encoding=EncType.totalizer)
    for clause in enc.clauses:
        wcnf.append(clause)

# Can only arrive at a city once
for x in same_dest.values():
    enc = CardEnc.equals(lits=x, bound=1, top_id=wcnf.nv, encoding=EncType.totalizer)
    for clause in enc.clauses:
        wcnf.append(clause)

# Cannot take more that one flight per day
for x in same_date.values():
    enc = CardEnc.atmost(lits=x, bound=1, top_id=wcnf.nv, encoding=EncType.totalizer)
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
    print(f"{total_price}\n{chosen_flights}".strip())


solver = RC2Stratified(wcnf, solver="g4")
solution = solver.compute()
pretty_print_solution(solution)

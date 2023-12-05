import datetime
import json
import random
from datetime import timedelta
from random import randint
from threading import Thread

import requests


def send_state(data):
    token = (
        (
            requests.post(
                "https://emotion-projects.eu/api/auth/login/",
                data={
                    "username": "manager-admin_Spotlink",
                    "password": "Testissimo1!234",
                },
            )
        )
        .json()
        .get("key")
    )
    res = requests.post(
        "https://emotion-projects.eu/api/vehicle-states/",
        data=data,
        headers={"Authorization": f"Token {token}"},
    )
    print(f"respond from server: {res.json()}\n {json.dumps(data, indent=2)}")
    print(f"respond from server: {token}")
    # print(json.dumps(data, indent=2))


inMovimento1 = randint(0, 1)
inRicarica1 = randint(0, 1)
TARGA1 = 7
dataInizio1 = datetime.datetime(2021, 10, 9, 16, 00)
kmTot1 = 82294
numRicariche1 = 31
kwCaricati1 = 54.94
TARGA2 = 4
inMovimento2 = randint(0, 1)
inRicarica2 = randint(0, 1)
dataInizio2 = datetime.datetime(2021, 10, 13, 16, 00)
kmTot2 = 37662
numRicariche2 = 1
kwCaricati2 = 0


class Simulazione:
    def __init__(
        self,
        battery,
        targa,
        data,
        inMovimento,
        inRicarica,
        kmTot,
        numRicariche,
        kwCaricati,
    ):
        self.battery = battery
        self.targa = targa
        self.data = data
        self.inMovimento = inMovimento
        self.inRicarica = inRicarica
        self.kmTot = kmTot
        self.numRicariche = numRicariche
        self.kwCaricati = kwCaricati
        self.start_simulation()

    def is_night(self):
        dateFomatter = self.data.strftime("%Y-%m-%d %H:%M:%S")
        send_state(
            {
                "km_tot": self.kmTot,
                "battery_percentage": self.battery,
                "velocity": 0,
                "timestamp": dateFomatter,
                "in_charge": "false",
                "charges_count": self.numRicariche,
                "kwh_charged": self.kwCaricati,
                "vehicle": self.targa,
                "efficiency": "0",
            }
        )
        self.data = self.data + timedelta(hours=5)

    def car_is_in_movement(self):
        Elapsed = timedelta(minutes=2).total_seconds()
        # FinalDistance = 0
        distanzaPercorsa = randint(3, 16)
        if self.battery >= 20:
            for FinalDistance in range(distanzaPercorsa):
                dateFomatter = self.data.strftime("%Y-%m-%d %H:%M:%S")
                Distance = randint(1000, 3300)
                float(Elapsed)
                Velocity = (Distance / Elapsed) * (3600 / 1000)
                batteryBefore = int(self.battery)
                self.battery -= Velocity / 60
                batteryAfter = int(self.battery)
                kmBefore = self.kmTot
                kmAfter = self.kmTot + (Distance / 1000)
                kmTot = int(kmAfter)
                efficiency = str(
                    round((batteryBefore - batteryAfter) / (kmAfter - kmBefore), 3)
                )
                self.kmTot = kmTot

                send_state(
                    {
                        "km_tot": kmTot,
                        "battery_percentage": int(self.battery),
                        "velocity": int(Velocity),
                        "timestamp": dateFomatter,
                        "in_charge": "false",
                        "charges_count": self.numRicariche,
                        "kwh_charged": self.kwCaricati,
                        "vehicle": self.targa,
                        "efficiency": efficiency,
                    }
                )
                if self.battery <= 25:
                    self.inMovimento = 0
                    self.inRicarica = 1

                self.data = self.data + timedelta(minutes=3)

    def car_in_charge(self):
        numRicariche = self.numRicariche + 1
        self.numRicariche = numRicariche
        while self.battery <= 97:
            if self.battery < 85:  # ricarica rapida
                self.battery += randint(0, 2)
                Battperc = round((random.random() * 2), 2)
                kwCaricati = round(self.kwCaricati + Battperc, 2)
                self.kwCaricati = kwCaricati
                dateFomatter = self.data.strftime("%Y-%m-%d %H:%M:%S")
                send_state(
                    {
                        "km_tot": int(self.kmTot),
                        "battery_percentage": int(self.battery),
                        "velocity": 0,
                        "timestamp": dateFomatter,
                        "in_charge": "true",
                        "charges_count": numRicariche,
                        "kwh_charged": kwCaricati,
                        "vehicle": self.targa,
                        "efficiency": "charging",
                    }
                )
                self.data = self.data + timedelta(minutes=3)
            else:  # ricarica lenta
                self.battery += randint(0, 2)
                Battperc = round(random.random(), 2)
                kwCaricati = round(self.kwCaricati + Battperc, 2)
                dateFomatter = self.data.strftime("%Y-%m-%d %H:%M:%S")
                send_state(
                    {
                        "km_tot": int(self.kmTot),
                        "battery_percentage": int(self.battery),
                        "velocity": 0,
                        "timestamp": dateFomatter,
                        "in_charge": "true",
                        "charges_count": numRicariche,
                        "kwh_charged": kwCaricati,
                        "vehicle": self.targa,
                        "efficiency": "charging",
                    }
                )
                self.data = self.data + timedelta(minutes=3)

    def car_is_parked(self):
        tempoAttesa = randint(0, 10)
        for attesa in range(tempoAttesa):
            dateFomatter = self.data.strftime("%Y-%m-%d %H:%M:%S")
            send_state(
                {
                    "km_tot": self.kmTot,
                    "battery_percentage": self.battery,
                    "velocity": 0,
                    "timestamp": dateFomatter,
                    "in_charge": "false",
                    "charges_count": self.numRicariche,
                    "kwh_charged": self.kwCaricati,
                    "vehicle": self.targa,
                    "efficiency": "0",
                }
            )
            self.data = self.data + timedelta(minutes=3)
            self.data = self.data + timedelta(hours=2)
            self.inMovimento = randint(0, 1)
            self.inRicarica = randint(0, 1)
            if self.inMovimento == 1:
                self.inRicarica = 0

    def start_simulation(self):
        oggi = datetime.datetime.now()
        while self.data <= oggi:
            if self.data.hour > 21 or self.data.hour < 7:  # se e' notte
                self.is_night()
            else:  # e' giorno
                if self.inMovimento == 1:  # la macchina e' in movimento
                    self.car_is_in_movement()
                else:  # macchina ferma
                    if self.inRicarica == 1 and self.battery < 25:  # macchina in ricarica
                        self.car_in_charge()
                    else:  # macchina ferma
                        self.car_is_parked()


if __name__ == "__main__":
    auto1 = Thread(
        target=Simulazione,
        args=(
            30,
            TARGA1,
            dataInizio1,
            inMovimento1,
            inRicarica1,
            kmTot1,
            numRicariche1,
            kwCaricati1,
        ),
    )
    auto1.start()
    auto2 = Thread(
        target=Simulazione,
        args=(
            25,
            TARGA2,
            dataInizio2,
            inMovimento2,
            inRicarica2,
            kmTot2,
            numRicariche2,
            kwCaricati2,
        ),
    )
    auto2.start()

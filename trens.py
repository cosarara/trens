#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""

"""

import sys
#import requests
from datetime import datetime
from collections import namedtuple
from pprint import pprint

import json
import aiohttp
import asyncio
import async_timeout

class Train(namedtuple("Train", ['sortida', 'arribada', 'linia'])):
    def __lt__(self, other):
        return self.sortida < other.sortida

    def __str__(self):
        return "{}\t{}\t".format(
            self.linia,
            self.hora_sortida(),
            self.hora_arribada())

    def hora_sortida(self):
        return self.sortida.strftime("%H:%M")

    def hora_arribada(self):
        return self.arribada.strftime("%H:%M")


def make_train(data):
    sortida = datetime.strptime(data["sortida"], "%d/%m/%Y %H:%M:%S")
    arribada = datetime.strptime(data["arribada"], "%d/%m/%Y %H:%M:%S")
    return Train(sortida, arribada, data["linia"])

def get_trains(date, src="SC", dst="UN"):
    url = 'http://www.fgc.net/cercador/cerca.asp'
    trains = set()

    async def fetch(session, payload):
        async with session.get(url, params=payload) as resp:
            assert resp.status == 200
            text = await resp.text()
            r_out = json.loads(text)[0][0]
            for train in r_out:
                train = make_train(train[0])
                trains.add(train)
            print(train)

    loop = asyncio.get_event_loop()
    conn = aiohttp.TCPConnector(limit=10)

    tasks = []
    with aiohttp.ClientSession(loop=loop, connector=conn) as session:
        for i in range(24):
            for j in (0, 20, 40):
                print(i, j)
                payload = {
                    "liniasel": 1,
                    "estacio_origen": src,
                    "estacio_desti": dst,
                    "tipus": "S",
                    "dia": date.strftime("%d/%m/%Y"),
                    "horas": i,
                    "minutos": j
                }
                tasks.append(asyncio.ensure_future(fetch(session, payload)))
        loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()

    return trains

if __name__ == "__main__":
    date = datetime.today()
    trains = get_trains(date)
    print("data fetched on {}".format(date))
    for train in sorted(list(trains)):
        print(train)

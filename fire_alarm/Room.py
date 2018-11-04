#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Room.py
#  
#  Copyright 2018 Francesco Antoniazzi <francesco.antoniazzi1991@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

from cocktail.Thing import Thing
from cocktail.Event import Event
from cocktail.Action import Action

from AlarmLight import AlarmLight
from TempSensor import TempSensor
from SmokeSensor import SmokeSensor
from GasActuator import GasActuator
from AlarmEmitter import AlarmEmitter

import logging


logging.basicConfig(
    format='%(filename)s:%(funcName)s:%(levelname)s:%(message)s',
    level=logging.INFO)
logger = logging.getLogger("CocktailBenchmarkLogger")


class Room:
    def __init__(self, engine, room_number, dataschemas):
        self.engine = engine
        self.number = room_number
        self.baseName = "Room{}".format(room_number)
        self.baseUri = "ct:"+self.baseName
        self.baseTD = self.baseUri+"/thingDescription"
        self.ds = dataschemas

        # setup smoke sensors
        self.smokeSensors = [
            SmokeSensor(self.engine,
                        self.baseUri+"/smoke1",
                        self.baseName+"_smoke1",
                        self.baseTD+"/smoke1", self.ds),
            SmokeSensor(self.engine, self.baseUri+"/smoke2",
                        self.baseName+"_smoke2",
                        self.baseTD+"/smoke2", self.ds)]
        logger.info("Room {} smokeSensors: done".format(room_number))
            
        # setup temperature sensors
        self.tempSensors = [
            TempSensor(self.engine, self.baseUri+"/temp1",
                       self.baseName+"_temp1",
                       self.baseTD+"/temp1", self.ds),
            TempSensor(self.engine, self.baseUri+"/temp2",
                       self.baseName+"_temp2",
                       self.baseTD+"/temp2", self.ds)]
        logger.info("Room {} tempSensors: done".format(room_number))

        # setup red alarm lights
        self.redLights = [
            AlarmLight(self.engine, self.baseUri+"/redLight1",
                       self.baseName+"_redLight1",
                       self.baseTD+"/redLight1", self.ds),
            AlarmLight(self.engine, self.baseUri+"/light2",
                       self.baseName+"_redLight2",
                       self.baseTD+"/redLight2", self.ds)]
        logger.info("Room {} alarmLights: done".format(room_number))
        
        self.gas = GasActuator(self.engine, self.baseUri+"/gasValve",
                               self.baseName+"_gasValve",
                               self.baseTD+"/gasValve", self.ds)
        logger.info("Room {} gasActuator: done".format(room_number))
                               
        self.sound = AlarmEmitter(self.engine, self.baseUri+"/soundAlarm",
                                  self.baseName+"_soundAlarm",
                                  self.baseTD+"/soundAlarm", self.ds)
        logger.info("Room {} soundAlarm: done".format(room_number))

    def run(self):
        logger.info("Running devices...")
        for smokesensor in self.smokeSensors:
            smokesensor.start()
        for tempsensor in self.tempSensors:
            tempsensor.start()
        for light in self.redLights:
            light.enable()
        self.gas.enable()
        self.sound.enable()
        return self

    def shutdown(self):
        logger.info("Shutting down devices...")
        for smokesensor in self.smokeSensors:
            smokesensor.stop()
        for tempsensor in self.tempSensors:
            tempsensor.stop()
        for light in self.redLights:
            light.disable()
        self.gas.disable()
        self.sound.disable()

# Web Of Things example: a fire alarm

In this file a Web of Things application based on the WoT ontology and
on Cocktail. This application consists in a fire alarm control example.

### Concepts
In a first example, we will consider 3 rooms: A, B, C
A and C communicate with B and the external world;
B communicates with A and C, but not with the external world.

In every room we have some sensors, and some actuators:
1. Two smoke sensors;
2. Two temperature sensors;
3. A gas emitter actuator
4. A sound alarm emitter
5. 1 Red alarm light next to each door (i.e. 2 Red alarm lights per room)

The alarm sequence is the following:
_When the first smoke sensor detects smoke, all red lights are switched on.
If, in 60 seconds, another sensor (both temperature, or smoke) is triggered, 
this means that a fire is starting. Otherwise, nothing to do.
When the fire start is detected, the procedure starts:
The sound alarm starts.
A 60 seconds timer starts, to give time to people to run away.
After those 60 seconds, gas emitters start their job, reducing oxigen 
in the room._

### Implementation Methods
##### Cocktail with IFTTT

##### Plain Cocktail

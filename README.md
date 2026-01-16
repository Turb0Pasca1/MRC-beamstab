# MRC-beamstab

Project work in progress  

Python package to use MRC Systems [Active Laser Beam Stabilization](https://www.mrc-systems.de/en/products/laser-beam-stabilization) with python.   
The communication protocol is based on version [JH - 24.05.2023](https://www.mrc-systems.de/downloads/de/laser-strahlstabilisierung/BA-digital-communication-interface_ver8_2.pdf).

## Structure Adjustment:

- connection class
  - connect to the device 
  - send and receive data
  - close connection
  - base class (higher abstraction level) 
    - set basic functions necessary for both serial and TCP/IP 
  - serial and TCP/IP 
    - receive function for known number of bytes
    - and receive function for continues receiving

  - protocol class
    - keep general and close to the communication protocol

  - tango 
    - inherit connection and protocol from classes above to translate command outputs to tango attributes, commands and properties

## Implemented:

- TCP/IP connection to the device
- basic command sending
- decoding received command responses


## ToDo

- implement continues receiving commands
- wait for returns after sending commands
- combine sending and decoding commands
  - adjusthow the command acknowledgement '0;' to feedback whether the command was acknowledged (might solve 'S1S;' return length problem)
- test all possible commands to send
  - sometimes the return of 'S1S;' is shorter than the expected 25 byte length
- add serial connection
- adjust and add tango implementation



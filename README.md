# MRC-beamstab

Python package to use MRC Systems [Active Laser Beam Stabilization](https://www.mrc-systems.de/en/products/laser-beam-stabilization) with python.   
The communication protocol is based on version [JH - 24.05.2023](https://www.mrc-systems.de/downloads/de/laser-strahlstabilisierung/BA-digital-communication-interface_ver8_2.pdf).

## Implemented:

- TCP/IP connection to the device
- basic command sending
- decoding received command responses


## ToDo

- wait for returns after sending commands
- combine sending and decoding commands
  - adjusthow the command acknowledgement '0;' to feedback whether the command was acknowledged (might solve 'S1S;' return length problem)
- test all possible commands to send
  - sometimes the return of 'S1S;' is shorter than the expected 25 byte length
- add serial connection
- adjust and add tango implementation

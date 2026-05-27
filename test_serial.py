from connections import TCPConnection
from connections.serial import SerialConnection
from protocol import ProtocolDecoder  
import time

with SerialConnection('COM5') as conn:
    decoder = ProtocolDecoder(conn)
    enable = True

    # --- P-factor tests ---
    STAGE = 2
    TEST_P = 1200  # mV, within valid 0–5000 range

    print("=== P-factor tests ===")
    print(f"Get P-factor (stage {STAGE}) before set: ", decoder.get_p_factor(STAGE))
    print(f"Set P-factor (stage {STAGE}) to {TEST_P} mV: ", decoder.set_p_factor(STAGE, TEST_P))
    print(f"Get P-factor (stage {STAGE}) after set:  ", decoder.get_p_factor(STAGE))
    print()

    # --- Main loop ---
    while True:
        print("S1S: ", decoder.get_S1S())
        print("GDA: ", decoder.get_GDA())
        print("Set reference position: ", decoder.set_reference_position(450, -80))
        if not enable:
            print("Enable stabilization: ", decoder.enable_stabilization())
        else:
            print("Disable stabilization: ", decoder.disable_stabilization())
        enable = not enable
        print("\r")
        time.sleep(10)

import time 
from typing import Any

import profinet_client_lib

UDP_REMOTE_IP = "127.0.0.1"
UDP_REMOTE_PORT = 5571
LOOP_SLEEP_TIME = 0.5  # seconds

# TODO: Possibly implement a timeout that turns off the relays if
#       no message is received from the Profinet service


def set_bit_value(bitfield: int, bitnumber: int, value: bool) -> int:
    """Set or reset a single bit in an integer

    Args:
        bitfield: The integer before modification
        bitnumber: Which bit to modify. Least significant bit is number 0.
        value: Value of the bit

    Returns:
        The integer after modification

    """
    mask = 1 << bitnumber
    if value:
        return bitfield | mask
    return bitfield & ~mask


def relay_callback(output: profinet_client_lib.Outputdata, arg: Any) -> None:
    """Callback triggered when new outputdata arrives from the PLC

    Args:
        output: Outputdata from PLC
        arg: User argument. In this example it is a reference to the
             inputdata, so it can do some example updates.

    """

    # Outputdata from PLC #
    print("Received ", end="")
    print(output)

    # Inputdata to PLC #
    input = arg

    # Parse bits in the outputdata #
    aux2_relay = (output.controlbits & 0x01) > 0
    aux3_relay = (output.controlbits & 0x02) > 0
    aux4_relay = (output.controlbits & 0x04) > 0
    discharge_relay = (output.controlbits & 0x08) > 0
    charge_relay = (output.controlbits & 0x10) > 0
    go_to_sleep = (output.controlbits & 0x20) > 0
    '''
    # Update inputdata to PLC #
    input.statusbits_a = set_bit_value(input.statusbits_a, 1, aux2_relay)
    input.statusbits_a = set_bit_value(input.statusbits_a, 2, aux3_relay)
    input.statusbits_a = set_bit_value(input.statusbits_a, 3, aux4_relay)
    input.statusbits_a = set_bit_value(input.statusbits_a, 4, discharge_relay)
    input.statusbits_a = set_bit_value(input.statusbits_a, 5, charge_relay)
    if go_to_sleep:
        input.statusbits_a = set_bit_value(input.statusbits_a, 0, False)
        input.statusbits_a = set_bit_value(input.statusbits_a, 1, False)
        input.statusbits_a = set_bit_value(input.statusbits_a, 2, False)
        input.statusbits_a = set_bit_value(input.statusbits_a, 3, False)
        input.statusbits_a = set_bit_value(input.statusbits_a, 4, False)
        input.statusbits_a = set_bit_value(input.statusbits_a, 5, False)
    '''

def main() -> None:
    """Battery simulator, talking UDP to a Profinet service."""

    print(
        "Battery simulator talking UDP to a Profinet service (which uses Profinet to talk to a PLC)."
    )

    # Fake inputdata to PLC (via Profinet service) #
    input = profinet_client_lib.Inputdata()
    input.valid = True
    input.allowed_charge_current = 13.7
    input.allowed_charge_temp_max = 31.0
    input.allowed_charge_temp_min = -24.3
    input.allowed_discharge_current = 125.0
    input.allowed_discharge_temp_max = 35.0
    input.allowed_discharge_temp_min = -11.0
    input.allowed_cell_voltage_max = 4.13
    input.allowed_cell_voltage_min = 2.64
    input.allowed_batt_voltage_max = 31.4
    input.allowed_batt_voltage_min = 26.3
    input.cells_in_series = 13
    input.nominal_voltage = 28.0
    input.nominal_capacity = 110.0
    input.nominal_energy = input.nominal_voltage * input.nominal_capacity
    input.error_delay_time = 3.5
    input.communication_timeout = 3.0

    input.voltage = 54.6
    input.max_cell_voltage = 3.91
    input.min_cell_voltage = 3.84
    input.pos_cell_max = 3
    input.pos_cell_min = 7
    input.current = 11.23
    input.state_of_charge = 58.3

    input.temperature_1 = 38.9
    input.temperature_2 = 22.3
    input.temperature_3 = 11.3
    input.temperature_4 = 00.3
    input.temperature_5 = -10.3
    input.temperature_6 = -20.3
    input.temperature_7 = -30.3
    input.temperature_8 = -40.3

    input.isolation_minus = 38
    input.isolation_plus = 39.3
    input.spec_isolation_minus = 6700
    input.spec_isolation_plus = 4900

    input.statusbits_a = 0x13
    input.statusbits_b = 0x04
    input.warningbits_a = 0x00
    input.warningbits_b = 0x00
    input.errorbits_a = 0x00
    input.errorbits_b = 0x00

    # Set up communication to Profinet service #
    client = profinet_client_lib.ProfinetServiceClient(
        UDP_REMOTE_IP, UDP_REMOTE_PORT, relay_callback, input
    )

    while True:

        # Calculate fake inputdata #
        input.voltage -= 0.011
        input.max_cell_voltage -= 0.0015
        input.min_cell_voltage -= 0.002
        input.current += 0.013
        input.state_of_charge -= 0.03
        input.temperature_1 += 0.022
        input.temperature_2 += 0.006
        input.temperature_8 += 0.13
        input.warningbits_a ^= 0x0

        print("\nSending simulated ", end="")
        print(input)

        # Send and receive data to Profinet service #
        client.send_inputdata_to_plc(input)
        client.listen()

        time.sleep(LOOP_SLEEP_TIME)


if __name__ == "__main__":
    main()

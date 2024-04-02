import socket
import time

import canopen_client_lib as profinet_client_lib


UDP_LOCAL_IP = "127.0.0.1"
UDP_LOCAL_PORT = 5571
UDP_BUFFER_SIZE = 1024  # bytes
TIMEOUT_VALUE = 3  # seconds
POLL_SLEEP_TIME = 0.001  # seconds


def main() -> None:
    """Profinet service simulator, talking UDP to a battery."""

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serversocket.bind((UDP_LOCAL_IP, UDP_LOCAL_PORT))
    serversocket.setblocking(False)

    print(
        "This process simulates a service that talks Profinet with a PLC, and UDP with a Python program."
    )
    print(f"Listening on UDP port {UDP_LOCAL_PORT}")

    data_age_valid = False
    receive_timestamp = time.time()
    previous_timestamp = receive_timestamp

    # Simulate outputdata from PLC to battery pack #
    output = profinet_client_lib.Outputdata()
    output.controlbits = 0x03

    while True:
        if data_age_valid:
            if time.time() - receive_timestamp > TIMEOUT_VALUE:
                print(
                    "  *** Data is now invalid due to timeout (No data from client) ***"
                )
                data_age_valid = False

        # Receive incoming UDP frame (with inputdata) from battery pack #
        try:
            receivedata, remote_addr = serversocket.recvfrom(UDP_BUFFER_SIZE)
        except BlockingIOError:
            time.sleep(POLL_SLEEP_TIME)
            continue

        receive_timestamp = time.time()
        remote_host, remote_port = remote_addr
        print(
            "\nIncoming UDP frame from IP: {} Port: {} Size: {} bytes. Period {:.3f} s".format(
                remote_host,
                remote_port,
                len(receivedata),
                receive_timestamp - previous_timestamp,
            )
        )
        previous_timestamp = receive_timestamp
        if not data_age_valid:
            print("  *** Data validity is now controlled by client ***")
        data_age_valid = True

        # Parse incoming UDP frame #
        try:
            input = profinet_client_lib.Inputdata.unpack(receivedata)
        except:
            print("Wrong incoming frame length, frame type or protocol version")
            continue
        if input.profinet_slot != profinet_client_lib.DEFAULT_PROFINET_SLOT:
            print("Wrong slot in incoming frame")
            continue
        if input.profinet_subslot != profinet_client_lib.DEFAULT_PROFINET_SUBSLOT:
            print("Wrong subslot in incoming frame")
            continue
        print(input)

        # Update fake outdata to battery pack #
        output.controlbits ^= 0x01
        print("Sending simulated ", end="")
        print(output)

        # Send UDP response #
        serversocket.sendto(output.pack(), remote_addr)


if __name__ == "__main__":
    main()
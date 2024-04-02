from __future__ import annotations

import dataclasses
import socket
import struct
import textwrap
from typing import Any, Callable, ClassVar, Dict, Final, Optional


"""Implementation of Hellpower UDP protocol.

So far it only supports a single UDP port, and a single Profinet subslot on a single slot.

"""

UDP_BUFFER_SIZE: Final[int] = 1024  # bytes
HPUP_PROTOCOL_VERSION: Final[int] = 2  # Hellpower UDP protocol version
STRUCT_FORMAT_HEADER: Final[str] = "!HB2H?H"
STRUCT_FORMAT_INPUTDATA_PAYLOAD: Final[str] = "9f2H4f2H2fH15f6B"
STRUCT_FORMAT_OUTPUTDATA_PAYLOAD: Final[str] = "B"
HPUP_FRAMETYPE_REQUEST: Final[int] = 0x01
HPUP_FRAMETYPE_RESPONSE: Final[int] = 0x02

SIZE_HEADER: Final[int] = struct.calcsize(STRUCT_FORMAT_HEADER)
SIZE_INPUTDATA_FRAME: Final[int] = struct.calcsize(
    STRUCT_FORMAT_HEADER + STRUCT_FORMAT_INPUTDATA_PAYLOAD
)
SIZE_OUTPUTDATA_FRAME: Final[int] = struct.calcsize(
    STRUCT_FORMAT_HEADER + STRUCT_FORMAT_OUTPUTDATA_PAYLOAD
)
SIZE_INPUTDATA_PAYLOAD: Final[int] = SIZE_INPUTDATA_FRAME - SIZE_HEADER
SIZE_OUTPUTDATA_PAYLOAD: Final[int] = SIZE_OUTPUTDATA_FRAME - SIZE_HEADER

DEFAULT_PROFINET_SLOT: Final[int] = 1
DEFAULT_PROFINET_SUBSLOT: Final[int] = 1


NAMES_STATUSBITS_A = {
    0: "AUX1",
    1: "AUX2",
    2: "AUX3",
    3: "AUX4",
    4: "DischargeRelay",
    5: "ChargeRelay",
    6: "Balancing",
    7: "Chargercomm",
}
NAMES_STATUSBITS_B = {
    0: "Charging",
    1: "Finished",
    2: "BatteryOk",
    3: "FS1",
    4: "FS2",
    5: "FS3",
    6: "FS4",
    7: "FS5",
}
NAMES_WARNINGBITS_A = {
    0: "CellOvervoltage",
    1: "CellUndervoltage",
    2: "DischargeOvertemperature",
    3: "DischargeUndertemperature",
    4: "ChargeOvertemperature",
    5: "ChargeUndertemperature",
    6: "DischargeOvercurrent",
    7: "ChargeOvercurrent",
}
NAMES_WARNINGBITS_B = {
    0: "Isolation",
    1: "Unbalanced",
    2: "Discharged",
    3: "FW1",
    4: "FW2",
    5: "FW3",
    6: "FW4",
    7: "FW5",
}
NAMES_ERRORBITS_A = {
    0: "CellOvervoltage",
    1: "CellUndervoltage",
    2: "DischargeOvertemperature",
    3: "DischargeUndertemperature",
    4: "ChargeOvertemperature",
    5: "ChargeUndertemperature",
    6: "DischargeOvercurrent",
    7: "ChargeOvercurrent",
}
NAMES_ERRORBITS_B = {
    0: "Isolation",
    1: "CommTimeout",
    2: "HardwareFailure",
    3: "FE1",
    4: "FE2",
    5: "FE3",
    6: "FE4",
    7: "FE5",
}
NAMES_CONTROLBITS = {
    0: "AUX2",
    1: "AUX3",
    2: "AUX4",
    3: "DischargeRelay",
    4: "ChargeRelay",
    5: "Sleep",
    6: "FC1",
    7: "FC2",
}


def _describe_byte_contents(bitdescriptions: Dict[int, str], value: int) -> str:
    """Describe which bits that are currently set in a byte.

    Args:
        bitdescriptions: Texts describing the bits
        value: Current value of the byte

    Returns:
        Single line string describing which bits are set

    """
    descriptions = []
    for bitnumber, text in bitdescriptions.items():
        mask = 1 << bitnumber
        if value & mask:
            descriptions.append(text)
    return " ".join(descriptions)


def _generate_bit_description_table(title: str, bitdescriptions: Dict[int, str]):
    """Generate a ReST description string about the bits in a byte.

    Args:
        title: Title
        bitdescriptions: Texts describing the bits

    Returns:
        Text and table in ReST format

    """
    text = "**" + title + "**\n\n"
    text += "========== ========================\n"
    text += "Bit number Description\n"
    text += "========== ========================\n"
    for bitnumber in sorted(bitdescriptions.keys()):
        description = bitdescriptions[bitnumber]
        text += f"{bitnumber:<10} {description}\n"
    text += "========== ========================\n\n"

    return text


@dataclasses.dataclass
class Inputdata:
    """Inputdata to the PLC"""

    # Profinet payload to PLC
    # Int is uint16_t on wire, and float is float32_t
    # Fields named 'bits' are uint8_t on the wire
    voltage: float = 0.0
    current: float = 0.0
    state_of_charge: float = 0.0
    temperature_1: float = 0.0
    temperature_2: float = 0.0
    temperature_3: float = 0.0
    temperature_4: float = 0.0
    max_cell_voltage: float = 0.0
    min_cell_voltage: float = 0.0
    pos_cell_max: int = 0
    pos_cell_min: int = 0
    isolation_plus: float = 0.0
    isolation_minus: float = 0.0
    spec_isolation_plus: float = 0.0
    spec_isolation_minus: float = 0.0
    fp1: int = 0
    fp2: int = 0
    fp3: float = 0.0
    fp4: float = 0.0
    cells_in_series: int = 0
    allowed_cell_voltage_max: float = 0.0
    allowed_cell_voltage_min: float = 0.0
    allowed_batt_voltage_max: float = 0.0
    allowed_batt_voltage_min: float = 0.0
    allowed_discharge_current: float = 0.0
    allowed_charge_current: float = 0.0
    allowed_discharge_temp_max: float = 0.0
    allowed_discharge_temp_min: float = 0.0
    allowed_charge_temp_max: float = 0.0
    allowed_charge_temp_min: float = 0.0
    error_delay_time: float = 0.0
    communication_timeout: float = 0.0
    nominal_voltage: float = 0.0
    nominal_capacity: float = 0.0
    nominal_energy: float = 0.0
    statusbits_a: int = 0
    statusbits_b: int = 0
    warningbits_a: int = 0
    warningbits_b: int = 0
    errorbits_a: int = 0
    errorbits_b: int = 0

    # Part of user header
    valid: bool = True
    profinet_slot: int = DEFAULT_PROFINET_SLOT
    profinet_subslot: int = DEFAULT_PROFINET_SUBSLOT
    version: ClassVar[int] = HPUP_PROTOCOL_VERSION
    frame_type: ClassVar[int] = HPUP_FRAMETYPE_REQUEST
    payload_size: ClassVar[int] = SIZE_INPUTDATA_PAYLOAD
    formatter: ClassVar[struct.Struct] = struct.Struct(
        STRUCT_FORMAT_HEADER + STRUCT_FORMAT_INPUTDATA_PAYLOAD
    )

    def __str__(self) -> str:
        string_valid = "Valid" if self.valid else "Invalid"
        string_statusbits_a = _describe_byte_contents(
            NAMES_STATUSBITS_A, self.statusbits_a
        )
        string_statusbits_b = _describe_byte_contents(
            NAMES_STATUSBITS_B, self.statusbits_b
        )
        string_warningbits_a = _describe_byte_contents(
            NAMES_WARNINGBITS_A, self.warningbits_a
        )
        string_warningbits_b = _describe_byte_contents(
            NAMES_WARNINGBITS_B, self.warningbits_b
        )
        string_errorbits_a = _describe_byte_contents(
            NAMES_ERRORBITS_A, self.errorbits_a
        )
        string_errorbits_b = _describe_byte_contents(
            NAMES_ERRORBITS_B, self.errorbits_b
        )

        return (
            f"{self.__class__.__name__} {string_valid} {self.current:.2f}A {self.state_of_charge:.2f}% {self.voltage:.2f}V "
            + f"({self.cells_in_series} cells {self.min_cell_voltage:.2f}V to {self.max_cell_voltage:.2f}V at {self.pos_cell_min} and {self.pos_cell_max}) "
            + f"T1: {self.temperature_1:.1f}C T2: {self.temperature_2:.1f}C T3: {self.temperature_3:.1f}C T4: {self.temperature_4:.1f}C "
            + f"Plus: {self.isolation_plus:.1f}kOhm {self.spec_isolation_plus:.1f}Ohm/V Minus: {self.isolation_minus:.1f}kOhm {self.spec_isolation_minus:.1f}Ohm/V\n"
            + f"   Allowed {self.allowed_cell_voltage_min:.2f}V to {self.allowed_cell_voltage_max:.2f}V "
            + f"Charge {self.allowed_charge_current:.2f}A {self.allowed_charge_temp_min:.1f}C to {self.allowed_charge_temp_max:.1f}C "
            + f"Disharge {self.allowed_discharge_current:.2f}A {self.allowed_discharge_temp_min:.1f}C to {self.allowed_discharge_temp_max:.1f}C\n"
            + f"   Nominal {self.nominal_voltage:.1f}V ({self.allowed_batt_voltage_min:.1f}V-{self.allowed_batt_voltage_max:.1f}V) {self.nominal_capacity:.1f}Ah {self.nominal_energy:.1f}Wh "
            + f"Error delay setting {self.error_delay_time:.1f}s Timeout setting {self.communication_timeout:.1f}s\n"
            + f"   Status A:    {self.statusbits_a:#04x}   {string_statusbits_a}\n"
            + f"   Status B:    {self.statusbits_b:#04x}   {string_statusbits_b}\n"
            + f"   Warnings A:  {self.warningbits_a:#04x}   {string_warningbits_a}\n"
            + f"   Warnings B:  {self.warningbits_b:#04x}   {string_warningbits_b}\n"
            + f"   Errors A:    {self.errorbits_a:#04x}   {string_errorbits_a}\n"
            + f"   Errors B:    {self.errorbits_b:#04x}   {string_errorbits_b}"
        )

    def pack(self) -> bytes:
        """Pack the data into a bytes object"""

        return self.formatter.pack(
            int(self.version),
            int(self.frame_type),
            int(self.profinet_slot),
            int(self.profinet_subslot),
            bool(self.valid),
            int(self.payload_size),
            float(self.voltage),
            float(self.current),
            float(self.state_of_charge),
            float(self.temperature_1),
            float(self.temperature_2),
            float(self.temperature_3),
            float(self.temperature_4),
            float(self.max_cell_voltage),
            float(self.min_cell_voltage),
            int(self.pos_cell_max),
            int(self.pos_cell_min),
            float(self.isolation_plus),
            float(self.isolation_minus),
            float(self.spec_isolation_plus),
            float(self.spec_isolation_minus),
            int(self.fp1),
            int(self.fp2),
            float(self.fp3),
            float(self.fp4),
            int(self.cells_in_series),
            float(self.allowed_cell_voltage_max),
            float(self.allowed_cell_voltage_min),
            float(self.allowed_batt_voltage_max),
            float(self.allowed_batt_voltage_min),
            float(self.allowed_discharge_current),
            float(self.allowed_charge_current),
            float(self.allowed_discharge_temp_max),
            float(self.allowed_discharge_temp_min),
            float(self.allowed_charge_temp_max),
            float(self.allowed_charge_temp_min),
            float(self.error_delay_time),
            float(self.communication_timeout),
            float(self.nominal_voltage),
            float(self.nominal_capacity),
            float(self.nominal_energy),
            int(self.statusbits_a),
            int(self.statusbits_b),
            int(self.warningbits_a),
            int(self.warningbits_b),
            int(self.errorbits_a),
            int(self.errorbits_b),
        )

    @classmethod
    def unpack(cls, data: bytes) -> Inputdata:
        """Create a new object by parsing a data bytearray

        :raises: struct.error and ValueError
        """
        (
            version,
            frame_type,
            profinet_slot,
            profinet_subslot,
            valid,
            payload_size,
            voltage,
            current,
            state_of_charge,
            temperature_1,
            temperature_2,
            temperature_3,
            temperature_4,
            max_cell_voltage,
            min_cell_voltage,
            pos_cell_max,
            pos_cell_min,
            isolation_plus,
            isolation_minus,
            spec_isolation_plus,
            spec_isolation_minus,
            fp1,
            fp2,
            fp3,
            fp4,
            cells_in_series,
            allowed_cell_voltage_max,
            allowed_cell_voltage_min,
            allowed_batt_voltage_max,
            allowed_batt_voltage_min,
            allowed_discharge_current,
            allowed_charge_current,
            allowed_discharge_temp_max,
            allowed_discharge_temp_min,
            allowed_charge_temp_max,
            allowed_charge_temp_min,
            error_delay_time,
            communication_timeout,
            nominal_voltage,
            nominal_capacity,
            nominal_energy,
            statusbits_a,
            statusbits_b,
            warningbits_a,
            warningbits_b,
            errorbits_a,
            errorbits_b,
        ) = cls.formatter.unpack(data)

        if version != cls.version:
            raise ValueError(
                "Wrong version of the HPUP protocol: Given {} but it should be {}".format(
                    version, cls.version
                )
            )
        if frame_type != HPUP_FRAMETYPE_REQUEST:
            raise ValueError(
                "Wrong frame type given in the HPUP message. Given {} but it should be {}".format(
                    frame_type, HPUP_FRAMETYPE_REQUEST
                )
            )
        if payload_size != SIZE_INPUTDATA_PAYLOAD:
            raise ValueError(
                "Wrong payload length given in the HPUP message. Given {} but it should be {}".format(
                    payload_size, SIZE_INPUTDATA_PAYLOAD
                )
            )

        return cls(
            voltage,
            current,
            state_of_charge,
            temperature_1,
            temperature_2,
            temperature_3,
            temperature_4,
            max_cell_voltage,
            min_cell_voltage,
            pos_cell_max,
            pos_cell_min,
            isolation_plus,
            isolation_minus,
            spec_isolation_plus,
            spec_isolation_minus,
            fp1,
            fp2,
            fp3,
            fp4,
            cells_in_series,
            allowed_cell_voltage_max,
            allowed_cell_voltage_min,
            allowed_batt_voltage_max,
            allowed_batt_voltage_min,
            allowed_discharge_current,
            allowed_charge_current,
            allowed_discharge_temp_max,
            allowed_discharge_temp_min,
            allowed_charge_temp_max,
            allowed_charge_temp_min,
            error_delay_time,
            communication_timeout,
            nominal_voltage,
            nominal_capacity,
            nominal_energy,
            statusbits_a,
            statusbits_b,
            warningbits_a,
            warningbits_b,
            errorbits_a,
            errorbits_b,
            valid,
            profinet_slot,
            profinet_subslot,
        )

    @classmethod
    def describe_protocol(cls) -> str:
        """Describe on-wire details of the protocol"""
        text = textwrap.dedent(
            f"""
        Input data to the PLC from the battery

        The protocol has big endian format on the wire. Fields 'Fxn' are reserved for future use.

        Frame size (UDP payload size): { SIZE_INPUTDATA_FRAME } bytes. Payload size within HPUP: { SIZE_INPUTDATA_PAYLOAD } bytes

        =========================== =========== ======================= ==============
        Field                       Type        Comment                 Profinet addr
        =========================== =========== ======================= ==============
        Protocol version            UInt16      Should be {HPUP_PROTOCOL_VERSION}
        Frame type                  UInt8       Request ({HPUP_FRAMETYPE_REQUEST:#04x})
        Profinet slot               UInt16      Typically {DEFAULT_PROFINET_SLOT}
        Profinet subslot            UInt16      Typically {DEFAULT_PROFINET_SUBSLOT}
        Valid                       UInt8       1 or 0
        Payload size                UInt16      Bytes after this ({SIZE_INPUTDATA_PAYLOAD})
        Voltage                     Float32     V                       0
        Current                     Float32     A                       4
        State of charge             Float32     %                       8
        Temperature 1               Float32     C                       12
        Temperature 2               Float32     C                       16
        Temperature 3               Float32     C                       20
        Temperature 4               Float32     C                       24
        Max cell voltage            Float32     V                       28
        Min cell voltage            Float32     V                       32
        Pos cell max                UInt16                              36
        Pos cell min                UInt16                              38
        Isolation plus              Float32     kOhm                    40
        Isolation minus             Float32     kOhm                    44
        Spec isolation plus         Float32     Ohm/V                   48
        Spec isolation minus        Float32     Ohm/V                   52
        Reserved FP1                UIint16                             56
        Reserved FP2                UIint16                             58
        Reserved FP3                Float32                             60
        Reserved FP4                Float32                             64
        Cells in series             UInt16                              68
        Allowed cell voltage max    Float32     V                       70
        Allowed cell voltage min    Float32     V                       74
        Allowed batt voltage max    Float32     V                       78
        Allowed batt voltage min    Float32     V                       82
        Allowed discharge current   Float32     A                       86
        Allowed charge current      Float32     A                       90
        Allowed discharge temp max  Float32     C                       94
        Allowed discharge temp min  Float32     C                       98
        Allowed charge temp max     Float32     C                       102
        Allowed charge temp min     Float32     C                       106
        Error delay time            Float32     s                       110
        Communication timeout       Float32     s                       114
        Nominal battery voltage     Float32     V                       118
        Nominal battery capacity    Float32     Ah                      122
        Nominal battery energy      Float32     Wh                      126
        Statusbits A                UInt8                               130
        Statusbits B                UInt8                               131
        Warningbits A               UInt8                               132
        Warningbits B               UInt8                               133
        Errorbits A                 UInt8                               134
        Errorbits B                 UInt8                               135
        =========================== =========== ======================= ==============

        For a more detailed description of the signals, see the GSDML file.

        """
        )

        text += _generate_bit_description_table("Statusbits A", NAMES_STATUSBITS_A)
        text += _generate_bit_description_table("Statusbits B", NAMES_STATUSBITS_B)
        text += _generate_bit_description_table("Warningbits A", NAMES_WARNINGBITS_A)
        text += _generate_bit_description_table("Warningbits B", NAMES_WARNINGBITS_B)
        text += _generate_bit_description_table("Errorbits A", NAMES_ERRORBITS_A)
        text += _generate_bit_description_table("Errorbits B", NAMES_ERRORBITS_B)

        return text


@dataclasses.dataclass
class Outputdata:
    """Outputdata from the PLC"""

    # Profinet payload from PLC
    # Int is uint16_t
    # Fields named 'bits' are uint8_t on the wire
    controlbits: int = 0

    # Part of user header
    valid: bool = True
    profinet_slot: int = DEFAULT_PROFINET_SLOT
    profinet_subslot: int = DEFAULT_PROFINET_SUBSLOT

    version: ClassVar[int] = HPUP_PROTOCOL_VERSION
    frame_type: ClassVar[int] = HPUP_FRAMETYPE_RESPONSE
    payload_size: ClassVar[int] = SIZE_OUTPUTDATA_PAYLOAD
    formatter: ClassVar[struct.Struct] = struct.Struct(
        STRUCT_FORMAT_HEADER + STRUCT_FORMAT_OUTPUTDATA_PAYLOAD
    )

    def __str__(self) -> str:
        string_valid = "Valid" if self.valid else "Invalid"
        string_controlbits = _describe_byte_contents(
            NAMES_CONTROLBITS, self.controlbits
        )
        return f"{self.__class__.__name__} {string_valid} {self.controlbits:#04x} Bits: {string_controlbits}"

    def pack(self) -> bytes:
        """Pack the data into a bytes object"""
        return self.formatter.pack(
            int(self.version),
            int(self.frame_type),
            int(self.profinet_slot),
            int(self.profinet_subslot),
            bool(self.valid),
            int(self.payload_size),
            int(self.controlbits),
        )

    @classmethod
    def unpack(cls, data: bytes) -> Outputdata:
        """Create a new object by parsing a data bytearray

        :raises: struct.error and ValueError
        """
        (
            version,
            frame_type,
            profinet_slot,
            profinet_subslot,
            valid,
            payload_size,
            controlbits,
        ) = cls.formatter.unpack(data)

        if version != cls.version:
            raise ValueError(
                "Wrong version of the HPUP protocol: Given {} but it should be {}".format(
                    version, cls.version
                )
            )

        if frame_type != HPUP_FRAMETYPE_RESPONSE:
            raise ValueError(
                "Wrong frame type given in the HPUP message. Given {} but it should be {}".format(
                    frame_type, HPUP_FRAMETYPE_RESPONSE
                )
            )
        if payload_size != SIZE_OUTPUTDATA_PAYLOAD:
            raise ValueError(
                "Wrong payload length given in the HPUP message. Given {} but it should be {}".format(
                    payload_size, SIZE_OUTPUTDATA_PAYLOAD
                )
            )

        return cls(
            controlbits,
            valid,
            profinet_slot,
            profinet_subslot,
        )

    @classmethod
    def describe_protocol(cls) -> str:
        """Describe on-wire details of the protocol"""
        text = textwrap.dedent(
            f"""
        Output data from the PLC to the battery

        The protocol has big endian format on the wire. Fields 'Fxn' are reserved for future use.

        Frame size (UDP payload size): { SIZE_OUTPUTDATA_FRAME } bytes. Payload size within HPUP: { SIZE_OUTPUTDATA_PAYLOAD } bytes

        =========================== =========== ======================= ==============
        Field                       Type        Comment                 Profinet addr
        =========================== =========== ======================= ==============
        Protocol version            UInt16      Should be {HPUP_PROTOCOL_VERSION}
        Frame type                  UInt8       Response ({HPUP_FRAMETYPE_RESPONSE:#04x})
        Profinet slot               UInt16      Typically {DEFAULT_PROFINET_SLOT}
        Profinet subslot            UInt16      Typically {DEFAULT_PROFINET_SUBSLOT}
        Valid                       UInt8       1 or 0
        Payload size                UInt16      Bytes after this ({SIZE_OUTPUTDATA_PAYLOAD})
        Controlbits                 UInt8                               0
        =========================== =========== ======================= ==============

        For a more detailed description of the signals, see the GSDML file.

        """
        )
        text += _generate_bit_description_table("Controlbits", NAMES_CONTROLBITS)

        return text


class ProfinetServiceClient:
    """Client for connecting to a Profinet service via UDP

    :param remote_ip: Remote IP address
    :param remote_port: Remote UDP port number
    :param callback: Callback triggered when receiving a message
    :param callback_argument: User argument for use in the callback

    :raises IOError: when the UDP socket not can be opened.

    """

    def __init__(
        self,
        remote_ip: str,
        remote_port: int,
        callback: Optional[Callable[[Outputdata, Any], None]] = None,
        callback_argument: Any = None,
    ) -> None:
        self.callback = callback
        self.callback_argument = callback_argument
        self.remote_ip = remote_ip
        self.remote_port = remote_port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        print(
            "Initialising Profinet service client for talking to IP: {} Port: {}".format(
                self.remote_ip, self.remote_port
            )
        )

    def send_inputdata_to_plc(self, input: Inputdata) -> None:
        """Send inputdata to the PLC (via the Profinet service)

        :raises IOError: if it not is possible to send data on the UDP socket.
        """
        self.sock.sendto(input.pack(), (self.remote_ip, self.remote_port))

    def listen(self) -> None:
        """Listen for an UDP frame from the Profinet service.

        Non-blocking, so it will return immediately if there is no UDP frame available.

        Triggers a callback on received frame.

        """
        try:
            receivedata, remote_addr = self.sock.recvfrom(UDP_BUFFER_SIZE)
        except BlockingIOError:
            # No UDP frame available
            return

        if self.callback is None:
            return

        try:
            output = Outputdata.unpack(receivedata)
        except:
            print("Wrong message length, frame type or protocol version")
            return

        if output.profinet_slot != DEFAULT_PROFINET_SLOT:
            print("Wrong slot")
            return

        if output.profinet_subslot != DEFAULT_PROFINET_SUBSLOT:
            print("Wrong subslot")
            return

        self.callback(output, self.callback_argument)

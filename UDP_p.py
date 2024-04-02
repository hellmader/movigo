import time
import threading
import enum
import profinet_client_lib
from typing import Any


class Request(enum.Enum):
    NONE = 0
    BASIC_INFO = 1
    CELL_VOLTAGE = 2

def UDP_callback(output: profinet_client_lib.Outputdata, arg: Any) -> None:
    
    """Callback triggered when new outputdata arrives from the PLC

    Args:
        output: Outputdata from PLC
        arg: User argument. In this example it is a reference to the
             inputdata, so it can do some example updates.

    """
    queue = arg
    data = {}
    
    # Outputdata from PLC #
    #print("Received ", end="")
    #print(output)
    #print(output.controlbits)
    try:
        data['Chargerate'] = output.commanded_chargerate
    except AttributeError:
        pass
    try:
        data['Controlbits'] = output.controlbits
    except AttributeError:
        pass
    queue.put(data)    
    
class UDP(threading.Thread):
    def __init__(self, debugOutput, updateCycle, inUDPfromMain, outUDPtoMain):
        threading.Thread.__init__(self)
        self.debugOutput = debugOutput
        self.updateCycle = updateCycle
        self.inUDPfromMain = inUDPfromMain
        self.outUDPtoMain = outUDPtoMain
        self.data = 0
        self.UDP_REMOTE_IP = "127.0.0.1"
        self.UDP_REMOTE_PORT = 5571
        self.LOOP_SLEEP_TIME = 0.5
        self.client = profinet_client_lib.ProfinetServiceClient(self.UDP_REMOTE_IP, self.UDP_REMOTE_PORT, UDP_callback, self.outUDPtoMain)
        




    def sendUDP(self,data):
        #data = {'Spannung': 45.9+i, 'Strom': 0, 'SoC': 100, 'Temperatur 1': 24.2, 'Temperatur 2': 25.1, 'Temperatur 3': 23.4, 'Temperatur 4': -273.15, 'maximale Zellspannung': 3.534, 'Position maximale Zellspannung': 10, 'minimale Zellspannung': 3.526, 'Position minimale Zellspannung': 5, 'Isolationswiderstand Gehäuse gegen PLUS': 38, 'Isolationswiderstand Gehäuse gegen MINUS': 38, 'spezifischer Isolationswiderstand Gehäuse gegen PLUS': 50, 'spezifischer Isolationswiderstand Gehäuse gegen MINUS': 50, 'Protection Status': 0, 'Balance Status': 0, 'Anzahl der Seriell-Verbindungen': 13, 'maximal erlaubte Zellspannung': 4.25, 'minimal erlaubte Zellspannung': 2.7, 'maximal erlaubte Batteriespannung': 55.25, 'minimal erlaubte Batteriespannung': 35.1, 'maximaler Entladestrom': 60, 'maximaler Ladestrom': 60, 'Minimale Temperatur Laden': 5, 'Maximale Temperatur Laden': 60, 'Minimale Temperatur Entladen': 0, 'Maximale Temperatur Entladen': 65, 'Fehlerauslösezeit': 5, 'nominelle Spannung': 48.1, 'nominelle Kapazität': 52.0, 'nominelle Energie': 2501.2000000000003, 'StatusA': 1, 'StatusB': 4, 'WarningA': 0, 'WarningB': 0, 'ErrorA': 0, 'ErrorB': 0}
        input = profinet_client_lib.Inputdata()
        input.valid = True
        input.allowed_charge_current = data['maximaler Ladestrom']
        input.allowed_charge_temp_max = data['Maximale Temperatur Laden']
        input.allowed_charge_temp_min = data['Minimale Temperatur Laden']
        input.allowed_discharge_current = data['maximaler Entladestrom']
        input.allowed_discharge_temp_max = data['Maximale Temperatur Entladen']
        input.allowed_discharge_temp_min = data['Minimale Temperatur Entladen']
        input.allowed_cell_voltage_max = data['maximal erlaubte Zellspannung']
        input.allowed_cell_voltage_min = data['minimal erlaubte Zellspannung']
        input.allowed_batt_voltage_max = data['maximal erlaubte Batteriespannung']
        input.allowed_batt_voltage_min = data['minimal erlaubte Batteriespannung']
        input.cells_in_series = data['Anzahl der Seriell-Verbindungen']
        input.nominal_voltage = data['nominelle Spannung']
        input.nominal_capacity = data['nominelle Kapazität']
        input.nominal_energy = data['nominelle Energie']
        input.error_delay_time = data['Fehlerauslösezeit']
        input.communication_timeout = 10.0

        input.voltage = data['Spannung']
        input.max_cell_voltage = data['maximale Zellspannung']
        input.min_cell_voltage = data['minimale Zellspannung']
        input.pos_cell_max = data['Position maximale Zellspannung']
        input.pos_cell_min = data['Position minimale Zellspannung']
        input.current = data['Strom']
        input.state_of_charge = data['SoC']

        input.temperature_1 = data['Temperatur 1']
        input.temperature_2 = data['Temperatur 2']
        input.temperature_3 = data['Temperatur 3']
        input.temperature_4 = data['Temperatur 4']
        input.temperature_5 = data['Temperatur 5']
        input.temperature_6 = data['Temperatur 6']
        input.temperature_7 = data['Temperatur 7']
        input.temperature_8 = data['Temperatur 8']

        input.isolation_minus = data['Isolationswiderstand Gehäuse gegen MINUS']
        input.isolation_plus = data['Isolationswiderstand Gehäuse gegen PLUS']
        input.spec_isolation_minus = data['spezifischer Isolationswiderstand Gehäuse gegen MINUS']
        input.spec_isolation_plus = data['spezifischer Isolationswiderstand Gehäuse gegen PLUS']

        input.statusbits_a = data['StatusA']
        input.statusbits_b = data['StatusB']
        input.warningbits_a = data['WarningA']
        input.warningbits_b = data['WarningB']
        input.errorbits_a = data['ErrorA']
        input.errorbits_b = data['ErrorB']
        #print(input)
        self.client.send_inputdata_to_plc(input)
        self.client.listen()
        self.data = data
        
        
    def printsendUDP(self):
        
        print('Data to UDP:   ',self.data)
        
        print("sent UDP Data")
        print("_________________________________________________")
        
    def run(self):
        if self.debugOutput:
            print("can: Run - Start Thread")
        incData = []
        self.running = True            
        
        while(self.running):
            #check for incoming data from main thread
            try:
                #if(self.sendInProgress==False):
                qDataIn = self.inUDPfromMain.get_nowait()
                
                if(qDataIn=="SIG-INT"):
                    # end thread
                    if self.debugOutput:
                        print("Can: End - SIG-INT arrived")
                    self.running = False
                    
                elif(qDataIn!=None):
                    self.sendUDP(qDataIn)
                    #self.printsendUDP()
                
            except:
                # do nothing
                pass
                
            time.sleep(.01)


        if self.debugOutput:
                print("canO: Thread exit")

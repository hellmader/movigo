import psutil
import time
net_sent_old = 0
net_recv_old = 0




while True:
    time.sleep(1)
    # Gesamte CPU-Auslastung
    cpu_percent = psutil.cpu_percent()
    
    # Speicherauslastung
    mem = psutil.virtual_memory()
    mem_percent = mem.percent
    
    # Netzwerkauslastung
    net_io_counters = psutil.net_io_counters()
    net_sent = net_io_counters.bytes_sent
    net_recv = net_io_counters.bytes_recv
    '''
    # Gesamtauslastung
    net_total = net_sent + net_recv
    net_total_percent = (net_total / net_io_counters.speed) * 100
    '''
    # Gesamtnetzwerkauslastung
    net_io_counters = psutil.net_io_counters()
    net_if_stats = psutil.net_if_stats()
    
    # Berechnung der Gesamtauslastung
    net_sent = net_io_counters.bytes_sent*8
    net_recv = net_io_counters.bytes_recv*8
    net_speed = (net_if_stats['eth0'].speed)*1000000
    
    
    net_sent_diff = net_sent - net_sent_old
    net_recv_diff = net_recv - net_recv_old
    
    net_sent_old = net_sent
    net_recv_old = net_recv
    
    
    
    net_total = net_sent_diff + net_recv_diff
    net_total_percent = (net_total / net_speed) * 100
    
    
    print(f"CPU-Auslastung: {cpu_percent}%")
    print(f"Speicherauslastung: {mem_percent}%")
    print(f"Netzwerkauslastung: {net_total_percent}%")
    print('Net Send:', net_sent_diff)
    print('Net Recv:', net_recv_diff)
    print('Net Total:', net_total)
    print('Net Speed:', net_speed)
# Import core POX components
from pox.core import core
from pox.lib.util import dpidToStr
import pox.openflow.libopenflow_01 as of
from pox.lib.recoco import Timer

# Initialize the logger to display info in the POX console
log = core.getLogger()

class BandwidthMonitor(object):
    """
    This component implements an SDN-based network monitoring solution.
    It periodically queries OpenFlow switches for port statistics to 
    calculate and display real-time bandwidth utilization[cite: 3, 39].
    """
    def __init__(self):
        # Register this class to listen for OpenFlow events (e.g., connection, stats)
        core.openflow.addListeners(self)
        
        # Dictionary to store previous byte counters: {dpid: {port_no: (rx_bytes, tx_bytes)}}
        # This is essential for calculating the difference (delta) over time[cite: 36, 39].
        self.stats = {} 
        
        # Create a recurring timer to trigger the statistics request every 5 seconds[cite: 10, 39].
        # Functional Requirement: Update statistics periodically[cite: 11].
        Timer(5, self._request_stats, recurring=True)

    def _request_stats(self):
        """
        Iterates through all switches connected to the controller and sends 
        an OpenFlow Port Statistics Request[cite: 4, 10].
        """
        for connection in core.openflow.connections:
            # Construct and send the ofp_stats_request message
            # body=of.ofp_port_stats_request() targets the switch port counters
            connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))

    def _handle_PortStatsReceived(self, event):
        """
        Event handler triggered when a switch responds with its port statistics[cite: 10].
        Calculates throughput and displays the utilization report[cite: 34, 39].
        """
        dpid = event.connection.dpid
        
        # Initialize stats storage for a new switch connection
        if dpid not in self.stats:
            self.stats[dpid] = {}

        # Display header for the current switch report [cite: 30, 36]
        print("\n--- Switch %s Bandwidth Report ---" % dpidToStr(dpid))
        print("Port | Rx (bps) | Tx (bps) | Total Bytes")
        
        for f in event.stats:
            # Retrieve previous statistics for this specific port; default to current if first time
            prev_rx, prev_tx = self.stats[dpid].get(f.port_no, (f.rx_bytes, f.tx_bytes))
            
            # Logic to calculate bandwidth utilization:
            # Formula: ((Current_Bytes - Previous_Bytes) * 8 bits) / 5 seconds
            rx_bps = (f.rx_bytes - prev_rx) * 8 / 5
            tx_bps = (f.tx_bytes - prev_tx) * 8 / 5
            
            # Update the history with current byte counts for the next interval
            self.stats[dpid][f.port_no] = (f.rx_bytes, f.tx_bytes)
            
            # Display result (Functional Correctness - Performance Observation) [cite: 25, 39]
            print(f"{f.port_no:<4} | {rx_bps:<8.2f} | {tx_bps:<8.2f} | {f.rx_bytes + f.tx_bytes}")

def launch():
    """
    POX launch function to register and start the component.
    """
    core.registerNew(BandwidthMonitor)

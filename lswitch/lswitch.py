"""
NWEN 302 Lab 2
Learning Switch Implementation
Modify this file to implement the learning switch requirements.

Full name: William George Robert Burroughs
Student ID: 300467432

You will be implementing the functions init() and receive_frame(). You are free to
define/create new functions.

You can use the functions switch_table_insert() and switch_table_delete() to insert
entries to and delete entries from switch table, respectively. 

"""

import os
import logging
import struct
import time

# Consts
max_table_entries = 3
default_expiration_time = 30

# Data structs
switch_table = {} # MAC address -> (Device name, expiration_time)
expiration_times = {} # MAC address --> expiration_time (For speedy access)
device_names = []

def init():
    """
    This function will be called once by the main program during starup.
    Use this function to initialize any data structures. 
    """
    logging.debug('called init()')
    # Clear the caches
    global switch_table, expiration_times
    switch_table = {}
    expiration_times = {}



def receive_frame(src_mac_address, dest_mac_address, incoming_device_name):
    """
    This function will be called every time the switch receives a frame from
    any of its ports. 

    Arguments:
    src_mac_address: Source 48-bit MAC address.
    dest_mac_address: Destination 48-bit MAC address.
    incoming_device_name: name of the interface (e.g. eth0) that the frame was received.

    """
    logging.debug('called receive_frame()')
    logging.debug(switch_table)

    if len(switch_table) >= max_table_entries:
        oldest_mac = min(switch_table, key=lambda k: switch_table[k][1])
        print(oldest_mac)
        switch_table_delete(oldest_mac, switch_table[oldest_mac][0])
        del switch_table[oldest_mac]
        print("Deleteed Oldest Mac")


    current_time = time.time()

    # Update the source MAC address entry
    switch_table[src_mac_address] = (incoming_device_name, current_time + default_expiration_time)
    expiration_times[src_mac_address] = current_time + default_expiration_time
    switch_table_insert(src_mac_address, incoming_device_name)

    # Check if the destination MAC address exists in the switch table
    if dest_mac_address in switch_table:
        output_device, expiration_time = switch_table[dest_mac_address]

        # Check if destination is on the same segment
        if output_device == incoming_device_name:
            # Drop the frame
            return
        else:
            # Forward the frame on the indicated output interface
            switch_table[dest_mac_address] = (output_device, current_time + default_expiration_time)
            switch_table_delete(dest_mac_address, incoming_device_name)
            switch_table_insert(dest_mac_address, output_device)
    else:
        # Entry doesn't exist --> Flood all interfaces except for incoming
        for device in device_names:
            if device != incoming_device_name:
                switch_table_insert(dest_mac_address, device)

    # Clean up expired entries
    for mac_address, expiration_time in list(expiration_times.items()):
        if expiration_time <= current_time:
            switch_table_delete(mac_address, switch_table[mac_address][0])
            del switch_table[mac_address]
            del expiration_times[mac_address]



# Do not edit this function. This is provided for you to use.
def switch_table_insert(mac_address, device):
    """
    Insert an entry in the switch table.
    
    Arguments:
    mac_address: This should be a 48-bit MAC address.
    device Name of interface where the node with @mac_address is attached.
    """
    mac_str = '%.2x:%.2x:%.2x:%.2x:%.2x:%.2x' % struct.unpack("BBBBBB", mac_address)
    cmd = 'bridge fdb add %s dev %s master static via br0' % (mac_str, device)
    logging.debug('Invoking %s' % cmd)
    os.system(cmd)



# Do not edit this function. This is provided for you to use.
def switch_table_delete(mac_address, device):
    """
    Delete an entry in the switch table.
    
    Arguments:
    mac_address: MAC address. This should be a 48-bit MAC address.
    device: Name of interface where the node with @mac_address is attached.
    """
    mac_str = '%.2x:%.2x:%.2x:%.2x:%.2x:%.2x' % struct.unpack("BBBBBB", mac_address)
    cmd = 'bridge fdb del %s dev %s master static via br0' % (mac_str, device)
    logging.debug('Invoking %s' % cmd)
    os.system(cmd)



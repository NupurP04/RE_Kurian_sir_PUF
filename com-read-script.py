import serial
import pandas as pd
import os
import struct

def read_from_com_port(port, baudrate=9600, timeout=1, max_segments=10):
    HEADER = b'\x0D\x0A'
    FOOTER = b'\x00\xFF\xFF'
    output_file = "psoc_segments_hex.csv"

    # Create a new CSV file at the start
    create_new_csv(output_file)
    
    try:
        with serial.Serial(port, baudrate=baudrate, timeout=timeout) as ser:
            print(f"Connected to {port} at {baudrate} baud.")
            
            buffer = bytearray()
            segment_count = 0
            
            while segment_count < max_segments:
                chunk = ser.read(1024)
                if not chunk:
                    continue
                
                buffer.extend(chunk)
                
                while segment_count < max_segments:
                    header_index = buffer.find(HEADER)
                    if header_index == -1:
                        break
                    
                    footer_index = buffer.find(FOOTER, header_index)
                    if footer_index == -1:
                        break
                    
                    data = buffer[header_index + len(HEADER):footer_index]
                    segment_count += 1
                    
                    combined_values = []
                    for i in range(0, len(data), 2):
                        msb = data[i]
                        lsb = data[i + 1]
                        decimal_value = (msb << 8) | lsb  # Combine MSB and LSB
                        combined_values.append(decimal_value)
                    
                   # int_values = convert_bytes_to_uint16(data)
                   # int_values_str = ",".join(map(str, int_values))
                    
                    
                    #print(f"Data Segment {segment_count} Found: {data.hex()}")
                    print(f"Data Segment {segment_count} Found:", "\t".join(map(str, combined_values)))
                    
                    append_to_csv(data, output_file)
                    
                    buffer = buffer[footer_index + len(FOOTER):]
            
            print(f"\nReceived {segment_count} segments.")
            
    except serial.SerialException as e:
        print(f"Error: Could not open serial port {port} - {e}")
    except KeyboardInterrupt:
        print("Stopped by user.")
        return
    
#def convert_bytes_to_uint16(byte_data):
    #int_list = []
   # for i in range(0,len(byte_data), 2):
    #    if i+2 <= len(byte_data):
     #       int_value = struct.unpack('H', byte_data[i:i+2])[0]
     #       int_list.append(int_value)
  #  return int_list

def create_new_csv(filename):
    df = pd.DataFrame()
    df.to_csv(filename, index=False, header=False)
    print(f"New CSV file created: {filename}")

def append_to_csv(segment, filename):
    if len(segment) % 2 != 0:
        print("Warning: Odd number of bytes received. Data may be incomplete.")
        return
    
    combined_values = []
    for i in range(0, len(segment), 2):
        msb = segment[i]
        lsb = segment[i + 1]
        decimal_value = (msb << 8) | lsb  # Combine MSB and LSB
        combined_values.append(decimal_value)
    
    df = pd.DataFrame([combined_values])
    df.to_csv(filename, mode='a', index=False, header=False)
    print(f"Segment appended to {filename}")

if __name__ == "__main__":
    port_name = "COM14"
    baud_rate = 115200
    max_data_segments = 30
    
    read_from_com_port(port_name, baudrate=baud_rate, max_segments=max_data_segments)

import serial
import pandas as pd
import os

def read_from_com_port(port, baudrate=9600, timeout=1, max_segments=10):
    HEADER = b'\x0D\x0A'
    FOOTER = b'\x00\xFF\xFF'
    output_file = "psoc_segments.csv"

    # Create a new CSV file at the start
    create_new_csv(output_file)
    
    try:
        # Open the COM port
        with serial.Serial(port, baudrate=baudrate, timeout=timeout) as ser:
            print(f"Connected to {port} at {baudrate} baud.")
            
            buffer = bytearray()  # To store incoming bytes
            segment_count = 0     # Counter for segments
            
            while segment_count < max_segments:
                # Read a chunk of data
                chunk = ser.read(1024)
                if not chunk:
                    continue  # Skip if no data is received
                
                buffer.extend(chunk)
                
                # Search for HEADER and FOOTER in the buffer
                while segment_count < max_segments:
                    header_index = buffer.find(HEADER)
                    if header_index == -1:
                        break  # No header found; wait for more data
                    
                    footer_index = buffer.find(FOOTER, header_index)
                    if footer_index == -1:
                        break  # Footer not found yet; wait for more data
                    
                    # Extract data between HEADER and FOOTER
                    data = buffer[header_index + len(HEADER):footer_index]
                    segment_count += 1
                    
                    print(f"Data Segment {segment_count} Found: {data.hex()}")
                    
                    # Append the current segment to the CSV
                    append_to_csv(data, output_file)
                    
                    # Remove processed bytes from the buffer
                    buffer = buffer[footer_index + len(FOOTER):]
            
            print(f"\nReceived {segment_count} segments.")
            
    except serial.SerialException as e:
        print(f"Error: Could not open serial port {port} - {e}")
    except KeyboardInterrupt:
        print("Stopped by user.")
        return

def create_new_csv(filename):
    # Create an empty DataFrame and save it as a CSV file
    df = pd.DataFrame()
    df.to_csv(filename, index=False, header=False)
    print(f"New CSV file created: {filename}")

def append_to_csv(segment, filename):
    # Convert the segment into a DataFrame
    df = pd.DataFrame([list(segment)])
    
    # Append to the CSV file without headers
    df.to_csv(filename, mode='a', index=False, header=False)
    print(f"Segment appended to {filename}")

# Usage example
if __name__ == "__main__":
    port_name = "COM9"  # Replace with your COM port name
    baud_rate = 115200  # Replace with your baud rate
    max_data_segments = 50  # Set the number of segments to read before stopping
    
    read_from_com_port(port_name, baudrate=baud_rate, max_segments=max_data_segments)

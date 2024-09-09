from turck_py.FEN20_16DXP import FEN20_16DXP
import time

def main():
    # Create an instance of FEN20_16DXP
    controller = FEN20_16DXP(host="192.168.1.11", port=502)  # Replace with your device's IP and port

    try:
        # Start the connection
        controller.start_connection()
        print("Connected to the controller.")

        # Check if connected
        if controller.is_connected():
            print("Connection is active.")
            

        # Read all inputs
        inputs = controller.get_inputs()
        print("Current input states:", inputs)

        # Read a specific input (e.g., input 3)
        input_3_state = controller.get_input(3)
        print("Input 3 state:", input_3_state)

        # Get device status
        status = controller.get_status()
        print("Device status:", status)

        # Get diagnostics
        diag = controller.get_diagnostics()
        print("Diagnostics:", diag)

        # Get I/O diagnostics
        io_diag = controller.get_io_diagnostics()
        print("I/O Diagnostics:", io_diag)

        # Read all outputs
        outputs = controller.get_outputs()
        print("Current output states:", outputs)

        # Set multiple outputs
        new_outputs = {0: True, 1: False, 2: True}
        controller.set_outputs(new_outputs)
        print("Set multiple outputs.")

        # Read outputs again to verify changes
        outputs = controller.get_outputs()
        print("Updated output states:", outputs)

        # Set a specific output (e.g., output 5 to True)
        controller.set_output(5, True)
        print("Set output 5 to True.")

        # Read the specific output to verify
        output_5_state = controller.get_output(5)
        print("Output 5 state:", output_5_state)

        # Wait for a moment to allow changes to take effect
        time.sleep(1)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # The connection will be closed automatically when the object is deleted,
        # but you can also close it explicitly if needed:
        # controller.client.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()
from typing import Any, Dict, List, Tuple, Literal, Union
import time

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.client import ModbusTcpClient
from pymodbus import (
    ExceptionResponse,
    Framer,
    ModbusException,
    pymodbus_apply_logging_config,
)
import asyncio
import logging
from .utils import merge_registers, to_bits_list, from_bits_list, int32_to_uint16
from .definitions import *

logger = logging.getLogger(__name__)



class FEN20_16DXP:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.client = ModbusTcpClient(
            host,
            port=port,
            framer=Framer.SOCKET,
        )    
        
    def start_connection(self):
        try:
            self.client.connect()
        except Exception as e:
            logger.error(f"Error connecting to {self.host}:{self.port}")
            logger.error(e)
            raise e
        
        self.get_outputs()
        
    def __del__(self):
        self.client.close()
    
    def is_connected(self) -> bool:
        """Check if the client is connected."""
        return self.client.is_socket_open()
   
    def get_inputs(self) -> dict:
        """ Get the state of the inputs.

        Returns
        -------
        dict
            A dictionary with the state of the inputs.
            The key is the input number and the value is the state.
        """
        
        res = self.client.read_holding_registers(0, 1)
        bits = to_bits_list(res.registers[0])
        
        return {bit: value for bit, value in enumerate(bits)}
    
    def get_input(self, input: int) -> bool:
        """
        Get the state of a specific input.

        Parameters:
        -----------
        input : int
            The number of the input to check (0-15).

        Returns:
        --------
        bool
            The state of the specified input (True if active, False if inactive).
        """
        res = self.client.read_holding_registers(0, 1)
        bits = to_bits_list(res.registers[0])
        
        return bool(bits[input])
    
    def get_status(self):
        """ 
        Get the status of the device:
        FCE -> I/O-ASSISTANT Force Mode Active
        CFG -> I/O Configuration Error
        COM -> Communication error on internal module bus
        V1LOW -> Undervoltage V1 
        DiagWarn -> Diagnostic at least on 1 channel
        """
        res = self.client.read_holding_registers(0x0001, 1)
        bits = to_bits_list(res.registers[0])
        
        output = {
            "FCE": bits[14],
            "CFG": bits[11],
            "COM": bits[10],
            "V1LOW": bits[9],
            "DiagWarn": bits[0]
        }
        
    def get_diagnostics(self) -> bool:
        """ I/O diagnostic detected """
        res = self.client.read_holding_registers(0x0002, 1)
        bits = to_bits_list(res.registers[0])
        
        return bool(bits[0])
        
    def get_io_diagnostics(self) -> dict:
        """
        Get the diagnostics for each channel. -> Short-circuit output x 

        Returns:
        --------
        dict
            A dictionary where the keys are channel numbers (0-15) and the values are boolean states (True/False).
        """
        res = self.client.read_holding_registers(0xA000, 1)
        bits = to_bits_list(res.registers[0])[8]
        res = self.client.read_holding_registers(0xA001, 1)
        bits2 = to_bits_list(res.registers[0])[:8]
        
        bits = bits2 + bits
        
        return {bit: value for bit, value in enumerate(bits)}
    
    def get_outputs(self) -> dict:
        """
        Get the state of all outputs.

        Returns:
        --------
        dict
            A dictionary where the keys are output numbers (0-15) and the values are boolean states (True/False).
        """
        res = self.client.read_holding_registers(0x0800, 1)
        bits = to_bits_list(res.registers[0])
        
        return {bit: value for bit, value in enumerate(bits)}
    
    def get_output(self, output: int) -> bool:
        """
        Get the state of a specific output.

        Parameters:
        -----------
        output : int
            The number of the output to check (0-15).

        Returns:
        --------
        bool
            The state of the specified output (True if active, False if inactive).
        """
        res = self.client.read_holding_registers(0x0800, 1)
        bits = to_bits_list(res.registers[0])
        
        return bool(bits[output])
    
    def set_outputs(self, outputs: dict):
        """
        Set the state of multiple outputs simultaneously.

        Parameters:
        -----------
        outputs : dict
            A dictionary where the keys are output numbers (0-15) and the values are boolean states (True/False).
        """
        bits = [outputs.get(i, False) for i in range(16)]
        value = int.from_bytes(bytes(bits), 'little')
        
        self.client.write_register(0x0800, value)
        
    def set_output(self, output: int, value: bool):
        """
        Set the state of a specific output.

        Parameters:
        -----------
        output : int
            The number of the output to set (0-15).
        value : bool
            The desired state of the output (True to activate, False to deactivate).
        """
        res = self.client.read_holding_registers(0x0800, 1)
        bits = to_bits_list(res.registers[0])
        
        bits[output] = value
        write_value = from_bits_list(bits)
        
        self.client.write_register(0x0800, write_value)
from typing import Any, Dict, List

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus import (
    ExceptionResponse,
    Framer,
    ModbusException,
    pymodbus_apply_logging_config,
)
import logging
from .utils import decode_payload_to_bits, encode_bits_to_payload

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
        res = BinaryPayloadDecoder.fromRegisters(res.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)

        # Now, extract each bit from this register value.
        bits = decode_payload_to_bits(res)

        return bits
    
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
        res = self.get_inputs()
        return bool(res[input])
    
    def get_status(self) -> dict:
        """ 
        Get the status of the device:
        FCE -> I/O-ASSISTANT Force Mode Active
        CFG -> I/O Configuration Error
        COM -> Communication error on internal module bus
        V1LOW -> Undervoltage V1 
        DiagWarn -> Diagnostic at least on 1 channel
        """
        res = self.client.read_holding_registers(0x0001, 1)
        res = BinaryPayloadDecoder.fromRegisters(res.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
        bits = decode_payload_to_bits(res)
        
        output = {
            "FCE": bits[14],
            "CFG": bits[11],
            "COM": bits[10],
            "V1LOW": bits[9],
            "DiagWarn": bits[0]
        }
        return output
        
    def get_diagnostics(self) -> bool:
        """ I/O diagnostic detected """
        res = self.client.read_holding_registers(0x0002, 1)
        res = BinaryPayloadDecoder.fromRegisters(res.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
        bits = decode_payload_to_bits(res)
        
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
        res = BinaryPayloadDecoder.fromRegisters(res.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
        bits_ = decode_payload_to_bits(res) # 15-8
        bits = {bit: bits_[bit] for bit in range(8, 16)}
        
        res = self.client.read_holding_registers(0xA001, 1)
        res = BinaryPayloadDecoder.fromRegisters(res.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
        bits2_ = decode_payload_to_bits(res) # 7-0
        bits2 = {bit: bits2_[bit] for bit in range(8)}
                
        return {**bits, **bits2}
    
    def get_outputs(self) -> dict:
        """
        Get the state of all outputs.

        Returns:
        --------
        dict
            A dictionary where the keys are output numbers (0-15) and the values are boolean states (True/False).
        """
        res = self.client.read_holding_registers(0x0800, 1)
        res = BinaryPayloadDecoder.fromRegisters(res.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
        bits = decode_payload_to_bits(res)
        
        return bits
    
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
        res = self.get_outputs()
        
        return bool(res[output])
    
    def set_outputs(self, outputs: dict):
        """
        Set the state of multiple outputs simultaneously.

        Parameters:
        -----------
        outputs : dict
            A dictionary where the keys are output numbers (0-15) and the values are boolean states (True/False).
        """
        outputs_new = self.get_outputs()
        # Set the new values
        for output, value in outputs.items():
            outputs_new[output] = value
        
        builder = encode_bits_to_payload(outputs_new)
        
        self.client.write_registers(0x0800, values = builder.to_registers())
        
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
        res = BinaryPayloadDecoder.fromRegisters(res.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
        bits = decode_payload_to_bits(res)
        
        bits[output] = value
        builder = encode_bits_to_payload(bits)
        
        self.client.write_registers(0x0800, values = builder.to_registers())
        
        
        
        
        
        

class FEN20_16DXP_async:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = AsyncModbusTcpClient(
            host,
            port=port,
        )

    async def start_connection(self):
        try:
            await self.client.connect()
        except Exception as e:
            logger.error(f"Error connecting to {self.host}:{self.port}")
            logger.error(e)
            raise e
        
        await self.get_inputs()

    async def __aenter__(self):
        await self.start_connection()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    async def is_connected(self) -> bool:
        """Check if the client is connected."""
        return self.client.connected

    async def get_inputs(self) -> dict:
        res = await self.client.read_holding_registers(0, 1)
        res = BinaryPayloadDecoder.fromRegisters(res.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
        return decode_payload_to_bits(res)

    async def get_input(self, input: int) -> bool:
        res = await self.get_inputs()
        return bool(res[input])

    async def get_status(self) -> dict:
        res = await self.client.read_holding_registers(0x0001, 1)
        res = BinaryPayloadDecoder.fromRegisters(res.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
        bits = decode_payload_to_bits(res)
        
        return {
            "FCE": bits[14],
            "CFG": bits[11],
            "COM": bits[10],
            "V1LOW": bits[9],
            "DiagWarn": bits[0]
        }

    async def get_diagnostics(self) -> bool:
        res = await self.client.read_holding_registers(0x0002, 1)
        res = BinaryPayloadDecoder.fromRegisters(res.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
        bits = decode_payload_to_bits(res)
        
        return bool(bits[0])

    async def get_io_diagnostics(self) -> dict:
        res = await self.client.read_holding_registers(0xA000, 1)
        res = BinaryPayloadDecoder.fromRegisters(res.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
        bits_ = decode_payload_to_bits(res)
        bits = {bit: bits_[bit] for bit in range(8, 16)}
        
        res = await self.client.read_holding_registers(0xA001, 1)
        res = BinaryPayloadDecoder.fromRegisters(res.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
        bits2_ = decode_payload_to_bits(res)
        bits2 = {bit: bits2_[bit] for bit in range(8)}
                
        return {**bits, **bits2}

    async def get_outputs(self) -> dict:
        res = await self.client.read_holding_registers(0x0800, 1)
        res = BinaryPayloadDecoder.fromRegisters(res.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
        return decode_payload_to_bits(res)

    async def get_output(self, output: int) -> bool:
        res = await self.get_outputs()
        return bool(res[output])

    async def set_outputs(self, outputs: dict):
        outputs_new = await self.get_outputs()
        for output, value in outputs.items():
            outputs_new[output] = value
        
        builder = encode_bits_to_payload(outputs_new)
        await self.client.write_registers(0x0800, values=builder.to_registers())

    async def set_output(self, output: int, value: bool):
        res = await self.client.read_holding_registers(0x0800, 1)
        res = BinaryPayloadDecoder.fromRegisters(res.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
        bits = decode_payload_to_bits(res)
        
        bits[output] = value
        builder = encode_bits_to_payload(bits)
        
        await self.client.write_registers(0x0800, values=builder.to_registers())
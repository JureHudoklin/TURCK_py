from typing import Tuple
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder

def decode_payload_to_bits(payload: BinaryPayloadDecoder) -> dict:
    
    # Decode the first (and in this case, only) register.
    register_value = payload.decode_16bit_uint()

    # Now, extract each bit from this register value.
    bits = {bit: (register_value >> bit) & 1 for bit in range(16)}

    return bits

def encode_bits_to_payload(bits: dict) -> BinaryPayloadBuilder:
    builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)
    
    # Convert the bits to a single integer
    value = sum([int(bits[i]) << i for i in range(16)])
    
    builder.add_16bit_uint(value)
    
    return builder
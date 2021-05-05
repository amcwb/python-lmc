from .lmc import ExampleWriteDevice, ExtendedDeviceRuntime, Runtime
import sys


if __name__ == "__main__":
    if "--write-device" in sys.argv:
        rt = ExtendedDeviceRuntime(200, operand_bits=28)
        rt.devices.append(ExampleWriteDevice(sys.argv[2]))
    else:
        rt = Runtime(200, operand_bits=28)
    
    rt.load_into_memory(open(sys.argv[1], "r").read())
    rt.run()
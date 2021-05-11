from collections import namedtuple
from typing import Callable

class Runtime:
    _default_opcodes = [
        ("HLT", 0,  "_HLT"),
        ("ADD", 1,  "_ADD"),
        ("SUB", 2,  "_SUB"),
        ("STA", 3,  "_STA"),
        ("DAT", 4,  "_DAT"),
        ("LDA", 5,  "_LDA"),
        ("BRA", 6,  "_BRA"),
        ("BRZ", 7,  "_BRZ"),
        ("BRP", 8,  "_BRP"),
        ("OUT", 9,  "_OUT"),
        ("INP", 10, "_INP"),
    ]

    def _HLT(self, arg0):
        self.done = True
    
    def _ADD(self, arg0):
        self.acc += self.get_memory(arg0)

    def _SUB(self, arg0):
        self.acc -= self.get_memory(arg0)
    
    def _STA(self, arg0):
        self.memory[arg0] = self.acc
    
    def _DAT(self, arg0):
        pass

    def _LDA(self, arg0):
        self.acc = self.get_memory(arg0)
    
    def _BRA(self, arg0):
        self.ptr = arg0 - 1
    
    def _BRZ(self, arg0):
        if self.acc == 0:
            self.ptr = arg0 - 1
    
    def _BRP(self, arg0):
        if self.acc >= 0:
            self.ptr = arg0 - 1
    
    def _INP(self, arg0):
        text = None
        while True:
            try:
                text = input("-> ")
                self.acc = int(text)
                break
            except (TypeError, ValueError):
                pass

    def _OUT(self, arg0):
        print(chr(self.acc), end="")

    def __init__(self, memory_size: int, /, operand_bits: int = None, opcode_bits = 4, register_default: bool = True) -> None:
        self.acc = 0
        self.ptr = 0
        self.done = False
        self.memory = [0 for _ in range(memory_size)]

        self._opcode_bits = opcode_bits
        self._operand_bits = operand_bits or (2**8).bit_length() - opcode_bits
        
        self._opcodes = {}
        self._opfuncs = {}
        if register_default:
            for mnemonic, opcode, method_name in self.__class__._default_opcodes:
                self.register_mnemonic(mnemonic, opcode)
                
                method = getattr(self, method_name)
                if mnemonic not in self._opfuncs:
                    self.register_opcode_handler(opcode, method)

    def register_mnemonic(self, opname: str, opcode: int):
        self._opcodes[opname] = opcode

    def register_opcode_handler(self, opcode: int, function: Callable):
        self._opfuncs[opcode] = function

    def get_opcode(self, name: str):
        return self._opcodes[name]

    def get_memory(self, address: int):
        return self.memory[address]

    def get_current_instruction(self):
        return self.get_memory(self.ptr)

    def load_into_memory(self, file: str, start_index: int = 0):
        dat = []
        jumps = []
        lines = file.split("\n")
        mem_index = start_index

        first_run = []
        for line in lines:
            line = line.strip()
            data = [part for part in line.split() if part != ""]
            if len(data) == 1:
                first_run.append([None, self.get_opcode(data[0]), None, mem_index])
                mem_index += 1
            elif len(data) == 2:
                if data[0] in self._opcodes:
                    first_run.append([None, self.get_opcode(data[0]), data[1], mem_index])
                    mem_index += 1
                else:
                    if data[1] == "DAT":
                        dat.append((data[0], 0))
                    else:
                        first_run.append([data[0], self.get_opcode(data[1]), None, mem_index])
                        jumps.append((data[0], mem_index))
                        mem_index += 1
            elif len(data) == 3:
                if data[1] == "DAT":
                    dat.append((data[0], int(data[2])))
                else:
                    first_run.append([data[0], self.get_opcode(data[1]), data[2], mem_index])
                    jumps.append((data[0], mem_index))
                    mem_index += 1

        # Get DAT address        
        dat_allocated = {}
        for dat_name, dat_value in dat:
            dat_allocated[dat_name] = mem_index
            self.memory[mem_index] = dat_value
            mem_index += 1
        
        # Index jumps
        jumps_allocated = {}
        for name, mem_index in jumps:
            jumps_allocated[name] = mem_index

        # Compile
        for name, opcode, operand, mem_index in first_run:
            # Is word or text...
            if operand is None:
                operand = 0
            try:
                operand = int(operand)
            except (ValueError, TypeError):
                if operand in dat_allocated:
                    operand = dat_allocated[operand]
                elif operand in jumps_allocated:
                    operand = jumps_allocated[operand]
                else:
                    raise KeyError("Unknown value", operand)

            combined = (opcode << self._operand_bits) + operand
            self.memory[mem_index] = combined

    def run(self, ptr: int = 0):
        self.done = False
        self.ptr = ptr
        while not self.done:
            try:
                instruction = self.get_current_instruction()
                opcode = instruction >> self._operand_bits
                operand = instruction & ((1 << (self._operand_bits)) - 1)

                self._opfuncs[opcode](operand)
                self.ptr += 1
            except Exception as err:
                print(f"{opcode=}, {operand=}")
                print("catastrophic failure: {}".format(err))
                print("memory dump: {}".format(self.memory))
                return


class ExtendedDeviceRuntime(Runtime):
    _default_opcodes = [
        *Runtime._default_opcodes,
        ("WRT", 11, "_WRT")
    ]

    def _WRT(self, arg0):
        self.get_device(arg0).write(self.acc)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.devices = []
    
    def get_device(self, index: int):
        return self.devices[index]

class ExampleWriteDevice:
    def __init__(self, path: str) -> None:
        self.file = open(path, "wb+")
    
    def write(self, value: int):
        self.file.write(chr(value).encode("utf-8"))

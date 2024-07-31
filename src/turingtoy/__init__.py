from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Union
)

import poetry_version

__version__ = poetry_version.extract(source_file=__file__)

Instruction = Union[str, Dict[str, Optional[str]]]

class TMachine:
    def __init__(self, machine: Dict, band: str) -> None:
        self.initial = machine
        self.table = machine['table']
        self.band = list(band)
        self.position = 0
        self.state = machine['start state']
        self.history = []

    def read(self) -> str:
        return self.band[self.position]

    def write(self, val: str) -> None:
        self.band[self.position] = val

    def get_instruction(self) -> Instruction:
        if self.state in self.table:
            state_table = self.table[self.state]
            return state_table.get(self.read(), state_table.get(self.initial['blank'], {}))
        return {}

    def fill(self) -> None:
        if self.position >= len(self.band):
            self.band.append(self.initial['blank'])
        elif self.position < 0:
            self.band.insert(0, self.initial['blank'])
            self.position = 0

    def exec_instruction(self, instruction: Instruction) -> None:
        if isinstance(instruction, str):
            instruction = {instruction: None}

        self.record()

        for k, v in instruction.items():
            if k == 'L':
                self.position -= 1
                if v:
                    self.state = v
            elif k == 'R':
                self.position += 1
                if v:
                    self.state = v
            elif k == 'write' and v:
                self.write(v)
            elif self.read() == k:
                self.exec_instruction(v)

            self.fill()

    def record(self) -> None:
        self.history.append(
            {
                'state': self.state,
                'reading': self.read(),
                'position': self.position,
                'memory': ''.join(self.band),
                'transition': self.get_instruction(),
            }
        )

    def trim(self) -> None:
        while self.band and self.band[0] == self.initial['blank']:
            self.band.pop(0)
        while self.band and self.band[-1] == self.initial['blank']:
            self.band.pop()

def run_turing_machine(
    machine: Dict,
    input_: str,
    steps: Optional[int] = None,
) -> Tuple[str, List[Dict], bool]:
    
    tmachine = TMachine(machine, input_)
    i = 0
    while tmachine.state != 'done' and (steps is None or i < steps):
        instruction = tmachine.get_instruction()
        if not instruction:
            break
        tmachine.exec_instruction(instruction)
        i += 1

    tmachine.trim()
    return ''.join(tmachine.band), tmachine.history, tmachine.state == 'done'

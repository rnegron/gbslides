#!/usr/bin/env python
from pathlib import Path
import typing

MAX_ROWS = 18
MAX_COLS = 20
ASM_VALUES_PER_LINE = 10
DEFAULT_CHARACTER_TILE_NUM = 0


class ASCIIToMapASM:
    def __init__(self):
        self.tiles_mapping = {}
        self._setup_alphabetic_tiles()
        self._setup_other_tiles()

    def create_slides(self, directory="."):
        valid_files = self._slide_filenames(directory)
        if valid_files:
            print(f"Add the following to your ASM code:")

            for filename in valid_files:
                data = self.read_slide(filename)
                output_filename = Path(f"{str(filename).split('.')[0]}.inc".upper())

                self.store(data, output_filename)

                print(f'INCLUDE "{output_filename}"')

    # Make sure file is saved in ASCII/DOS mode (or don't use extended ASCII set/window frame characters)
    def read_slide(self, filepath: Path):
        if not filepath.exists():
            raise f"File {str(filepath)} not found"

        processed_lines = []
        count = 0
        with Path.open(filepath, "r") as file:
            processed_lines = [self._process_line(line) for line in file.readlines()]

        while len(processed_lines) < MAX_ROWS:
            processed_lines.append(self._process_line(" "))

        return processed_lines

    def store(self, contents=[], filename="map_data.inc", section_postfix="_DATA"):
        section_name = f"{Path(filename).suffix}{section_postfix}"

        with Path.open(filename, "w") as file:
            file.write(self._asm_data(contents, section_name))

    def _slide_filenames(self, directory="."):
        return [
            file for file in Path(directory).iterdir() if Path(file).suffix == ".txt"
        ]

    def _asm_data(self, contents, section_name):
        asm_data = f"{section_name}::\n"
        i = 0
        has_more = True

        while has_more:
            chunk = contents[i:ASM_VALUES_PER_LINE]
            i += len(chunk)
            has_more = len(chunk) > i

            asm_data += f"{self._get_asm_line(chunk)}\n"

        return asm_data

    def _get_asm_line(self, hex_values):
        return f"DB {'.'.join([value.upper() for value in hex_values])}"

    def _process_line(self, line, linenum=1):
        if len(line) > MAX_COLS:
            raise f"Line {linenum} exceeds maximum column size ({MAX_COLS})"

        processed_line = [self._process_character(char) for char in line]

        while len(processed_line) < MAX_COLS:
            processed_line.append(self._process_character(" "))

        return processed_line

    def _process_character(self, char):
        output_char = self.tiles_mapping.get(
            char.upper().encode("ASCII"), DEFAULT_CHARACTER_TILE_NUM
        )

        char = (
            self._window_char(char)
            if output_char == DEFAULT_CHARACTER_TILE_NUM
            else output_char
        )
        return f"{char}02x"

    def _window_char(self, char):
        return {179: 70, 196: 71, 218: 72, 191: 73, 217: 74, 192: 75}.get(
            ord(char), DEFAULT_CHARACTER_TILE_NUM
        )

    def _setup_alphabetic_tiles(self):
        for i in range(26):
            self.tiles_mapping[chr(i + 65).encode("ascii")] = i + 1

        for i in range(10):
            self.tiles_mapping[chr(i + 48).encode("ascii")] = i + 36

    def _setup_other_tiles(self):
        self.tiles_mapping.update(
            {
                ".": 27,
                ",": 28,
                ":": 29,
                ";": 30,
                "!": 31,
                "?": 32,
                "-": 33,
                "(": 58,
                ")": 59,
                "[": 60,
                "]": 61,
                "+": 62,
                "=": 63,
                "&": 64,
                "$": 65,
                "'": 66,
                '"': 67,
                "/": 68,
                "|": 69,
            }
        )


if __name__ == "__main__":
    generator = ASCIIToMapASM().create_slides("slides")

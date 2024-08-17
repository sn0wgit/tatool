import metassigner
import compiler
import os
from InquirerPy import inquirer
from InquirerPy.validator import PathValidator

MODES = ["Metadata assigner", "Compile", "EXIT"]
LANGUAGES = ["en", "ru"]
ARCHIVE_PATH = inquirer.filepath( # type: ignore
    message="Enter path to archive:",
    default="./archive",
    validate=PathValidator(is_dir=True, message="Input is not a directory"),
    only_directories=True,
    filter = lambda result: os.path.abspath(result)
).execute()

mode = ""

while mode != MODES[-1]:
    mode = inquirer.select( # type: ignore
        message="Select mode\n",
        choices=MODES,
    ).execute()

    if mode == MODES[0]:
        metassigner.main(LANGUAGES, ARCHIVE_PATH)

    elif mode == MODES[1]:
        compiler.main(LANGUAGES, ARCHIVE_PATH)
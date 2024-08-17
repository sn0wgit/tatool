import metassigner
import compiler
from InquirerPy import inquirer

MODES = ["Metadata assigner", "Compile", "EXIT"]
LANGUAGES = ["en", "ru"]
mode = ""

while mode != MODES[-1]:
    mode = inquirer.select( # type: ignore
        message="== Select mode ==\n",
        choices=MODES,
    ).execute()

    if mode == MODES[0]:
        metassigner.main(LANGUAGES)

    elif mode == MODES[1]:
        compiler.main(LANGUAGES)
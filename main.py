import metassigner
from InquirerPy import inquirer

MODES = ["Metadata assigner", "EXIT"]
LANGUAGES = ["en", "ru"]
mode = ""

while mode != MODES[-1]:
    mode = inquirer.select( # type: ignore
        message="== Select mode ==\n",
        choices=MODES,
    ).execute()

    if mode == MODES[0]:
        metassigner.main(LANGUAGES)
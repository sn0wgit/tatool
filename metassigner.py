import os
import json
from os.path import join
from os.path import isdir
from os.path import isfile
from InquirerPy import inquirer

READ_FILE:str = 'r'
EXPLORER_TYPES = ['explorer.variation', 'explorer.item', 'explorer.folder', 'explorer.jpg', 'explorer.png', 'explorer.svg', 'explorer.a3d', 'explorer.3ds']
DIR_ACTIONS = ["Open folder", "Update metadata"]

def update(entry_path:str, entry_name:str, LANGUAGES:list[str]) -> bool:
    """Updates selected entry metadata. Returns if update is success"""

    metadata = {}
    if os.access(entry_path+".meta", os.R_OK):
        metafile = open(entry_path+".meta", READ_FILE)
        print("File already exists! File content:\n", metafile.read())
        metafile.close()

    entry_type = inquirer.select( # type: ignore
        message="Select entry type\n",
        choices=EXPLORER_TYPES,
    ).execute()
    metadata.update({"type": entry_type})

    unique_name = inquirer.text( # type: ignore
        message="Input unique name (for translations)\nInput:",
        default=entry_name.lower()
    ).execute()
    metadata.update({"namei18n": unique_name})

    for language in LANGUAGES:
        print(f"== Current language: {language} ==")

        name_in_current_language = inquirer.text(message="= Input name =\nInput:").execute() # type: ignore
        metadata.update({str(language+"Name"): name_in_current_language})

        desc_in_current_language = inquirer.text(message="= Input description =\nInput:").execute() # type: ignore
        metadata.update({str(language+"Desc"): desc_in_current_language})
    
    metadata.update({"targetName": entry_name})

    if isdir(entry_path):
        legal_subentries = [entry for entry in os.listdir(entry_path) if isfile(join(entry_path, entry)) and (not (entry.endswith(".meta")) or not (entry.endswith(".meta.json")))]
        preview_selection = inquirer.select( # type: ignore
            message="Select entry type\n",
            choices=["NO PREVIEW"]+legal_subentries,
        ).execute()
        preview_value:bool|str = False if (preview_selection == "NO PREVIEW") else preview_selection
        metadata.update({"preview": False if (preview_value == False) else f"./{entry_name}/{preview_value}"})

    elif entry_type in ['explorer.jpg', 'explorer.png', 'explorer.svg']:
        metadata.update({"preview": f"./{entry_name}"})

    else:
        metadata.update({"preview": False})

    metadata.update({"url": "./"+entry_name+"/"})

    write_agreement = inquirer.confirm(message="Confirm?").execute() # type: ignore

    if write_agreement:
        json.dump(metadata, metafile, indent=2, ensure_ascii=False)
        metafile.close()
        
        print(f'"{entry_name}.meta" created!')
        return True

    else: 
        metafile.close()
        print("Denied by user!")
        return False

def update_iterator(ENTRY_SELECTED:str, ENTRY_SELECTED_NAME:str, LANGUAGES:list[str]) -> bool:

    update_current_entry_again:bool = True

    while update_current_entry_again:
        update_iteration = update(ENTRY_SELECTED, ENTRY_SELECTED_NAME, LANGUAGES)

        if update_iteration:
            update_current_entry_again = False

            return inquirer.confirm(message="Continue in this mode?").execute() # type: ignore

        else:
            update_current_entry_again = inquirer.confirm(message="Try again?").execute() # type: ignore

            if not update_current_entry_again:
                update_current_entry_again = False
                return inquirer.confirm(message="Continue in this mode?").execute() # type: ignore

def selection(LANGUAGES:list[str], current_path:str) -> None:

    continue_selection:bool = True

    while continue_selection:

        entry_selected = inquirer.filepath( # type: ignore
            message="Select entry\n",
            default=current_path,
            validate=lambda path: os.path.abspath(path).startswith(current_path+"/") and not path.endswith(".meta") and not path.endswith(".meta.json"),
            invalid_message="Error: selection is outside of archive or is metafile",
            filter=lambda result: os.path.abspath(result),
        ).execute()
        
        entry_selected_name = os.path.basename(entry_selected)
        
        if isdir(entry_selected):
            action_select = inquirer.select( # type: ignore
                message="Select action\n",
                choices=DIR_ACTIONS,
            ).execute()
            if action_select == DIR_ACTIONS[0]:
                current_path = entry_selected
            elif action_select == DIR_ACTIONS[1]:
                continue_selection = update_iterator(entry_selected, entry_selected_name, LANGUAGES)
        else: 
            continue_selection = update_iterator(entry_selected, entry_selected_name, LANGUAGES)

def main(LANGUAGES:list[str], ARCHIVE_PATH:str):
    selection(LANGUAGES, ARCHIVE_PATH)

if __name__ == "__main__":
    print('Use "main.py"!')
import os
from os.path import join
from os.path import isdir
from os.path import isfile
from InquirerPy import inquirer

CREATE_FILE:str = 'w'
EXPLORER_TYPES = ['explorer.variation', 'explorer.item', 'explorer.jpg', 'explorer.png', 'explorer.svg', 'explorer.a3d', 'explorer.3ds']
DIR_ACTIONS = ["Open folder", "Update metadata"]

def update(entry_path:str, entry_name:str, languages:list[str]) -> None:
    """Updates selected entry metadata"""
    metadata = {}
    
    entry_type = inquirer.select( # type: ignore
        message="== Select entry type ==\n",
        choices=EXPLORER_TYPES,
    ).execute()
    metadata.update({"type": entry_type})

    unique_name = inquirer.text(message="== Input unique name (for translations) ==\nInput:").execute() # type: ignore
    metadata.update({"namei18n": unique_name})

    for language in languages:
        print(f"== Current language: {language} ==")

        name_in_current_language = inquirer.text(message="= Input name =\nInput:").execute() # type: ignore
        metadata.update({str(language+"Name"): name_in_current_language})

        desc_in_current_language = inquirer.text(message="= Input description =\nInput:").execute() # type: ignore
        metadata.update({str(language+"Desc"): desc_in_current_language})
    
    metadata.update({"targetName": entry_name})

    if isdir(entry_path):
        print("== Select preview ==\n0: NO PREVIEW")
        legal_subentries = [entry for entry in os.listdir(entry_path) if isfile(join(entry_path, entry)) and (not (entry.endswith(".meta")) or not (entry.endswith(".meta.json")))]
        preview_selection = inquirer.select( # type: ignore
            message="== Select entry type ==\n",
            choices=["NO PREVIEW"]+legal_subentries,
        ).execute()
        preview_value:bool|str = False if (preview_selection == "NO PREVIEW") else preview_selection
        metadata.update({"preview": False if (preview_value == False) else f"./{entry_name}/{preview_value}"})

    elif entry_type in ['explorer.jpg', 'explorer.png', 'explorer.svg']:
        metadata.update({"preview": f"./{entry_name}"})

    else:
        metadata.update({"preview": False})

    metadata.update({"url": "./"+entry_name+"/"})

    metafile = open(entry_path+".meta", CREATE_FILE)
    metafile.write(str(metadata).replace("'", '"').replace("False", 'false').replace("True", 'true'))
    metafile.close()
    
    print(f'"{entry_name}.meta" created!')

def selection(current_directory:str, languages:list[str]) -> None:
    origin_entries = sorted([c for c in os.listdir(current_directory) if (not (c.endswith(".meta") or c.endswith(".meta") or c.endswith(".meta.json")))])
    entry_selected = inquirer.select( # type: ignore
        message="== Select entry ==\n",
        choices=["GO UP"]+origin_entries,
    ).execute()
    entry_selected_path = join(current_directory, entry_selected)
    if isdir(entry_selected_path):
        action_select = inquirer.select( # type: ignore
            message="== Select action ==\n",
            choices=DIR_ACTIONS,
        ).execute()
        if action_select == DIR_ACTIONS[0]:
            selection(entry_selected_path, languages)
        elif action_select == DIR_ACTIONS[1]:
            update(entry_selected_path, entry_selected, languages)
    else: 
        update(entry_selected_path, entry_selected, languages)

def main(languages:list[str]):
    selection(join(os.getcwd(), "GDrive original sample", "items"), languages)
# TATool

Proprietary software, made for _Tanki Online #Archive_ team. 

## Dependencies

This program using [PyQt6](https://pypi.org/project/PyQt6/). To install all dependecies, run this command in terminal:

```sh
pip install PyQt6
```

## Using guide

User selects root directory and program starts to index all directories and files, that does not end with `.meta` or `.meta.json`. Program automatically suggests data types and unique data names. After you saved all metadata, than you can compile them by single button click on second program tab.

### Metadata Editor

Metadata Editor lets you edit metadata for any data you choose (_that does not end with `.meta` or `.meta.json`_). You input its name for further _i18n_ translations, its own translations, such as name and description (only English and Russian are supported now), and selects entry type from the data type list. Program overwrites `${original_file_or_directory_name}.meta` file in parent directory and will use it at Compiler tab.

### Compiler

Compiler creates `*.meta.json` files, which are based on `.meta` files, created by Metadata Editor. It goes through all directories, reading `.meta` files, processes them and overwrites `arrangement.meta.json` and `${language_code}.meta.json` files if Compiler had found `.meta` files in this directory.

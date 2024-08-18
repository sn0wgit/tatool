# _TO#A_ archive compiler

Proprietary software, made for _Tanki Online #Archive_ team. It takes specially configured archive and returns its compilation for the _TO#A_ register.

## Needed archive structure

Archive can contain any files. It is recommended to not use custom files with extension `.meta` as program uses them for archive compilation.

## Dependencies

This program using [InquirerPy](http://inquirerpy.readthedocs.io/). To install all dependecies, run this command in terminal:

```sh
pip3 install InquirerPy
```

## Using guide

Programm is running in terminal. It has two modes:

* Metadata assigner
* Compiler

Before mode selection you choose target archive folder.

### Metadata assigner

Metadata assginer... assigns metadata you choose for any entry (it could be file or directory). You input its name for further _i18n_ translations, its own translations, such as name and description (descriptions are not currently using anywhere) for English and Russian, languages and entry type. Program overwrites `.meta` file and using it in Compiler mode.

### Compiler

Compiler creates `.meta.json` files, which are based on `.meta` files, created by Metadata Assigner. It goes through all directories, reading `.meta` files, processes them and overwrites `arrangement.meta.json`, `en.meta.json` and `ru.meta.json` files if Compiler had found `.meta` files in this directory.

## Test on IDX

<a href="https://idx.google.com/import?url=https://github.com/sn0wgit/toa-compiler">
    <picture>
        <source media="(prefers-color-scheme: dark)" srcset="https://cdn.idx.dev/btn/open_dark_32@2x.png">
        <source media="(prefers-color-scheme: light)" srcset="https://cdn.idx.dev/btn/open_light_32@2x.png">
        <img height="32" alt="Open in IDX" src="https://cdn.idx.dev/btn/open_purple_32@2x.png">
    </picture>
</a>

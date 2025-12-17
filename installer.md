# Installer for linux
## Test in ubuntu 24.04
```shell
pyinstaller  main.py \
--onedir   \
--noconsole  \
--add-data "config.json:."  \
--hidden-import=pyodbc
```
---
# Installer for windows x64
## Test windows 10
```shell
pyinstaller  main.py \
--onedir   \
--noconsole  \
--add-data "config.json:."  \
--hidden-import=pyodbc
```
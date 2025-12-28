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

https://www.spice-space.org/download/windows/spice-guest-tools/spice-guest-tools-latest.exe

git clone https://github.com/crcarreno/PulseConnector.git
cd PulseConnector

python -m venv .venv .venv\Scripts\activate

pip install -r requirements.txt

python main.py

pyinstaller main.py ^
  --onefile ^
  --hidden-import=pyodbc ^
  --hidden-import=sqlalchemy.dialects.mssql.pyodbc

```
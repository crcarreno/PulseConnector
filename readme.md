# PulseConnector (Community)

![PulseConnector USE](images/pulseconnector1.png)

**PulseConnector** is a local database connector with a Python GUI that allows exposing your data via an OData service and connecting remotely from a VPS using SSH tunnels (forward and reverse).  

This project enables querying your local databases from a remote server securely, without opening public ports, with support for multiple database dialects (MySQL, PostgreSQL, SQL Server).

---

## Features

- **GUI (PySide6)** for:
  - Editing `config.json` visually in a key-value tree format.
  - Selecting the active database dialect using a ComboBox.
  - Viewing and dynamically updating connection parameters.

- **Local Python connector**:
  - Supports **SSH forward and reverse tunnels**.
  - Allows the VPS to query your **local OData service** through a reverse tunnel.
  - Automatically builds the connection string based on the selected dialect.

- **Embedded OData service** to expose local database data in a standard way.

---


## Configuration (`config.json`)

Example configuration file:

```json
{
  "ssh": {
    "enabled": true,
    "mode": "reverse",
    "vps_host": "0.0.0.0",
    "vps_user": "user",
    "vps_pass": "root",
    "remote_db_port": 3306,
    "local_bind_port": 5001
  },
  "db_mysql": {
    "dialect": "mysql",
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "pass": "root",
    "database": "northwind"
  },
  "db_postgres": {
    "dialect": "postgres",
    "host": "127.0.0.1",
    "port": 5432,
    "user": "postgres",
    "pass": "postgres",
    "database": "postgres"
  },
  "db_mssql": {
    "dialect": "mssql",
    "host": "127.0.0.1",
    "port": 1433,
    "user": "sa",
    "pass": "password",
    "database": "northwind"
  }
}
```
---
# Deployment

## Install dependencies

- pip install PySide6 sshtunnel sqlalchemy pymysql psycopg2 pyodbc
---

## Run the GUI
```
from gui_main import run_gui  # your main.py with MainWindow
import json

with open("config.json") as f:
    cfg = json.load(f)

run_gui(cfg)
```
---

## In the GUI

- Edit connection parameters visually.
- Select the active database dialect in the ComboBox.
- Start the SSH tunnel (forward or reverse, according to config).

First view
![PulseConnector USE](images/screenshots/capture2.png)

---

## Main Components

- JsonEditor: Visual editor of config.json with an expanded, editable tree structure.
- SshTunnelManager: Handles SSH forward and reverse tunnels from Python.
- build_connection_string(cfg): Builds the connection string according to the selected dialect.
- PySide6 GUI with dynamic ComboBox populated from db_* sections in JSON.
- Embedded OData service ready to expose your local database data.

---

## Security
- All tunnels use encrypted SSH connections.
- No need to open public ports on your local network.
- The reverse tunnel allows only the authorized VPS to access your OData.
---
## Possible Extensions

- Automatic reconnection if the SSH tunnel drops.
- Automatic validation of parameters according to the selected dialect.
- “Test Connection” button for each database.
- Activity logs and OData query logging.

---
# Use

## Test
http://localhost:4545/status

## Mysql
http://localhost:4545/odata/mi_tabla?$select=id,name&$filter=age gt 30&$top=10
http://localhost:4545/odata/customers?$select=id,company&$filter=city%20gt%20Miami

## Postgresql
http://localhost:4545/odata/customers?$select=customer_id,company_name&$filter=city%20gt%20Miami

![PulseConnector USE](images/screenshots/capture1.png)
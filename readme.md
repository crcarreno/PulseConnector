# PulseConnector

![PulseConnector USE](images/pulseconnector1.png)

**PulseConnector** PulseConnector is a lightweight Python database connector that transforms your data into a ready-to-use OData API in minutes.


---

## Website: https://pulseconnector.ecuarobot.com

# Features

![capture2.png](images/screenshots/capture2.png)

- Fast access to MSSQL, MySQL/MariaDB, PotgreSQL and other databases without writing additional code.

- Complete management from a modern GUI in PySide6.

- Built-in SSH tunnels for secure connectivity to remote databases.

- Lightweight backend with Waitress, compatible with Windows and Linux.

- Ideal for developers and administrators who need to expose data securely and quickly.


- ## [Benchmark](docs/benchmark.md)

- ## [Installer](docs/installer.md)

---

# General architecture

![arquitecture.png](images/general_architecture.png)


---

# Network architecture

![arquitecture.png](images/network_architecture.png)

---
# New Features

*December 22, 2025*
- Replaced ORM-based persistence with a custom SQL-based Data Access Layer to improve concurrency and performance
- Implemented native DB drivers with explicit pooling for high-load API scenarios
- Removed ORM overhead to achieve predictable latency under concurrent load

*December 19, 2025*
- Basic Authentication Support
- Stateless API Architecture
- JWT-Based Authentication (Bearer Tokens)
- Token Expiration Handling
- Secure Token Signing
- Protected OData Endpoints
- Centralized Request Logging

*December 18, 2025*
- Integrated HTTPS Proxy for remote connections
- Incorporate SSL / TLS Certificate

*December 16, 2025*
- Compatibility with linux/windows x64
- Package installation with embed libraries

*December 13, 2025*
- Waitress server implementation
- Independent server thread
- Thread control
- High-demand feature configuration for threads
- High-demand feature configuration for odata

*November 29, 2025*
- ODATA allows data entry via JSON
- ODATA allows partial or complete updates of records via JSON.
- The configuration has a separate screen.

---
## Configuration (`config.json`)

Example configuration file:

```json
{
    "ssh": {
        "enabled": true,
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
        "pass": "admin.1234",
        "database": "dbTest"
    },
    "server": {
        "host": "127.0.0.1",
        "port": 5000,
        "protocol": "http",
        "threads": 8,
        "connection_limit": 100,
        "backlog": 512,
        "channel_timeout": 60,
        "cleanup_interval": 30
    },
    "odata": {
        "pool_size": 20,
        "max_overflow": 10,
        "pool_timeout": 10,
        "pool_recycle": 1800,
        "pool_pre_ping": true
    },
    "active_dialect": "mssql"
}
```
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

## Test local server

- local: http://localhost:4545/status
- remote: https://localhost:5000/status

---


# Instructions for making queries using ODATA

## Select

**/odatab**: the web route

**/customer**: the table

**?**: add parameter in url

**$select**: statement that emulates a select

**id, company**: attributes of table

**Example:** 
```text
https://localhost:5000/odata/customers?$select=id,company
```
## $filters

**eq**: atributes c, v: c == v

**ne**: atributes c, v:  c != v,

**gt**: atributes c, v:  c > v,

**lt**: atributes c, v:  c < v,

**ge**: atributes c, v:  c >= v,

**le**: atributes c, v:  c <= v,

**like**: atributes c, v:  c.like(v)

**Test example:** 
```text
/data/customers?$select=id,company
        
/odata/products?$filter=precio gt 10

/odata/users?$filter=activo eq true

/odata/orders?$select=id,ship_name&$filter=ship_name like 'Karen%'
```

## Top
```text
/odata/Logs?$top=50
```

## Order by
```text
/odata/products?$orderby=precio desc

/odata/users?$orderby=nombre asc
```
## Combinations
```text
/odata/Productos?$select=id,nombre,precio&$filter=precio gt 20&$orderby=precio desc&$top=10
```
![PulseConnector USE](images/screenshots/capture1.png)

---
# Inserts

## Test using postman

![capture3.png](images/screenshots/capture3.png)


# Update

## Total (PUT) - Test using postman

![capture4.png](images/screenshots/capture4.png)


## Partial (PATCH) - Test using postman

![capture5.png](images/screenshots/capture5.png)

---

# Server configuration

## Normal

```json
{
    "host": "0.0.0.0",
    "port": 5000,
    "threads": 8,
    "connection_limit": 100,
    "backlog": 512,
    "channel_timeout": 60,
    "cleanup_interval": 30
}
```

## High

```json
{
  "host": "0.0.0.0",
  "port": 5000,
  "threads": 32,
  "connection_limit": 1000,
  "backlog": 2048,
  "channel_timeout": 120,
  "cleanup_interval": 30
}
```

---

## OData configuration

## Normal

```json
    {
      "pool_size":20,
      "max_overflow":10,
      "pool_timeout":10,
      "pool_recycle":1800,
      "pool_pre_ping":"True"
    }
```

## High

```json
    {
      "pool_size":50,
      "max_overflow":100,
      "pool_timeout":30,
      "pool_recycle":1800,
      "pool_pre_ping":"True"
    }
```


# License

This project is free for non-commercial use.

Commercial use requires prior written authorization from the author.
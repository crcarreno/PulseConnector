## Create image from docker file of SQL Server 2022
```shell
sudo docker build -t sqlserver2022 .
```

## Up image
```shell
sudo docker run -d \
  --name sql2022 \
  -e "ACCEPT_EULA=Y" \
  -e "MSSQL_SA_PASSWORD=admin.1234" \
  -p 1433:1433 \
  sqlserver2022-custom
```

## Verify images
```shell
sudo docker ps -a
```

## Start image
```shell
sudo docker start sql2022
```

## Instalar ODBC Drivers for SQL Server in your ubuntu
```shell
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

curl https://packages.microsoft.com/config/ubuntu/24.04/prod.list \
  | tee /etc/apt/sources.list.d/mssql-release.list

sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev
```
# Imagen base oficial de SQL Server 2022 para Linux (Ubuntu 20.04)
FROM mcr.microsoft.com/mssql/server:2022-latest

# Variables de entorno requeridas por SQL Server
ENV ACCEPT_EULA=Y
ENV MSSQL_PID=Developer
ENV MSSQL_SA_PASSWORD=admin.1234

# Exponer el puerto del SQL Server
EXPOSE 1433

# Directorio por defecto
WORKDIR /var/opt/mssql

# Comando de inicio (ya viene preconfigurado en la imagen base)
CMD ["/opt/mssql/bin/sqlservr"]


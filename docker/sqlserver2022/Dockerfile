# Imagen base oficial de SQL Server 2022 para Linux (Ubuntu 20.04)
FROM mcr.microsoft.com/mssql/server:2022-latest

ENV ACCEPT_EULA=Y
ENV MSSQL_PID=Developer
ENV MSSQL_SA_PASSWORD=admin.1234

EXPOSE 1433

WORKDIR /var/opt/mssql

CMD ["/opt/mssql/bin/sqlservr"]


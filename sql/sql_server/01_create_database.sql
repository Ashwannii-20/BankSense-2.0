/* BankSense 2.0 - SQL Server setup
   Run this file in SSMS while connected to the target SQL Server instance. */
IF DB_ID(N'BankSense') IS NULL
BEGIN
    CREATE DATABASE [BankSense];
END;
GO

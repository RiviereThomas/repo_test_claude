import pyodbc
import sqlalchemy as sqla
from sqlalchemy import text
import os
import urllib
import pandas as pd


# fonction qui permet la connection à notre DWH
# return engine qu'on peut par la suite appeler directement dans un read sql ou via un cursor
def connect_dwh():
    drivers = pyodbc.drivers()
    if 'ODBC Driver 17 for SQL Server' in drivers:
        connect_string = r'DRIVER={ODBC Driver 17 for SQL Server};SERVER=SQLDW.mandarine.lan;DATABASE=MandarineGestion_Datawarehouse;Trusted_Connection=Yes'
    elif 'ODBC Driver 13 for SQL Server' in drivers:
        connect_string = r'DRIVER={ODBC Driver 13 for SQL Server};SERVER=SQLDW.mandarine.lan;DATABASE=MandarineGestion_Datawarehouse;Trusted_Connection=Yes'
    params = urllib.parse.quote_plus(connect_string)
    engine = sqla.create_engine('mssql+pyodbc:///?odbc_connect={}'.format(params))
    cursor = engine.connect()
    print(test_connection(cursor))
    # print('BASE PROD')
    return cursor


def connect_dwh_test():
    drivers = pyodbc.drivers()

    if 'ODBC Driver 17 for SQL Server' in drivers:
        connect_string = r'DRIVER={ODBC Driver 17 for SQL Server};SERVER=SQLDW;DATABASE=Test_MandarineGestion_Datawarehouse;Trusted_Connection=Yes'
    elif 'ODBC Driver 13 for SQL Server' in drivers:
        connect_string = r'DRIVER={ODBC Driver 13 for SQL Server};SERVER=SQLDW;DATABASE=Test_MandarineGestion_Datawarehouse;Trusted_Connection=Yes'
    params = urllib.parse.quote_plus(connect_string)
    engine = sqla.create_engine('mssql+pyodbc:///?odbc_connect={}'.format(params))
    cursor = engine.connect()
    # print(test_connection(cursor))
    # print('BASE TEST')
    return cursor


def connect_engine():
    drivers = pyodbc.drivers()
    if 'ODBC Driver 17 for SQL Server' in drivers:
        connect_string = r'DRIVER={ODBC Driver 17 for SQL Server};SERVER=SQLDW;DATABASE=MandarineGestion_Datawarehouse;Trusted_Connection=Yes'
    elif 'ODBC Driver 13 for SQL Server' in drivers:
        connect_string = r'DRIVER={ODBC Driver 13 for SQL Server};SERVER=SQLDW;DATABASE=MandarineGestion_Datawarehouse;Trusted_Connection=Yes'
    params = urllib.parse.quote_plus(connect_string)
    engine = sqla.create_engine('mssql+pyodbc:///?odbc_connect={}'.format(params))
    return engine


def read_sql_dataframe(query: str, engine: sqla.engine.Engine) -> pd.DataFrame:
    with engine.connect() as conn:
        return pd.read_sql_query(query, conn.connection)


def test_connection(cursor):
    try:
        cursor.execute(text("SELECT * FROM ref_funds"))
    except BaseException:
        return 'Connection KO'
    return 'Connection OK'


def update_table(connection, table_name, set_values, where_clause):
    try:
        set_clause = ", ".join([f"{column} = :{column}" for column in set_values.keys()])
        # Construction de la partie WHERE de la requête
        where_conditions = " AND ".join([f"{column} = :{column}" for column in where_clause.keys()])
        # Création de la requête SQL
        sql_query = text(f"UPDATE {table_name} SET {set_clause} WHERE {where_conditions}")
        # Fusion des valeurs des parties SET et WHERE dans un dictionnaire
        params = {**set_values, **where_clause}
        connection.execute(sql_query, params)
        connection.connection.commit()
        print(f"Lignes mises à jour avec succès :", params)
    except Exception as err:
        print(f"Erreur: {err}")


def insert_into_table(connection, table_name, insert_values):
    try:
        # Construction des colonnes et des valeurs de la requête
        columns = ", ".join(insert_values.keys())
        placeholders = ", ".join([f":{key}" for key in insert_values.keys()])

        # Création de la requête SQL
        sql_query = text(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})")
        # Exécution de la requête
        connection.execute(sql_query, insert_values)
        # Validation des changements
        connection.connection.commit()
        print(f"Données insérées avec succès.")
    except Exception as err:
        print(f"Erreur: {err}")


def connection_sustain():
    from sustainalytics.api import API
    client_id = '879eb58d-0200-4c23-a07e-19492ea80717'
    client_secret_key = 'CN.Ga*?w@qp}HZN>1.GX.@dgS;WNDm_U'
    con = API(client_id=client_id, client_secretkey=client_secret_key)
    return con


if __name__ == '__main__':
    engine = connect_engine()
    with engine.begin() as conn:
        conn.execute(text("insert into tmp_test (ISIN) values ('test2')"))

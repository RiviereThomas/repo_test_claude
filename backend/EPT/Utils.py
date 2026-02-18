import calendar
import warnings
import pyodbc
import urllib
import os
import re
import tkinter as tk
import pandas as pd
import numpy as np
import sqlalchemy as sqla
from tqdm import tqdm
from tkinter import simpledialog, ttk
from datetime import datetime, timedelta

print(
    '===========================================================================================================================================================')
print(
    '=    start                                                                                                                                                =')
print(
    '===========================================================================================================================================================')

'''
############################################################################################
#   Connection to MAM Database                                                             #
############################################################################################
connection_string_DWH_MAM_PRD = (
    r"Driver=SQL Server;"
    r"Server=meesrv-bimam;"
    r"Database=DWH_MAM_PRD;"
    r"Trusted_Connection=yes;"
)

connection_url_dwh = URL.create(
    "mssql+pyodbc", 
    query={"odbc_connect": connection_string_DWH_MAM_PRD}
)
'''


def Get_Credentials():
    """
    This function is designed to interactively prompt the user for their database credentials.
    It creates a pop-up window to securely collect the username and password required for
    connecting to a database. The entered information is then returned as a tuple containing
    the username and password.

    Returns:
    - username (str): The entered username.
    - password (str): The entered password.
    """
    root = tk.Tk()
    root.withdraw()
    username = simpledialog.askstring("Input", "Entrez votre nom d'utilisateur:")
    password = simpledialog.askstring("Input", "Entrez votre mot de passe:", show='*')

    return username, password


def valider(liste1, liste2, liste3):
    valeur_liste1 = liste1.get()
    valeur_liste2 = liste2.get()
    valeur_liste3 = liste3.get()


def Get_Data_Table(Table, username, password, Server='10.130.1.20', database='MandarineGestion_Datawarehouse',
                   requete_SQL=''):
    """
    This function retrieves data from a specified table in a SQL Server database using the provided credentials.

    Parameters:
    - Table (str): The name of the table from which to retrieve data.
    - username (str): The username for connecting to the database.
    - password (str): The password for connecting to the database.
    - Server (str): The server address (default is '10.130.1.20').
    - database (str): The database name (default is 'MandarineGestion_Datawarehouse').
    - requete_SQL (str): Optional custom SQL query to retrieve specific data from the table.

    Returns:
    - df (pd.DataFrame): A pandas DataFrame containing the retrieved data from the specified table.
    """
    # Establish a connection to the SQL Server database
    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                          f'SERVER={Server};'
                          f'DATABASE={database};'
                          f'UID={username};'
                          f'PWD={password}')
    cursor = conn.cursor()

    # Execute the SQL query
    if requete_SQL == '':
        requete_SQL = "SELECT * FROM " + Table
        cursor.execute(requete_SQL)
    else:
        cursor.execute(requete_SQL)
    # Fetch the results, close the cursor and connection
    results = cursor.fetchall()
    results = [list(row) for row in results]
    columns = [column[0] for column in cursor.description]
    cursor.close()
    conn.close()
    # Convert the results into a pandas DataFrame
    df = pd.DataFrame(results, columns=columns)

    return df


def Check_Date(date_str):
    """
    Check_Date function is designed to validate whether a given string represents a date
    in the 'yyyy-mm-dd' format. It uses the datetime.strptime method to attempt to parse
    the input string into a datetime object. If successful, it returns True, indicating
    that the input string is a valid date in the expected format. If an exception
    (ValueError) is raised during the parsing attempt, it returns False, signifying that
    the input string does not conform to the expected date format.

    Parameters:
    - date_str (str): A string representing a date.

    Returns:
    - bool: True if the input string is a valid date in the 'yyyy-mm-dd' format, False otherwise.
    """
    try:
        datetime_obj = datetime.strptime(date_str, '%Y-%d-%m')
        return True
    except ValueError:
        return False


############################################################################################
#   Get Function                                                                           #
############################################################################################

def Get_Ref_Product(List_Key_Valeur, username, password, List_Labels=['*'], Server='10.130.1.20',
                    database='MandarineGestion_Datawarehouse'):
    """
    This function retrieves reference product data based on the provided key values.

    Parameters:
    - List_Key_Valeur (list): A list of Id_Ref_Valeur values to find in the reference database.
    - username (str): The username for connecting to the database.
    - password (str): The password for connecting to the database.
    - List_Labels (list): A list of labels specifying the columns to retrieve (default is ['*'] for all columns).
    - Server (str): The server address (default is '10.130.1.20').
    - database (str): The table name (default is 'MandarineGestion_Datawarehouse').

    Returns:
    - df (pd.DataFrame): A pandas DataFrame containing the product's datails of the specified key values.
    """
    Str_Labels = ', '.join(List_Labels)
    Str_Targets = " OR Key_Valeur = ".join(str(Key_Valeur) for Key_Valeur in List_Key_Valeur)
    Str_Targets = " WHERE Key_Valeur = " + Str_Targets

    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                          f'SERVER={Server};'
                          f'DATABASE={database};'
                          f'UID={username};'
                          f'PWD={password}')
    cursor = conn.cursor()
    # Execute the SQL query to retrieve product's data based on key values
    requete_SQL = "SELECT " + Str_Labels + " FROM Ref_Valeurs" + Str_Targets
    cursor.execute(requete_SQL)
    results = cursor.fetchall()
    results = [list(row) for row in results]
    columns = [column[0] for column in cursor.description]
    cursor.close()
    conn.close()
    # Convert the results into a pandas DataFrame
    df = pd.DataFrame(results, columns=columns)
    return df


def Get_Ref_Data_Histo(List_Key_Valeur, Date, username, password, Server='10.130.1.20',
                       database='MandarineGestion_Datawarehouse'):
    """
    This function retrieves reference product data based on the provided key values.

    Parameters:
    - List_Key_Valeur (list): A list of Id_Ref_Valeur values to find in the reference database.
    - username (str): The username for connecting to the database.
    - password (str): The password for connecting to the database.
    - Server (str): The server address (default is '10.130.1.20').
    - database (str): The table name (default is 'MandarineGestion_Datawarehouse').

    Returns:
    - df (pd.DataFrame): A pandas DataFrame containing the product's datails of the specified key values.
    """
    Date_as_Date = datetime.strptime(Date, "%Y-%d-%m")
    Date_Min = Date_as_Date - timedelta(days=7)
    Date_Min = Date_Min.strftime("%Y-%d-%m")

    Str_Targets = ",".join(str(Key_Valeur) for Key_Valeur in List_Key_Valeur)
    Date_Filter = f"WHERE Date_Cloture <= '{Date}' AND Date_Cloture > '{Date_Min}' GROUP BY ID_Ref_Valeur"

    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                          f'SERVER={Server};'
                          f'DATABASE={database};'
                          f'UID={username};'
                          f'PWD={password}')
    cursor = conn.cursor()

    # Execute the SQL query to retrieve product's data based on key values
    requete_SQL = f"SELECT Tb_Mo_Data_Histo.* FROM Tb_Mo_Data_Histo INNER JOIN (SELECT ID_Ref_Valeur,MAX(Date_Cloture) \
AS Max_Date_VL FROM Tb_Mo_Data_Histo {Date_Filter}) AS A ON Tb_Mo_Data_Histo.ID_Ref_Valeur = A.ID_Ref_Valeur AND \
Tb_Mo_Data_Histo.Date_Cloture = A.Max_Date_VL WHERE Tb_Mo_Data_Histo.ID_Ref_Valeur IN ({Str_Targets})"

    cursor.execute(requete_SQL)
    results = cursor.fetchall()
    results = [list(row) for row in results]
    columns = [column[0] for column in cursor.description]
    cursor.close()
    conn.close()
    # Convert the results into a pandas DataFrame
    df = pd.DataFrame(results, columns=columns)
    return df


def Get_Ptf(fund_id, username, password, Date, List_Labels=['*']):
    """
    This function retrieves data of a specific portfolio (Ptf) from the database
    based on the provided portfolio name, date, and optional list of labels.

    Parameters:
    - fund_id (str): The ID of the investment portfolio to retrieve data from.
    - username (str): The username for connecting to the database.
    - password (str): The password for connecting to the database.
    - Date (str): The date for which to retrieve portfolio data in the format 'YYYY-MM-DD'.
    - List_Labels (list): A list of labels specifying the columns to retrieve (default is ['*'] for all columns).

    Returns:
    - df (pd.DataFrame): A pandas DataFrame containing the portfolio data for the specified name and date.
    """
    Server = '10.130.1.20'
    database = 'MandarineGestion_Datawarehouse'
    Str_Labels = ', '.join(List_Labels)
    Ptf_Name = " WHERE fund_id = '" + str(fund_id) + "'"
    Ptf_Date = " AND Date_Contrib = '" + Date + "'"
    # Establish a connection to the SQL Server database
    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                          f'SERVER={Server};'
                          f'DATABASE={database};'
                          f'UID={username};'
                          f'PWD={password}')
    cursor = conn.cursor()
    # Execute the SQL query to retrieve portfolio data based on name and date
    requete_SQL = "SELECT " + Str_Labels + " FROM Tb_MO_Contribution " + Ptf_Name + Ptf_Date
    cursor.execute(requete_SQL)
    results = cursor.fetchall()
    results = [list(row) for row in results]
    columns = [column[0] for column in cursor.description]
    cursor.close()
    conn.close()
    # Convert the results into a pandas DataFrame
    df = pd.DataFrame(results, columns=columns)
    return df


def Get_Fund_Details(Key_Fund, username, password, List_Labels=['*']):
    """
    This function retrieves details for a specific fund from the database based on the provided Mnemo (Mnemonic) identifier
    and an optional list of labels.

    Parameters:
    - Key_Fund (str): The ID identifier of the fund to retrieve details for.
    - username (str): The username for connecting to the database.
    - password (str): The password for connecting to the database.
    - List_Labels (list): A list of labels specifying the columns to retrieve (default is ['*'] for all columns).

    Returns:
    - df (pd.DataFrame): A pandas DataFrame containing the fund details for the specified Mnemo identifier.
    """
    Server = '10.130.1.20'
    database = 'MandarineGestion_Datawarehouse'
    Str_Labels = ', '.join(List_Labels)
    Ptf_Name = " WHERE Key_Fund = '" + Key_Fund + "'"
    requete_SQL = "SELECT " + Str_Labels + " FROM Ref_Funds" + Ptf_Name

    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                          f'SERVER={Server};'
                          f'DATABASE={database};'
                          f'UID={username};'
                          f'PWD={password}')
    cursor = conn.cursor()
    cursor.execute(requete_SQL)
    results = cursor.fetchall()
    results = [list(row) for row in results]
    columns = [column[0] for column in cursor.description]
    cursor.close()
    conn.close()
    df = pd.DataFrame(results, columns=columns)


def Get_Fund_List(username, password, List_Labels=['*'], PTF_Reel=1, Open_Fund=1, Public_Dedie=None, Freq_VL=None,
                  Additionnal_Filter=None):
    """
    This function retrieves a list of funds from the database based on specified filters and criteria.

    Parameters:
    - username (str): The username for connecting to the database.
    - password (str): The password for connecting to the database.
    - List_Labels (list): A list of labels specifying the columns to retrieve (default is ['*'] for all columns).
    - PTF_Reel (int): The filter for selecting real portfolios (default is 1, Reel Ptf).
    - Open_Fund (int): The filter for selecting open funds (default is 1, Open fund).
    - Public_Dedie (int or None): The filter for selecting public or dedicated funds (default is None for no filter).
    - Freq_VL (int or None): The filter for selecting funds based on a specific frequency (default is None for no filter).
    - Additionnal_Filter (str or None): Additional SQL filter condition (default is None for no additional filter).

    Returns:
    - df (pd.DataFrame): A pandas DataFrame containing the list of funds based on the specified filters.
    """
    Server = '10.130.1.20'
    database = 'MandarineGestion_Datawarehouse'
    # Début de la requête SQL
    requete_SQL = f"SELECT {', '.join(List_Labels)} FROM Ref_Funds WHERE 1=1"
    if PTF_Reel is not None:
        requete_SQL += f" AND PTF_Reel = {PTF_Reel}"
    if Open_Fund == 1:
        requete_SQL += f" AND Date_Cloture is null"
    if Public_Dedie is not None:
        requete_SQL += f" AND Public_Dedie = '{Public_Dedie}'"
    if Freq_VL is not None:
        requete_SQL += f" AND Freq_VL = '{Freq_VL}'"
    if Additionnal_Filter is not None:
        requete_SQL += f" AND {Additionnal_Filter}"
    # Establish a connection to the SQL Server database
    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                          f'SERVER={Server};'
                          f'DATABASE={database};'
                          f'UID={username};'
                          f'PWD={password}')
    cursor = conn.cursor()
    # Execute the SQL query to retrieve fund list based on filter
    cursor.execute(requete_SQL)
    results = cursor.fetchall()
    results = [list(row) for row in results]
    columns = [column[0] for column in cursor.description]
    cursor.close()
    conn.close()
    # Convert the results into a pandas DataFrame
    df = pd.DataFrame(results, columns=columns)

    return df


def Get_Fund_Part_List(username, password, Key_Fund, List_Labels=['*'], Statut_Part='Active', Code_Part=None,
                       Public_Dedie=None, Additionnal_Filter=None):
    '''
    Function to retrieve fund part details from the database based on specified criteria.
    Parameters:
    - username: Database username for authentication.
    - password: Database password for authentication.
    - Key_Fund: Key identifier for the fund.
    - List_Labels: List of columns to be retrieved (default is all columns represented by '*').
    - Statut_Part: Status of the fund part (default is 'Active').
    - Code_Part: Specific code for the fund part (default is None).
    - Public_Dedie: Indicator for public or dedicated fund part (default is None).
    - Additionnal_Filter: Additional filter conditions for the SQL query (default is None).
    Returns a DataFrame containing the fund part details.
    '''
    Server = '10.130.1.20'
    database = 'MandarineGestion_Datawarehouse'
    # Début de la requête SQL
    requete_SQL = f"SELECT {', '.join(List_Labels)} FROM Ref_Funds_Parts WHERE 1=1"
    if Statut_Part is not None:
        requete_SQL += f" AND Statut_Part = '{Statut_Part}'"
    if Code_Part is not None:
        requete_SQL += f" AND Code_Part = '{Code_Part}'"
    if Public_Dedie is not None:
        requete_SQL += f" AND Public_Dedie = '{Public_Dedie}'"
    if Additionnal_Filter is not None:
        requete_SQL += f" AND {Additionnal_Filter}"
    requete_SQL += f" AND ref_fund_id = '{Key_Fund}'"
    # Establish a connection to the SQL Server database
    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                          f'SERVER={Server};'
                          f'DATABASE={database};'
                          f'UID={username};'
                          f'PWD={password}')
    cursor = conn.cursor()
    # Execute the SQL query to retrieve fund list based on filter
    cursor.execute(requete_SQL)
    results = cursor.fetchall()
    results = [list(row) for row in results]
    columns = [column[0] for column in cursor.description]
    cursor.close()
    conn.close()
    # Convert the results into a pandas DataFrame
    df = pd.DataFrame(results, columns=columns)
    return df


def Get_Last_Nav_Date(username, password, fund_id, Date):
    '''
    Function to retrieve the latest NAV date for a specified fund and date.
    Parameters:
    - username: Database username for authentication.
    - password: Database password for authentication.
    - fund_id: Identifier for the fund.
    - Date: Reference date for NAV calculation.
    Returns the latest NAV date based on the provided fund identifier and date filter.
    '''
    Server = '10.130.1.20'
    database = 'MandarineGestion_Datawarehouse'
    if Check_Date(Date):

        Filter = f" WHERE fund_id = '{fund_id}' AND Date_Contrib <= '{Date}'"
        requete_SQL = f"SELECT MAX(DISTINCT(Date_Contrib)) FROM Tb_MO_Contribution"
        requete_SQL += Filter
        # Establish a connection to the SQL Server database
        conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                              f'SERVER={Server};'
                              f'DATABASE={database};'
                              f'UID={username};'
                              f'PWD={password}')
        cursor = conn.cursor()
        # Execute the SQL query to retrieve fund list based on filter
        cursor.execute(requete_SQL)
        results = cursor.fetchall()
        results = [list(row) for row in results]
        columns = [column[0] for column in cursor.description]
        cursor.close()
        conn.close()
        # Convert the results into a pandas DataFrame
        df = pd.DataFrame(results, columns=columns)
        result = df.at[0, '']
        if result == None:
            return None
        else:
            result = result.strftime('%Y-%d-%m')
        return result
    else:
        print("The date format is not <yyyy-dd-mm>")
        return None


def Get_Funds_VL(username, password, ref_funds_part_id, Date, List_Labels=['*']):
    '''
    Function to retrieve fund values based on the reference funds part ID and a specific date.
    Parameters:
    - username: Database username for authentication.
    - password: Database password for authentication.
    - ref_funds_part_id: Identifier for the reference funds part.
    - Date: Reference date for fund valuation.
    - List_Labels: List of columns to be retrieved (default is all columns represented by '*').
    Returns a DataFrame containing fund values for the specified reference funds part ID and date.
    '''
    Server = '10.130.1.20'
    database = 'MandarineGestion_Datawarehouse'
    if Check_Date(Date):
        requete_SQL = f"SELECT {', '.join(List_Labels)} FROM Tb_Funds_VL WHERE Date_VL_Date = '{Date}' AND ref_funds_part_id = '{ref_funds_part_id}'"
        # Establish a connection to the SQL Server database
        conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                              f'SERVER={Server};'
                              f'DATABASE={database};'
                              f'UID={username};'
                              f'PWD={password}')
        cursor = conn.cursor()
        # Execute the SQL query to retrieve fund list based on filter
        cursor.execute(requete_SQL)
        results = cursor.fetchall()
        results = [list(row) for row in results]
        columns = [column[0] for column in cursor.description]
        cursor.close()
        conn.close()
        # Convert the results into a pandas DataFrame
        df = pd.DataFrame(results, columns=columns)
        return df


def Get_Last_Previous_Month_Date(date_str):
    '''
    Function to obtain the last day of the previous month based on a given date string.
    Parameters:
    - date_str: Input date string in the format '%Y-%d-%m'.
    Returns a string representing the last day of the previous month in the format '%Y-%d-%m'.
    '''
    date_object = datetime.strptime(date_str, '%Y-%d-%m')
    first_day_of_current_month = datetime(date_object.year, date_object.month, 1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    result_date_str = last_day_of_previous_month.strftime('%Y-%d-%m')

    return result_date_str


def Get_Ref_Pays(username, password):
    '''
    Function to retrieve reference data for countries from a SQL Server database.

    Parameters:
    - username (str): Username for database connection.
    - password (str): Password for database connection.

    Returns:
    - pd.DataFrame: A pandas DataFrame containing reference data for countries.
    '''
    Server = '10.130.1.20'
    database = 'MandarineGestion_Datawarehouse'
    requete_SQL = "SELECT * FROM Ref_Pays"
    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                          f'SERVER={Server};'
                          f'DATABASE={database};'
                          f'UID={username};'
                          f'PWD={password}')
    cursor = conn.cursor()
    # Execute the SQL query to retrieve fund list based on filter
    cursor.execute(requete_SQL)
    results = cursor.fetchall()
    results = [list(row) for row in results]
    columns = [column[0] for column in cursor.description]
    cursor.close()
    conn.close()
    # Convert the results into a pandas DataFrame
    df = pd.DataFrame(results, columns=columns)
    return df


def get_fx_for_row(row, Devise1, Date, username, password):
    '''
    Function to retrieve Fx data for specific Date ans currencies from database.
    Parameters:
    - Devise1 :
    - Devise2 :
    - Date (str)('dd/mm/yyyy'): Date of Fx needed
    - username (str): Username for database connection.
    - password (str): Password for database connection.

    Returns:
    - pd.DataFrame: A pandas DataFrame containing reference data for countries.
    '''
    Devise2 = row['21_Quotation_currency_(A)']

    # print(f"Devise2 : {Devise2}")

    if Devise2 != Devise1:
        Server = '10.130.1.20'
        database = 'MandarineGestion_Datawarehouse'
        requete_SQL = f"SELECT TOP(1) Cours FROM Tb_MO_Cours_Cloture WHERE (Isin LIKE '%{Devise1}{Devise2} ECB%' OR Isin LIKE '%{Devise1}{Devise2}%') AND Date='{Date}' ORDER BY id_cours DESC"
        conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                              f'SERVER={Server};'
                              f'DATABASE={database};'
                              f'UID={username};'
                              f'PWD={password}')
        cursor = conn.cursor()
        # Execute the SQL query to retrieve fund list based on filter
        cursor.execute(requete_SQL)
        results = cursor.fetchall()
        # print(f"Result  : {results}")
        results = [list(row) for row in results]
        columns = [column[0] for column in cursor.description]
        cursor.close()
        conn.close()
        # Convert the results into a pandas DataFrame
        return float(results[0][0])
    else:
        return 1


def Fx_Opti(devises, devise_base, date):
    # Setup
    Server = '10.130.1.20'
    database = 'MandarineGestion_Datawarehouse'
    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                          f'SERVER={Server};'
                          f'DATABASE={database};'
                          f'Trusted_Connection=yes')

    dictionary_Fx = {}
    Liste_Change = [devise_base + devise for devise in devises]

    for change in Liste_Change:
        requete_SQL = f"SELECT TOP(1) Cours FROM Tb_MO_Cours_Cloture WHERE ( Isin LIKE '%{change} ECB%' OR Isin LIKE '%{change}%')  AND Date='{date}'"
        # print (requete_SQL)
        if change[:3] == change[-3:]:
            # print("ok")
            dictionary_Fx[change] = 1
        else:
            cursor = conn.cursor()
            cursor.execute(requete_SQL)
            results = cursor.fetchall()
            if results:
                valeur = results[0][0]
                dictionary_Fx[change] = valeur
            else:
                print(f"Aucune valeur n'a été retournée par la requête {change}.")
    return dictionary_Fx


def Redemption_type(row):
    '''
    Function to determine the redemption type based on the values in specific columns of a DataFrame row.
    Parameters:
    - row: DataFrame row containing information on redemption-related columns ('defaulted', 'bullet', 'sinkable').
    Returns a redemption type string ('DEFAULTED', 'BULLET', 'SINKABLE') or None.
    '''
    if row['defaulted'] == 'Y':
        return 'DEFAULTED'
    elif row['bullet'] == 'Y':
        return 'BULLET'
    elif row['sinkable'] == 'Y':
        return 'SINKABLE'
    else:
        return None


def assign_value_LEI_Or_Empty(val):
    '''
    Function to assign a value based on the presence of None (NaN) in a DataFrame column.
    If the value is None, assign 9; otherwise, assign 1.
    '''
    return 9 if pd.isna(val) or val == '' else 1


def Process_NACE_Code(val):
    '''
    Function to process a NACE code from a DataFrame column.
    If the value is None, it returns None.
    If the value is not None, it extracts the first character of the string.
    If the first character is a letter, it returns the letter.
    Otherwise, it issues a warning and returns None.
    If the string is empty, it issues a warning and returns None.
    '''

    if pd.isna(val):
        return None
    else:
        # Retrieve the value of val
        nace_code = str(val)
        # Check if the string is not empty
        if nace_code:
            # Test if the first character is a letter
            if nace_code[0].isalpha() and nace_code[0] == 'K':
                return nace_code
            elif nace_code[0].isalpha():
                return nace_code[0]
            else:
                # warnings.warn('NACE code is not in the correct format')
                return nace_code
        else:
            # warnings.warn('NACE code is empty')
            return None


def Process_Economic_Area_Code(val, username, password):
    '''
    Function to process an Economic Area code from a DataFrame column.

    Args:
    - val (str): The value to be processed.
    - username (str): The username for authentication.
    - password (str): The password for authentication.

    Returns:
    - str or None: Returns a string representing the Economic Area code (1, 2, or 3) or None.

    Steps:
    1. Replace empty strings with None.
    2. Retrieve reference country information using Get_Ref_Pays.
    3. If val is None, return None.
    4. Extract OCDE and EEE values from reference countries.
    5. Determine the Economic Area Code based on OCDE and EEE values.
       - Code '1' if EEE is 1.
       - Code '2' if OCDE is 1 and EEE is 0.
       - Code '3' otherwise.
    '''
    if val == '':
        val = None
    Ref_Pays = Get_Ref_Pays(username, password)
    if pd.isna(val):
        return None
    else:
        OCDE = Ref_Pays.loc[Ref_Pays['Mnemo_Pays'] == val, 'OCDE'].values[0]
        EEE = Ref_Pays.loc[Ref_Pays['Mnemo_Pays'] == val, 'EEE'].values[0]
        if val == 'EO':
            return '1'
        if EEE == 1:
            return '1'
        elif OCDE == 1 and EEE == 0:
            return '2'
        else:
            return '3'


def Get_Economic_Area_Code_Opti(username, password):
    '''

    '''
    Ref_Pays = Get_Ref_Pays(username, password)
    Ref_Pays['Economic_Area_Code'] = Ref_Pays.apply(lambda row:
                                                    1 if row['Mnemo_Pays'] == 'EO' else
                                                    (1 if row['EEE'] == 1 else
                                                     (2 if (row['OCDE'] == 1 and row['EEE'] == 0) else 3)), axis=1)

    dict_pays_economic_area = Ref_Pays.set_index('Mnemo_Pays')['Economic_Area_Code'].to_dict()

    return dict_pays_economic_area


def organize_columns(dataframe):
    # Select columns starting with a digit
    digit_columns = [col for col in dataframe.columns if col[0].isdigit()]

    # Select columns starting with a letter
    letter_columns = [col for col in dataframe.columns if col[0].isalpha()]

    # Organize columns in order
    organized_columns = sorted(digit_columns, key=lambda x: (
        int(x.split("_")[0]) if x.split("_")[0].isdigit() else int(x.split("_")[0][:-1]))) + letter_columns

    # Create a new DataFrame with organized columns
    organized_dataframe = dataframe[organized_columns]

    return organized_dataframe


def Process_Hedge(val):
    if val == '':
        val = None
    if pd.isna(val):
        return None
    elif val[2].isalpha():
        return 'Y'


def Process_CIC_Code(val):
    '''
    This function processes a CIC code, which is expected to be a 4-character string.
    The code is first checked for empty or NaN values and replaced accordingly. If the length of the code is not 4, a warning is issued, and the function returns None.
    Otherwise, it proceeds to map the first two characters to a category and the last two characters to a subcategory using predefined dictionaries.

    Parameters:
    val: The CIC code to be processed.

    Returns:
    A list containing the first two characters of the code, the last two characters of the code, the corresponding category, and the corresponding subcategory.
    '''
    if val == '':
        val = None
    if pd.isna(val):
        return None
    val.replace(" ", "")
    if len(val) != 4:
        warnings.warn('CIC code is not in the correct format')
        return None
    else:
        Correspondance_Catégorie = {
            '1': 'Sovereign Bonds',
            '2': 'Corporate Bonds',
            '3': 'Equities',
            '4': 'Investment Funds',
            '5': 'Structured Securities',
            '6': 'Securitized Securities',
            '7': 'Cash and Deposits',
            '8': 'Loans and Mortgages',
            '9': 'Tangible Assets',
            'A': 'Futures',
            'B': 'Call Options',
            'C': 'Put Options',
            'D': 'Swap Contracts',
            'E': 'Forward Contracts',
            'F': 'Credit Derivatives'
        }
        Correspondance_Sous_Catégorie = {
            '11': 'State Bonds',
            '12': 'Supranational Organization Bonds',
            '13': 'Regional Bonds',
            '14': 'Municipal Bonds',
            '15': 'Treasury Bills',
            '16': 'Secured Bonds',
            '19': 'Others',
            '21': 'Ordinary Bonds',
            '22': 'Convertible Bonds',
            '23': 'Commercial Paper',
            '24': 'Monetary Instruments',
            '25': 'Hybrid Securities',
            '26': 'Ordinary Secured Bonds',
            '27': 'Legally Secured Bonds',
            '28': 'Subordinated Securities',
            '29': 'Others',
            '31': 'Common Stocks',
            '32': 'Stocks in Real Estate Companies and Similar',
            '33': 'Subscription Warrants',
            '34': 'Preferred Stocks',
            '39': 'Others',
            '41': 'Equity Funds',
            '42': 'Bond Funds',
            '43': 'Money Market Funds',
            '44': 'Asset Allocation Funds',
            '45': 'Real Estate Funds',
            '46': 'Alternative Funds',
            '47': 'Private Equity Funds',
            '48': 'Infrastructure Funds',
            '49': 'Others',
            '51': 'Equity Risk',
            '52': 'Interest Rate Risk',
            '53': 'Exchange Rate Risk',
            '54': 'Credit Risk',
            '55': 'Real Estate Risk',
            '56': 'Commodity-Related Risks',
            '57': 'Catastrophe and Climate Risk',
            '58': 'Mortality Risk',
            '59': 'Others',
            '61': 'Equity Risk',
            '62': 'Interest Rate Risk',
            '63': 'Exchange Rate Risk',
            '64': 'Credit Risk',
            '65': 'Real Estate Risk',
            '66': 'Commodity-Related Risks',
            '67': 'Catastrophe and Climate Risk',
            '68': 'Mortality Risk',
            '69': 'Others',
            '71': 'Cash',
            '72': 'Transferable Deposits (Equivalent to Cash)',
            '73': 'Other Short-Term Deposits (Less Than One Year)',
            '74': 'Other Deposits With a Term Over One Year',
            '75': 'Deposits With Lenders',
            '79': 'Others',
            '81': 'Unsecured Loans',
            '82': 'Securities-Backed Loans',
            '84': 'Mortgages',
            '85': 'Other Secured Loans',
            '86': 'Advances on Policies',
            '89': 'Others',
            '91': 'Real Estate (Office and Commercial)',
            '92': 'Real Estate (Residential)',
            '93': 'Real Estate (Own Use)',
            '94': 'Construction Real Estate',
            '95': 'Equipment (Own Use)',
            '99': 'Others',
            'A1': 'Futures Contracts on Stocks and Stock Indices',
            'A2': 'Interest Rate Futures Contracts',
            'A3': 'Currency Futures Contracts',
            'A5': 'Commodity Futures Contracts',
            'A7': 'Catastrophe and Climate Risk Contracts',
            'A8': 'Mortality Risk',
            'A9': 'Others',
            'B1': 'Call Options on Stocks or Stock Indices',
            'B2': 'Call Options on Bonds',
            'B3': 'Call Options on Currency',
            'B4': 'Warrants',
            'B5': 'Call Options on Commodities',
            'B6': 'Swaptions',
            'B7': 'Call Options on Catastrophe and Climate Risks',
            'B8': 'Call Options on Mortality Risk',
            'B9': 'Others',
            'C1': 'Put Options on Stocks or Stock Indices',
            'C2': 'Put Options on Bonds',
            'C3': 'Put Options on Currency',
            'C4': 'Warrants',
            'C5': 'Put Options on Commodities',
            'C6': 'Swaptions',
            'C7': 'Put Options on Catastrophe and Climate Risks',
            'C8': 'Put Options on Mortality Risk',
            'C9': 'Others',
            'D1': 'Interest Rate Swap Contracts',
            'D2': 'Currency Swap Contracts',
            'D3': 'Interest Rate and Currency Swap Contracts',
            'D5': 'Securities Swap Contracts',
            'D7': 'Catastrophe and Climate Risk Swap Contracts',
            'D8': 'Mortality Risk Swap Contracts',
            'D9': 'Others',
            'E1': 'Interest Rate Forwards Contracts',
            'E2': 'Currency Forwards Contracts',
            'E7': 'Catastrophe and Climate Risk Forwards Contracts',
            'E8': 'Mortality Risk Forwards Contracts',
            'E9': 'Others',
            'F1': 'Credit Event Derivatives (Credit Default Swap)',
            'F2': 'Credit Spread Options',
            'F3': 'Credit Spread Swaps',
            'F4': 'Total Return Swaps',
            'F9': 'Others'
        }
        # Utilisation du dictionnaire de correspondance pour obtenir la description
        return [val[0:2], val[2:4], Correspondance_Catégorie[val[2]], Correspondance_Sous_Catégorie[val[2:4]]]


def Process_Guarantee(val):
    '''
    Process a guarantee value and return 'Y' if it contains 'gov', otherwise 'N'.
    Parameters:
    - val: The input value representing a guarantee.
    Returns:
    - 'Y' if 'gov' is found in the input (case-insensitive), otherwise 'N'.
    '''
    if val == '':
        val = None
    if pd.isna(val):
        return None
    if val.lower().find('gov'):
        return 'Y'
    else:
        return 'N'


def Process_Call_Put(val):
    if val is not None:
        if val == "":
            return None
        else:
            val_lower = val.lower()
            if val_lower == 'call' or val_lower == 'c':
                return 'Cal'
            elif val_lower == 'put' or val_lower == 'p':
                return 'Put'
            elif val_lower == 'floor':
                return 'Flr'
            elif val_lower == 'cap':
                return 'Cap'
            else:
                return val
    else:
        return None


def Process_Underlying_asset_category(val):
    '''
    Process an underlying asset category code and return a modified value.
    Parameters:
    - val: The input value representing an underlying asset category code.
    Returns:
    - If the length is not 4, a warning is issued, and the original value is returned.
    - If the third character is '3', returns '3L'.
    - Otherwise, returns the third character.
    '''
    if val == '':
        val = None
    if pd.isna(val):
        return None
    if len(val) != 4:
        warnings.warn('CIC code is not in the correct format')
        return val
    elif val[2] == '3':
        return val[2] + 'L'
    else:
        return val[2]


def generate_date_range(start_date, end_date):
    date_list = []
    current_date = start_date

    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)

    return date_list


def is_valid_isin(isin):
    """
    Checks if a string is a valid ISIN.

    Args:
    isin (str): The string to check.

    Returns:
    bool: True if the ISIN is valid, False otherwise.
    """
    isin = isin.replace(" ", "").upper()
    if len(isin) != 12:
        return False
    elif not re.match(r'^[A-Z]{2}[0-9A-Z]{10}$', isin):
        return False
    else:
        return True


def Process_ISIN(val):
    if val == '':
        val = None
    elif pd.isna(val):
        return None
    elif is_valid_isin(val):
        return '1'
    else:
        return '99'


def formatage_chiffre(chiffre):
    return '{:,.0f}'.format(chiffre).replace(',', ' ')


def create_date_dataframe(start_date=None, end_date=None):
    if start_date is None:
        start_date = datetime.now()
    if end_date is None:
        end_date = start_date - timedelta(days=180)
    date_range = pd.date_range(end=start_date, start=end_date, freq='B')

    formatted_dates = [date.strftime('%d/%m/%Y') for date in date_range]
    df = pd.DataFrame({'Date': formatted_dates})

    return df


def Get_Historical_Fund_NAV(Key_Fund, username, password, start_date=None, end_date=None):
    # Setup
    Server = '10.130.1.20'
    database = 'MandarineGestion_Datawarehouse'
    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                          f'SERVER={Server};'
                          f'DATABASE={database};'
                          f'UID={username};'
                          f'PWD={password}')

    if start_date is None:
        start_date = datetime.now()
    if end_date is None:
        end_date = start_date - timedelta(days=180)

    start_date = start_date.strftime('%d/%m/%Y')
    end_date = end_date.strftime('%d/%m/%Y')

    Sql_Query = f"SELECT TB_VL.Date_VL_Date, SUM(TB_VL.VL) AS Fund_VL FROM Tb_Funds_VL AS TB_VL LEFT JOIN Ref_Funds_Parts AS REF_PART ON REF_PART.Key_Fund_Part = TB_VL.ref_funds_part_id LEFT JOIN Ref_Funds AS REF_FUND ON REF_FUND.Key_Fund = REF_PART.ref_fund_id WHERE REF_PART.Key_Fund_Part = {Key_Fund} AND Date_VL_Date >= '{end_date}' AND Date_VL_Date <= '{start_date}' AND Statut_Part = 'Active' GROUP BY Key_Fund, Date_VL_Date ORDER BY Key_Fund DESC, Date_VL_Date DESC"

    cursor = conn.cursor()
    cursor.execute(Sql_Query)
    results = cursor.fetchall()
    results = [list(row) for row in results]
    columns = [column[0] for column in cursor.description]
    cursor.close()
    conn.close()
    df = pd.DataFrame(results, columns=columns)
    # df['Date_VL_Date'] = df['Date_VL_Date'].dt.strftime('%d/%m/%Y')
    return df


def Process_Coupon(val):
    if val == 'A':
        return 1
    elif val == 'T':
        return 4
    elif val == 'S':
        return 2
    else:
        return val  # Garder les autres valeurs inchangées


def Get_Rtg_Dictionnary(List_Oblig, Date):
    List_Oblig = "('" + "', '".join(List_Oblig) + "')"
    Server = '10.130.1.20'
    database = 'MandarineGestion_Datawarehouse'
    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                          f'SERVER={Server};'
                          f'DATABASE={database};'
                          f'Trusted_Connection=yes')

    Sql_Query = f"SELECT RF.Key_Valeur, RTG.Rtg_MDY , RTG.Rtg_SP , RTG.Rtg_Fitch , RTG.Rtg_MG_1 FROM Tb_MO_Rating AS RTG LEFT JOIN Ref_Valeurs AS RF ON RF.Code_ISIN_Valeur = RTG.Isin WHERE RTG.Date_Rating = '{Date}' AND RTG.Isin IN {List_Oblig} ORDER BY RTG.Id_Rating DESC"

    cursor = conn.cursor()
    cursor.execute(Sql_Query)
    results = cursor.fetchall()
    results = [list(row) for row in results]
    columns = [column[0] for column in cursor.description]
    cursor.close()
    conn.close()
    df = pd.DataFrame(results, columns=columns)

    correspondance = {
        'Aaa': 'AAA',
        'Aa1': 'AA+',
        'Aa2': 'AA+',
        'Aa3': 'AA-',
        'A1': 'A+',
        'A2': 'A',
        'A3': 'A-',
        'Baa1': 'BBB+',
        'Baa2': 'BBB',
        'Baa3': 'BBB-',
        'Ba1': 'BB+',
        'Ba2': 'BB',
        'Ba3': 'BB-',
        'B1': 'B+',
        'B2': 'B',
        'B3': 'B-',
        'Caa1': 'CCC+',
        'Caa2': 'CCC',
        'Caa3': 'CCC-',
        'Ca': 'CC',
        'C': 'D'
    }
    df['Rtg_MDY'] = df['Rtg_MDY'].map(correspondance)
    df['Rating_Agency'] = df.apply(get_provenance, axis=1)
    df = df[['Key_Valeur', 'Rtg_MG_1', 'Rating_Agency']]
    df = df.rename(columns={'Key_Valeur': 'Id_Ref_Valeur'})
    return df


def get_provenance(row):
    if isinstance(row['Rtg_SP'], str) and row['Rtg_MG_1'] in row['Rtg_SP']:
        return 'S&P'
    elif isinstance(row['Rtg_Fitch'], str) and row['Rtg_MG_1'] in row['Rtg_Fitch']:
        return 'Fitch'
    elif isinstance(row['Rtg_MDY'], str) and row['Rtg_MG_1'] in row['Rtg_MDY']:
        return "Moody's"
    else:
        return None


def EPT_DB_Storage(df):
    Server = '10.130.1.20'
    database = 'MandarineGestion_Datawarehouse'
    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                          f'SERVER={Server};'
                          f'DATABASE={database};'
                          f'Trusted_Connection=yes')

    for index, row in df.iterrows():
        merge_query = f"""
            MERGE INTO ma_table AS target
            USING (VALUES ('{row['00001_EPT_Version']}','{row['00002_EPT_Producer_Name']}','{row['00004_EPT_Producer_Email']}','{row['00005_File_Generation_Date_And_Time']}','{row['00006_EPT_Data_Reporting_Narratives']}',
                           '{row['00007_EPT_Data_Reporting_Costs']}','{row['00008_EPT_Data_Reporting_Additional_Requirements_German_MOPs']}','{row['00009_EPT_Additional_Information_Structured_Products']}','{row['00010_Portfolio_Manufacturer_Name']}',
                           '{row['00015_Portfolio_Manufacturer_Group_Name']}','{row['00016_Portfolio_Manufacturer_LEI']}','{row['00017_Portfolio_Manufacturer_Email']}','{row['00020_Portfolio_Guarantor_Name']}','{row['00030_Portfolio_Identifying_Data']}',
                           {row['00040_Type_Of_Identification_Code_For_The_Fund_Share_Or_Portfolio']},'{row['00050_Portfolio_Name']}','{row['00060_Portfolio_Or_Share_Class_Currency']}','{row['00070_PRIIPs_KID_Publication_Date']}',
                           '{row['00075_PRIIPs_KID_Web_Address']}',{row['00080_Portfolio_PRIIPS_Category']},'{row['00090_Fund_CIC_code']}','{row['00110_Is_An_Autocallable_Product']}','{row['00120_Reference_Language']}',{row['01010_Valuation_Frequency']},
                           {row['01020_Portfolio_VEV_Reference']},'{row['01030_IS_Flexible']}',{row['01040_Flex_VEV_Historical']},{row['01050_Flex_VEV_Ref_Asset_Allocation']},'{row['01060_IS_Risk_Limit_Relevant']}',{row['01070_Flex_VEV_Risk_Limit']},
                           '{row['01080_Existing_Credit_Risk']}',{row['01090_SRI']},'{row['01095_IS_SRI_Adjusted']}',{row['01100_MRM']},{row['01110_CRM']},{row['01120_Recommended_Holding_Period']},'{row['01125_Has_A_Contractual_Maturity_Date']}',
                           '{row['01130_Maturity_Date']}','{row['01140_Liquidity_Risk']}',{row['02010_Portfolio_Return_Unfavourable_Scenario_1_Year']},{row['02020_Portfolio_Return_Unfavourable_Scenario_Half_RHP']},
                           {row['02030_Portfolio_Return_Unfavourable_Scenario_RHP_Or_First_Call_Date']},'{row['02032_Autocall_Applied_Unfavourable_Scenario']}','{row['02035_Autocall_Date_Unfavourable_Scenario']}',{row['02040_Portfolio_Return_Moderate_Scenario_1_Year']},
                           {row['02050_Portfolio_Return_Moderate_Scenario_Half_RHP']},{row['02060_Portfolio_Return_Moderate_Scenario_RHP_Or_First_Call_Date']},'{row['02062_Autocall_Applied_Moderate_Scenario']}','{row['02065_Autocall_Date_Moderate_Scenario']}',
                           {row['02070_Portfolio_Return_Favourable_Scenario_1_Year']},{row['02080_Portfolio_Return_Favourable_Scenario_Half_RHP']},{row['02090_Portfolio_Return_Favourable_Scenario_RHP_Or_First_Call_Date']},'{row['02092_Autocall_Applied_Favourable_Scenario']}',
                           '{row['02095_Autocall_Date_Favourable_Scenario']}',{row['02100_Portfolio_return_stress_scenario_1_year']},{row['02110_Portfolio_return_stress_scenario_half_RHP']},{row['02120_Portfolio_Return_Stress_Scenario_RHP_Or_First_Call_Date']},
                           '{row['02122_Autocall_Applied_Stress_Scenario']}','{row['02125_Autocall_Date_Stress_Scenario']}',{row['02130_Portfolio_Number_Of_Observed_Return_M0']},{row['02140_Portfolio_Mean_Observed_Returns_M1']},{row['02150_Portfolio_Observed_Sigma']},
                           {row['02160_Portfolio_Observed_Skewness']},{row['02170_Portfolio_Observed_Excess_Kurtosis']},{row['02180_Portfolio_Observed_Stressed_Volatility']},'{row['02185_Portfolio_Past_Performance_Disclosure_Required']}',
                           '{row['02190_Past_Performance_Link']}','{row['02200_Previous_Performance_Scenarios_Calculation_Link']}',{row['02210_Past_Performance_Number_Of_Years']},{row['02220_Reference_Invested_Amount']},{row['03010_One_off_cost_Portfolio_entry_cost']},
                           {row['03015_One_off_cost_Portfolio_entry_cost_Acquired']},{row['03020_One_off_costs_Portfolio_exit_cost_at_RHP']},{row['03030_One_off_costs_Portfolio_exit_cost_at_1_year']},{row['03040_One_off_costs_Portfolio_exit_cost_at_half_RHP']},
                           '{row['03050_One_off_costs_Portfolio_sliding_exit_cost_Indicator']}',{row['03060_Ongoing_Costs_Management_Fees_And_Other_Administrative_Or_Operating_Costs']},NULL,{row['03080_Ongoing_costs_Portfolio_transaction_costs']},
                           '{row['03090_Existing_Incidental_Costs_Portfolio']}',{row['03095_Incidental_costs']},NULL,NULL,NULL,'{row['04020_Comprehension_Alert_Portfolio']}','{row['04030_Intended_target_market_retail_investor_Portfolio']}',
                           '{row['04040_Investment_objective_Portfolio']}','{row['04050_Risk_narrative_Portfolio']}','{row['04060_Other_materially_relevant_risk_narrative_Portfolio']}','{row['04070_Type_of_underlying_Investment_Option']}',
                           '{row['04080_Capital_Guarantee']}',{row['04081_Capital_Guarantee_Level']},'{row['04082_Capital_Guarantee_Limitations']}','{row['04083_Capital_Guarantee_Early_Exit_Conditions']}','{row['04084_Capital_guarantee_Portfolio']}',
                           {row['04085_Possible_maximum_loss_Portfolio']},'{row['04086_Description_Past_Interval_Unfavourable_Scenario']}','{row['04087_Description_Past_Interval_Moderate_Scenario']}','{row['04088_Description_Past_Interval_Favourable_Scenario']}',
                           '{row['04089_Was_Benchmark_Used_Performance_Calculation']}','{row['04090_Portfolio_Performance_Fees_Carried_Interest_Narrative']}',NULL,NULL,'{row['04120_One_Off_Cost_Portfolio_Entry_Cost_Description']}',
                           '{row['04130_One_Off_Cost_Portfolio_Exit_Cost_Description']}','{row['04140_Ongoing_Costs_Portfolio_Management_Costs_Description']}','{row['04150_Do_Costs_Depend_On_Invested_Amount']}','{row['04160_Cost_Dependence_Explanation']}',
                           NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'{row['06005_German_MOPs_Reference_Date']}',{row['06010_Bonds_Weight']},{row['06020_Annualized_Return_Volatility']},{row['06030_Duration_Bonds']},'{row['06040_Existing_Capital_Preservation']}',
                           {row['06050_Capital_Preservation_Level']},{row['06060_Time_Interval_Maximum_Loss']},'{row['06070_Uses_PI']}',{row['06080_Multiplier_PI']},'{row['07005_First_Possible_Call_Date']}',{row['07010_Total_Cost_1_Year_Or_First_Call']},
                           {row['07020_RIY_1_Year_Or_First_Call']},{row['07030_Total_Cost_Half_RHP']},{row['07040_RIY_Half_RHP']},{row['07050_Total_Cost_RHP']},{row['07060_RIY_RHP']},{row['07070_One_Off_Costs_Portfolio_Entry_Cost']},
                           {row['07080_One_Off_Costs_Portfolio_Exit_Cost']},{row['07090_Ongoing_Costs_Portfolio_Transaction_Costs']},{row['07100_Ongoing_Costs_Management_Fees_And_Other_Administrative_Or_Operating_Costs']},
                           {row['07110_Incidental_Costs_Portfolio_Performance_Fees_Carried _Interest']},NULL,'{row['08010_UK_PRIIP_Or_UCITS_Or_Both_data_delivery']}',{row['08020_UK_Ongoing_Costs_Portfolio_Transaction_Costs']},'{row['08030_UK_Transactions_costs_methodology']}',
                           '{row['08040_UK_Anti_Dilution_Benefit_Derived']}','{row['08045_UK_PRIIPs_Data_Reference_Date']}','{row['08050_UK_PRIIPs_KID_Publication_Date']}','{row['08060_UK_PRIIPs_KID_Web_Address']}','{row['08070_Investment_Objective_Portfolio']}',
                           '{row['08080_UK_Other_Materially_Relevant_Risk_Narrative_Portfolio']}','{row['08090_UK_Performance_Information_Main_Factors']}','{row['08100_UK_Performance_Information_Comparator']}','{row['08110_UK_Performance_Information_Higher_Returns']}',
                           '{row['08120_UK_Performance_Information_Lower_Returns_Or_Loss']}','{row['08130_UK_Performance_Information_Adverse_Conditions']}',{row['08140_UK_Assumed_Portfolio_Return']},'{row['08150_UCITS_KIID_Publication_Date']}',
                           '{row['08160_UCITS_KIID_Web_Address']}',{row['08170_UCITS_SRRI']},{row['08180_UCITS_Ongoing_Charges']},{row['08190_UCITS_Existing_Performance_Fees']},{row['08200_UCITS_Performance_Fees']},GETDATE(),'{row['Tech_Reporting_Date']}',
                           '{row['Tech_Reporting_Date']}','{row['Tech_ID']}')) 
                           AS source ('00001_EPT_Version','00002_EPT_Producer_Name','00004_EPT_Producer_Email','00005_File_Generation_Date_And_Time','00006_EPT_Data_Reporting_Narratives','00007_EPT_Data_Reporting_Costs','00008_EPT_Data_Reporting_Additional_Requirements_German_MOPs',
                           '00009_EPT_Additional_Information_Structured_Products','00010_Portfolio_Manufacturer_Name','00015_Portfolio_Manufacturer_Group_Name','00016_Portfolio_Manufacturer_LEI','00017_Portfolio_Manufacturer_Email','00020_Portfolio_Guarantor_Name',
                           '00030_Portfolio_Identifying_Data','00040_Type_Of_Identification_Code_For_The_Fund_Share_Or_Portfolio','00050_Portfolio_Name','00060_Portfolio_Or_Share_Class_Currency','00070_PRIIPs_KID_Publication_Date','00075_PRIIPs_KID_Web_Address',
                           '00080_Portfolio_PRIIPS_Category','00090_Fund_CIC_code','00110_Is_An_Autocallable_Product','00120_Reference_Language','01010_Valuation_Frequency','01020_Portfolio_VEV_Reference','01030_IS_Flexible','01040_Flex_VEV_Historical','01050_Flex_VEV_Ref_Asset_Allocation',
                           '01060_IS_Risk_Limit_Relevant','01070_Flex_VEV_Risk_Limit','01080_Existing_Credit_Risk','01090_SRI','01095_IS_SRI_Adjusted','01100_MRM','01110_CRM','01120_Recommended_Holding_Period','01125_Has_A_Contractual_Maturity_Date','01130_Maturity_Date','01140_Liquidity_Risk',
                           '02010_Portfolio_Return_Unfavourable_Scenario_1_Year','02020_Portfolio_Return_Unfavourable_Scenario_Half_RHP','02030_Portfolio_Return_Unfavourable_Scenario_RHP_Or_First_Call_Date','02032_Autocall_Applied_Unfavourable_Scenario',
                           '02035_Autocall_Date_Unfavourable_Scenario','02040_Portfolio_return_moderate_scenario_1_year','02050_Portfolio_return_moderate_scenario_half_RHP','02060_Portfolio_Return_Moderate_Scenario_RHP_Or_First_Call_Date','02062_Autocall_Applied_Moderate_Scenario',
                           '02065_Autocall_Date_Moderate_Scenario','02070_Portfolio_Return_Favourable_Scenario_1_Year','02080_Portfolio_Return_Favourable_Scenario_Half_RHP','02090_Portfolio_Return_Favourable_Scenario_RHP_Or_First_Call_Date','02092_Autocall_Applied_Favourable_Scenario',
                           '02095_Autocall_Date_Favourable_Scenario','02100_Portfolio_return_stress_scenario_1_year','02110_Portfolio_return_stress_scenario_half_RHP','02120_Portfolio_Return_Stress_Scenario_RHP_Or_First_Call_Date','02122_Autocall_Applied_Stress_Scenario',
                           '02125_Autocall_Date_Stress_Scenario','02130_Portfolio_number_of_observed_return_M0','02140_Portfolio_mean_observed_returns_M1','02150_Portfolio_observed_Sigma','02160_Portfolio_observed_Skewness','02170_Portfolio_observed_Excess_Kurtosis',
                           '02180_Portfolio_observed_Stressed_Volatility','02185_Portfolio_Past_Performance_Disclosure_Required','02190_Past_Performance_Link','02200_Previous_Performance_Scenarios_Calculation_Link','02210_Past_Performance_Number_Of_Years','02220_Reference_Invested_Amount',
                           '03010_One_off_cost_Portfolio_entry_cost','03015_One_off_cost_Portfolio_entry_cost_Acquired','03020_One_off_costs_Portfolio_exit_cost_at_RHP','03030_One_off_costs_Portfolio_exit_cost_at_1_year','03040_One_off_costs_Portfolio_exit_cost_at_half_RHP',
                           '03050_One_off_costs_Portfolio_sliding_exit_cost_Indicator','03060_Ongoing_Costs_Management_Fees_And_Other_Administrative_Or_Operating_Costs','03070_Ongoing_costs_Portfolio_management_costs','03080_Ongoing_costs_Portfolio_transaction_costs',
                           '03090_Existing_Incidental_Costs_Portfolio','03095_Incidental_Costs','03100_Existing_carried_interest_fees','03105_Incidental_costs_Portfolio_carried_interest','04010_Reference_Language','04020_Comprehension_Alert_Portfolio',
                           '04030_Intended_target_market_retail_investor_Portfolio','04040_Investment_objective_Portfolio','04050_Risk_narrative_Portfolio','04060_Other_materially_relevant_risk_narrative_Portfolio','04070_Type_of_underlying_Investment_Option',
                           '04080_Capital_Guarantee','04081_Capital_Guarantee_Level','04082_Capital_Guarantee_Limitations','04083_Capital_Guarantee_Early_Exit_Conditions','04084_Capital_guarantee_Portfolio','04085_Possible_maximum_loss_Portfolio',
                           '04086_Description_Past_Interval_Unfavourable_Scenario','04087_Description_Past_Interval_Moderate_Scenario','04088_Description_Past_Interval_Favourable_Scenario','04089_Was_Benchmark_Used_Performance_Calculation',
                           '04090_Portfolio_Performance_Fees_Carried_Interest_Narrative','04100_Portolio_Carried_Interest_Narrative','04110_Other_comment','04120_One_Off_Cost_Portfolio_Entry_Cost_Description','04130_One_Off_Cost_Portfolio_Exit_Cost_Description',
                           '04140_Ongoing_Costs_Portfolio_Management_Costs_Description','04150_Do_Costs_Depend_On_Invested_Amount','04160_Cost_Dependence_Explanation','05010_PRIIP_data_delivery','05020_UCITS_data_delivery','05030_Portfolio_UCITS_SRRI','05040_Portfolio_UCITS_Vol',
                           '05050_Ongoing_costs_Portfolio_other_costs_UCITS','05060_Ongoing_costs_Portfolio_transaction_costs','05065_Transactions_costs_methodology','05070_Incidental_costs_Portfolio_performance_fees_UCITS','05080_Incidental_costs_Portfolio_carried_interest_UCITS',
                           '05090_UCITS_KID_Web_Address','06005_German_MOPs_Reference_Date','06010_Bonds_Weight','06020_Annualized_Return_Volatility','06030_Duration_Bonds','06040_Existing_Capital_Preservation','06050_Capital_Preservation_Level','06060_Time_Interval_Maximum_Loss',
                           '06070_Uses_PI','06080_Multiplier_PI','07005_First_Possible_Call_Date','07010_Total_Cost_1_Year_Or_First_Call','07020_RIY_1_Year_Or_First_Call','07030_Total_cost_half_RHP','07040_RIY_half_RHP','07050_Total_cost_RHP','07060_RIY_RHP','07070_One_Off_Costs_Portfolio_Entry_Cost',
                           '07080_One_off_costs_Portfolio_exit_cost_RIY','07090_Ongoing_Costs_Portfolio_Transaction_Costs','07100_Ongoing_Costs_Management_Fees_And_Other_Administrative_Or_Operating_Costs','07110_Incidental_Costs_Portfolio_Performance_Fees_Carried_Interest',
                           '07120_Incidental_costs_Portfolio_carried_interests_RIY','08010_UK_PRIIP_Or_UCITS_Or_Both_data_delivery','08020_UK_Ongoing_Costs_Portfolio_Transaction_Costs','08030_UK_Transactions_costs_methodology','08040_UK_Anti_Dilution_Benefit_Derived',
                           '08045_UK_PRIIPs_Data_Reference_Date','08050_UK_PRIIPs_KID_Publication_Date','08060_UK_PRIIPs_KID_Web_Address','08070_Investment_Objective_Portfolio','08080_UK_Other_Materially_Relevant_Risk_Narrative_Portfolio','08090_UK_Performance_Information_Main_Factors',
                           '08100_UK_Performance_Information_Comparator','08110_UK_Performance_Information_Higher_Returns','08120_UK_Performance_Information_Lower_Returns_Or_Loss','08130_UK_Performance_Information_Adverse_Conditions','08140_UK_Assumed_Portfolio_Return',
                           '08150_UCITS_KIID_Publication_Date','08160_UCITS_KIID_Web_Address','08170_UCITS_SRRI','08180_UCITS_Ongoing_Charges','08190_UCITS_Existing_Performance_Fees','08200_UCITS_Performance_Fees','Tech_Load_TimeStamp','Tech_Mnemo_Fonds_Parts','Tech_Reporting_Date','Tech_ID')
                ON target.Tech_ID = source.Tech_ID
            WHEN MATCHED THEN
                    UPDATE SET 
                        target.00001_EPT_Version = source.00001_EPT_Version, target.00002_EPT_Producer_Name = source.00002_EPT_Producer_Name, target.00004_EPT_Producer_Email = source.00004_EPT_Producer_Email,
                        target.00005_File_Generation_Date_And_Time = source.00005_File_Generation_Date_And_Time, target.00006_EPT_Data_Reporting_Narratives = source.00006_EPT_Data_Reporting_Narratives, 
                        target.00007_EPT_Data_Reporting_Costs = source.00007_EPT_Data_Reporting_Costs, target.00008_EPT_Data_Reporting_Additional_Requirements_German_MOPs = source.00008_EPT_Data_Reporting_Additional_Requirements_German_MOPs,
                        target.00009_EPT_Additional_Information_Structured_Products = source.00009_EPT_Additional_Information_Structured_Products, target.00010_Portfolio_Manufacturer_Name = source.00010_Portfolio_Manufacturer_Name, 
                        target.00015_Portfolio_Manufacturer_Group_Name = source.00015_Portfolio_Manufacturer_Group_Name, target.00016_Portfolio_Manufacturer_LEI = source.00016_Portfolio_Manufacturer_LEI, 
                        target.00017_Portfolio_Manufacturer_Email = source.00017_Portfolio_Manufacturer_Email, target.00020_Portfolio_Guarantor_Name = source.00020_Portfolio_Guarantor_Name, target.00030_Portfolio_Identifying_Data = source.00030_Portfolio_Identifying_Data,
                        target.00040_Type_Of_Identification_Code_For_The_Fund_Share_Or_Portfolio = source.00040_Type_Of_Identification_Code_For_The_Fund_Share_Or_Portfolio, target.00050_Portfolio_Name = source.00050_Portfolio_Name,
                        target.00060_Portfolio_Or_Share_Class_Currency = source.00060_Portfolio_Or_Share_Class_Currency, target.00070_PRIIPs_KID_Publication_Date = source.00070_PRIIPs_KID_Publication_Date, 
                        target.00075_PRIIPs_KID_Web_Address = source.00075_PRIIPs_KID_Web_Address, target.00080_Portfolio_PRIIPS_Category = source.00080_Portfolio_PRIIPS_Category, target.00090_Fund_CIC_code = source.00090_Fund_CIC_code, 
                        target.00110_Is_An_Autocallable_Product = source.00110_Is_An_Autocallable_Product, target.00120_Reference_Language = source.00120_Reference_Language, target.01010_Valuation_Frequency = source.01010_Valuation_Frequency, 
                        target.01020_Portfolio_VEV_Reference = source.01020_Portfolio_VEV_Reference, target.01030_IS_Flexible = source.01030_IS_Flexible, target.01040_Flex_VEV_Historical = source.01040_Flex_VEV_Historical, 
                        target.01050_Flex_VEV_Ref_Asset_Allocation = source.01050_Flex_VEV_Ref_Asset_Allocation, target.01060_IS_Risk_Limit_Relevant = source.01060_IS_Risk_Limit_Relevant, target.01070_Flex_VEV_Risk_Limit = source.01070_Flex_VEV_Risk_Limit,
                        target.01080_Existing_Credit_Risk = source.01080_Existing_Credit_Risk, target.01090_SRI = source.01090_SRI, target.01095_IS_SRI_Adjusted = source.01095_IS_SRI_Adjusted, target.01100_MRM = source.01100_MRM, target.01110_CRM = source.01110_CRM,
                        target.01120_Recommended_Holding_Period = source.01120_Recommended_Holding_Period, target.01125_Has_A_Contractual_Maturity_Date = source.01125_Has_A_Contractual_Maturity_Date, target.01130_Maturity_Date = source.01130_Maturity_Date, 
                        target.01140_Liquidity_Risk = source.01140_Liquidity_Risk, target.02010_Portfolio_Return_Unfavourable_Scenario_1_Year = source.02010_Portfolio_Return_Unfavourable_Scenario_1_Year, 
                        target.02020_Portfolio_Return_Unfavourable_Scenario_Half_RHP = source.02020_Portfolio_Return_Unfavourable_Scenario_Half_RHP,
                        target.02030_Portfolio_Return_Unfavourable_Scenario_RHP_Or_First_Call_Date = source.02030_Portfolio_Return_Unfavourable_Scenario_RHP_Or_First_Call_Date, target.02032_Autocall_Applied_Unfavourable_Scenario = source.02032_Autocall_Applied_Unfavourable_Scenario,
                        target.02035_Autocall_Date_Unfavourable_Scenario = source.02035_Autocall_Date_Unfavourable_Scenario, target.02040_Portfolio_return_moderate_scenario_1_year = source.02040_Portfolio_return_moderate_scenario_1_year, 
                        target.02050_Portfolio_return_moderate_scenario_half_RHP = source.02050_Portfolio_return_moderate_scenario_half_RHP, 
                        target.02060_Portfolio_Return_Moderate_Scenario_RHP_Or_First_Call_Date = source.02060_Portfolio_Return_Moderate_Scenario_RHP_Or_First_Call_Date, target.02062_Autocall_Applied_Moderate_Scenario = source.02062_Autocall_Applied_Moderate_Scenario, 
                        target.02065_Autocall_Date_Moderate_Scenario = source.02065_Autocall_Date_Moderate_Scenario, target.02070_Portfolio_Return_Favourable_Scenario_1_Year = source.02070_Portfolio_Return_Favourable_Scenario_1_Year, 
                        target.02080_Portfolio_Return_Favourable_Scenario_Half_RHP = source.02080_Portfolio_Return_Favourable_Scenario_Half_RHP, 
                        target.02090_Portfolio_Return_Favourable_Scenario_RHP_Or_First_Call_Date = source.02090_Portfolio_Return_Favourable_Scenario_RHP_Or_First_Call_Date, target.02092_Autocall_Applied_Favourable_Scenario = source.02092_Autocall_Applied_Favourable_Scenario, 
                        target.02095_Autocall_Date_Favourable_Scenario = source.02095_Autocall_Date_Favourable_Scenario, target.02100_Portfolio_return_stress_scenario_1_year = source.02100_Portfolio_return_stress_scenario_1_year,
                        target.02110_Portfolio_return_stress_scenario_half_RHP = source.02110_Portfolio_return_stress_scenario_half_RHP, target.02120_Portfolio_Return_Stress_Scenario_RHP_Or_First_Call_Date = source.02120_Portfolio_Return_Stress_Scenario_RHP_Or_First_Call_Date,
                        target.02122_Autocall_Applied_Stress_Scenario = source.02122_Autocall_Applied_Stress_Scenario, target.02125_Autocall_Date_Stress_Scenario = source.02125_Autocall_Date_Stress_Scenario, 
                        target.02130_Portfolio_number_of_observed_return_M0 = source.02130_Portfolio_number_of_observed_return_M0, target.02140_Portfolio_mean_observed_returns_M1 = source.02140_Portfolio_mean_observed_returns_M1,
                        target.02150_Portfolio_observed_Sigma = source.02150_Portfolio_observed_Sigma, target.02160_Portfolio_observed_Skewness = source.02160_Portfolio_observed_Skewness, 
                        target.02170_Portfolio_observed_Excess_Kurtosis = source.02170_Portfolio_observed_Excess_Kurtosis, target.02180_Portfolio_observed_Stressed_Volatility = source.02180_Portfolio_observed_Stressed_Volatility, 
                        target.02185_Portfolio_Past_Performance_Disclosure_Required = source.02185_Portfolio_Past_Performance_Disclosure_Required, target.02190_Past_Performance_Link = source.02190_Past_Performance_Link,
                        target.02200_Previous_Performance_Scenarios_Calculation_Link = source.02200_Previous_Performance_Scenarios_Calculation_Link, target.02210_Past_Performance_Number_Of_Years = source.02210_Past_Performance_Number_Of_Years,
                        target.02220_Reference_Invested_Amount = source.02220_Reference_Invested_Amount, target.03010_One_off_cost_Portfolio_entry_cost = source.03010_One_off_cost_Portfolio_entry_cost, 
                        target.03015_One_off_cost_Portfolio_entry_cost_Acquired = source.03015_One_off_cost_Portfolio_entry_cost_Acquired, target.03020_One_off_costs_Portfolio_exit_cost_at_RHP = source.03020_One_off_costs_Portfolio_exit_cost_at_RHP, 
                        target.03030_One_off_costs_Portfolio_exit_cost_at_1_year = source.03030_One_off_costs_Portfolio_exit_cost_at_1_year, target.03040_One_off_costs_Portfolio_exit_cost_at_half_RHP = source.03040_One_off_costs_Portfolio_exit_cost_at_half_RHP,
                        target.03050_One_off_costs_Portfolio_sliding_exit_cost_Indicator = source.03050_One_off_costs_Portfolio_sliding_exit_cost_Indicator, 
                        target.03060_Ongoing_Costs_Management_Fees_And_Other_Administrative_Or_Operating_Costs = source.03060_Ongoing_Costs_Management_Fees_And_Other_Administrative_Or_Operating_Costs, 
                        target.03070_Ongoing_costs_Portfolio_management_costs = source.03070_Ongoing_costs_Portfolio_management_costs, target.03080_Ongoing_costs_Portfolio_transaction_costs = source.03080_Ongoing_costs_Portfolio_transaction_costs, 
                        target.03090_Existing_Incidental_Costs_Portfolio = source.03090_Existing_Incidental_Costs_Portfolio, target.03095_Incidental_Costs = source.03095_Incidental_Costs, 
                        target.03100_Existing_carried_interest_fees = source.03100_Existing_carried_interest_fees, target.03105_Incidental_costs_Portfolio_carried_interest = source.03105_Incidental_costs_Portfolio_carried_interest,
                        target.04010_Reference_Language = source.04010_Reference_Language, target.04020_Comprehension_Alert_Portfolio = source.04020_Comprehension_Alert_Portfolio, 
                        target.04030_Intended_target_market_retail_investor_Portfolio = source.04030_Intended_target_market_retail_investor_Portfolio, target.04040_Investment_objective_Portfolio = source.04040_Investment_objective_Portfolio,
                        target.04050_Risk_narrative_Portfolio = source.04050_Risk_narrative_Portfolio, target.04060_Other_materially_relevant_risk_narrative_Portfolio = source.04060_Other_materially_relevant_risk_narrative_Portfolio,
                        target.04070_Type_of_underlying_Investment_Option = source.04070_Type_of_underlying_Investment_Option, target.04080_Capital_Guarantee = source.04080_Capital_Guarantee, target.04081_Capital_Guarantee_Level = source.04081_Capital_Guarantee_Level,
                        target.04082_Capital_Guarantee_Limitations = source.04082_Capital_Guarantee_Limitations, target.04083_Capital_Guarantee_Early_Exit_Conditions = source.04083_Capital_Guarantee_Early_Exit_Conditions,
                        target.04084_Capital_guarantee_Portfolio = source.04084_Capital_guarantee_Portfolio, target.04085_Possible_maximum_loss_Portfolio = source.04085_Possible_maximum_loss_Portfolio, 
                        target.04086_Description_Past_Interval_Unfavourable_Scenario = source.04086_Description_Past_Interval_Unfavourable_Scenario, target.04087_Description_Past_Interval_Moderate_Scenario = source.04087_Description_Past_Interval_Moderate_Scenario, 
                        target.04088_Description_Past_Interval_Favourable_Scenario = source.04088_Description_Past_Interval_Favourable_Scenario, target.04089_Was_Benchmark_Used_Performance_Calculation = source.04089_Was_Benchmark_Used_Performance_Calculation,
                        target.04090_Portfolio_Performance_Fees_Carried_Interest_Narrative = source.04090_Portfolio_Performance_Fees_Carried_Interest_Narrative, target.04100_Portolio_Carried_Interest_Narrative = source.04100_Portolio_Carried_Interest_Narrative,
                        target.04110_Other_comment = source.04110_Other_comment, target.04120_One_Off_Cost_Portfolio_Entry_Cost_Description = source.04120_One_Off_Cost_Portfolio_Entry_Cost_Description, 
                        target.04130_One_Off_Cost_Portfolio_Exit_Cost_Description = source.04130_One_Off_Cost_Portfolio_Exit_Cost_Description, target.04140_Ongoing_Costs_Portfolio_Management_Costs_Description = source.04140_Ongoing_Costs_Portfolio_Management_Costs_Description,
                        target.04150_Do_Costs_Depend_On_Invested_Amount = source.04150_Do_Costs_Depend_On_Invested_Amount, target.04160_Cost_Dependence_Explanation = source.04160_Cost_Dependence_Explanation, target.05010_PRIIP_data_delivery = source.05010_PRIIP_data_delivery, 
                        target.05020_UCITS_data_delivery = source.05020_UCITS_data_delivery, target.05030_Portfolio_UCITS_SRRI = source.05030_Portfolio_UCITS_SRRI, target.05040_Portfolio_UCITS_Vol = source.05040_Portfolio_UCITS_Vol, 
                        target.05050_Ongoing_costs_Portfolio_other_costs_UCITS = source.05050_Ongoing_costs_Portfolio_other_costs_UCITS, target.05060_Ongoing_costs_Portfolio_transaction_costs = source.05060_Ongoing_costs_Portfolio_transaction_costs,
                        target.05065_Transactions_costs_methodology = source.05065_Transactions_costs_methodology, target.05070_Incidental_costs_Portfolio_performance_fees_UCITS = source.05070_Incidental_costs_Portfolio_performance_fees_UCITS, 
                        target.05080_Incidental_costs_Portfolio_carried_interest_UCITS = source.05080_Incidental_costs_Portfolio_carried_interest_UCITS, target.05090_UCITS_KID_Web_Address = source.05090_UCITS_KID_Web_Address, 
                        target.06005_German_MOPs_Reference_Date = source.06005_German_MOPs_Reference_Date, target.06010_Bonds_Weight = source.06010_Bonds_Weight, target.06020_Annualized_Return_Volatility = source.06020_Annualized_Return_Volatility, 
                        target.06030_Duration_Bonds = source.06030_Duration_Bonds, target.06040_Existing_Capital_Preservation = source.06040_Existing_Capital_Preservation, target.06050_Capital_Preservation_Level = source.06050_Capital_Preservation_Level,
                        target.06060_Time_Interval_Maximum_Loss = source.06060_Time_Interval_Maximum_Loss, target.06070_Uses_PI = source.06070_Uses_PI, target.06080_Multiplier_PI = source.06080_Multiplier_PI, 
                        target.07005_First_Possible_Call_Date = source.07005_First_Possible_Call_Date, target.07010_Total_Cost_1_Year_Or_First_Call = source.07010_Total_Cost_1_Year_Or_First_Call, target.07020_RIY_1_Year_Or_First_Call = source.07020_RIY_1_Year_Or_First_Call,
                        target.07030_Total_cost_half_RHP = source.07030_Total_cost_half_RHP, target.07040_RIY_half_RHP = source.07040_RIY_half_RHP, target.07050_Total_cost_RHP = source.07050_Total_cost_RHP, target.07060_RIY_RHP = source.07060_RIY_RHP, 
                        target.07070_One_Off_Costs_Portfolio_Entry_Cost = source.07070_One_Off_Costs_Portfolio_Entry_Cost, target.07080_One_off_costs_Portfolio_exit_cost_RIY = source.07080_One_off_costs_Portfolio_exit_cost_RIY, 
                        target.07090_Ongoing_Costs_Portfolio_Transaction_Costs = source.07090_Ongoing_Costs_Portfolio_Transaction_Costs,
                        target.07100_Ongoing_Costs_Management_Fees_And_Other_Administrative_Or_Operating_Costs = source.07100_Ongoing_Costs_Management_Fees_And_Other_Administrative_Or_Operating_Costs,
                        target.07110_Incidental_Costs_Portfolio_Performance_Fees_Carried_Interest = source.07110_Incidental_Costs_Portfolio_Performance_Fees_Carried_Interest,
                        target.07120_Incidental_costs_Portfolio_carried_interests_RIY = source.07120_Incidental_costs_Portfolio_carried_interests_RIY, target.08010_UK_PRIIP_Or_UCITS_Or_Both_data_delivery = source.08010_UK_PRIIP_Or_UCITS_Or_Both_data_delivery, 
                        target.08020_UK_Ongoing_Costs_Portfolio_Transaction_Costs = source.08020_UK_Ongoing_Costs_Portfolio_Transaction_Costs, target.08030_UK_Transactions_costs_methodology = source.08030_UK_Transactions_costs_methodology, 
                        target.08040_UK_Anti_Dilution_Benefit_Derived = source.08040_UK_Anti_Dilution_Benefit_Derived, target.08045_UK_PRIIPs_Data_Reference_Date = source.08045_UK_PRIIPs_Data_Reference_Date, 
                        target.08050_UK_PRIIPs_KID_Publication_Date = source.08050_UK_PRIIPs_KID_Publication_Date, target.08060_UK_PRIIPs_KID_Web_Address = source.08060_UK_PRIIPs_KID_Web_Address, 
                        target.08070_Investment_Objective_Portfolio = source.08070_Investment_Objective_Portfolio, target.08080_UK_Other_Materially_Relevant_Risk_Narrative_Portfolio = source.08080_UK_Other_Materially_Relevant_Risk_Narrative_Portfolio,
                        target.08090_UK_Performance_Information_Main_Factors = source.08090_UK_Performance_Information_Main_Factors, target.08100_UK_Performance_Information_Comparator = source.08100_UK_Performance_Information_Comparator,
                        target.08110_UK_Performance_Information_Higher_Returns = source.08110_UK_Performance_Information_Higher_Returns, target.08120_UK_Performance_Information_Lower_Returns_Or_Loss = source.08120_UK_Performance_Information_Lower_Returns_Or_Loss,
                        target.08130_UK_Performance_Information_Adverse_Conditions = source.08130_UK_Performance_Information_Adverse_Conditions, target.08140_UK_Assumed_Portfolio_Return = source.08140_UK_Assumed_Portfolio_Return, 
                        target.08150_UCITS_KIID_Publication_Date = source.08150_UCITS_KIID_Publication_Date, target.08160_UCITS_KIID_Web_Address = source.08160_UCITS_KIID_Web_Address, target.08170_UCITS_SRRI = source.08170_UCITS_SRRI,
                        target.08180_UCITS_Ongoing_Charges = source.08180_UCITS_Ongoing_Charges, target.08190_UCITS_Existing_Performance_Fees = source.08190_UCITS_Existing_Performance_Fees, target.08200_UCITS_Performance_Fees = source.08200_UCITS_Performance_Fees,
                        target.Tech_Load_TimeStamp = source.Tech_Load_TimeStamp, target.Tech_Mnemo_Fonds_Parts = source.Tech_Mnemo_Fonds_Parts, target.Tech_Reporting_Date = source.Tech_Reporting_Date, target.Tech_ID = source.Tech_ID


            WHEN NOT MATCHED THEN
                INSERT (00001_EPT_Version,00002_EPT_Producer_Name,00004_EPT_Producer_Email,00005_File_Generation_Date_And_Time,00006_EPT_Data_Reporting_Narratives,00007_EPT_Data_Reporting_Costs,00008_EPT_Data_Reporting_Additional_Requirements_German_MOPs,
                00009_EPT_Additional_Information_Structured_Products,00010_Portfolio_Manufacturer_Name,00015_Portfolio_Manufacturer_Group_Name,00016_Portfolio_Manufacturer_LEI,00017_Portfolio_Manufacturer_Email,00020_Portfolio_Guarantor_Name,
                00030_Portfolio_Identifying_Data,00040_Type_Of_Identification_Code_For_The_Fund_Share_Or_Portfolio,00050_Portfolio_Name,00060_Portfolio_Or_Share_Class_Currency,00070_PRIIPs_KID_Publication_Date,00075_PRIIPs_KID_Web_Address,00080_Portfolio_PRIIPS_Category,
                00090_Fund_CIC_code,00110_Is_An_Autocallable_Product,00120_Reference_Language,01010_Valuation_Frequency,01020_Portfolio_VEV_Reference,01030_IS_Flexible,01040_Flex_VEV_Historical,01050_Flex_VEV_Ref_Asset_Allocation,01060_IS_Risk_Limit_Relevant,
                01070_Flex_VEV_Risk_Limit,01080_Existing_Credit_Risk,01090_SRI,01095_IS_SRI_Adjusted,01100_MRM,01110_CRM,01120_Recommended_Holding_Period,01125_Has_A_Contractual_Maturity_Date,01130_Maturity_Date,01140_Liquidity_Risk,
                02010_Portfolio_Return_Unfavourable_Scenario_1_Year,02020_Portfolio_Return_Unfavourable_Scenario_Half_RHP,02030_Portfolio_Return_Unfavourable_Scenario_RHP_Or_First_Call_Date,02032_Autocall_Applied_Unfavourable_Scenario,
                02035_Autocall_Date_Unfavourable_Scenario,02040_Portfolio_return_moderate_scenario_1_year,02050_Portfolio_return_moderate_scenario_half_RHP,02060_Portfolio_Return_Moderate_Scenario_RHP_Or_First_Call_Date,02062_Autocall_Applied_Moderate_Scenario,
                02065_Autocall_Date_Moderate_Scenario,02070_Portfolio_Return_Favourable_Scenario_1_Year,02080_Portfolio_Return_Favourable_Scenario_Half_RHP,02090_Portfolio_Return_Favourable_Scenario_RHP_Or_First_Call_Date,02092_Autocall_Applied_Favourable_Scenario,
                02095_Autocall_Date_Favourable_Scenario,02100_Portfolio_return_stress_scenario_1_year,02110_Portfolio_return_stress_scenario_half_RHP,02120_Portfolio_Return_Stress_Scenario_RHP_Or_First_Call_Date,02122_Autocall_Applied_Stress_Scenario,
                02125_Autocall_Date_Stress_Scenario,02130_Portfolio_number_of_observed_return_M0,02140_Portfolio_mean_observed_returns_M1,02150_Portfolio_observed_Sigma,02160_Portfolio_observed_Skewness,02170_Portfolio_observed_Excess_Kurtosis,
                02180_Portfolio_observed_Stressed_Volatility,02185_Portfolio_Past_Performance_Disclosure_Required,02190_Past_Performance_Link,02200_Previous_Performance_Scenarios_Calculation_Link,02210_Past_Performance_Number_Of_Years,
                02220_Reference_Invested_Amount,03010_One_off_cost_Portfolio_entry_cost,03015_One_off_cost_Portfolio_entry_cost_Acquired,03020_One_off_costs_Portfolio_exit_cost_at_RHP,03030_One_off_costs_Portfolio_exit_cost_at_1_year,
                03040_One_off_costs_Portfolio_exit_cost_at_half_RHP,03050_One_off_costs_Portfolio_sliding_exit_cost_Indicator,03060_Ongoing_Costs_Management_Fees_And_Other_Administrative_Or_Operating_Costs,03070_Ongoing_costs_Portfolio_management_costs,
                03080_Ongoing_costs_Portfolio_transaction_costs,03090_Existing_Incidental_Costs_Portfolio,03095_Incidental_Costs,03100_Existing_carried_interest_fees,03105_Incidental_costs_Portfolio_carried_interest,04010_Reference_Language,
                04020_Comprehension_Alert_Portfolio,04030_Intended_target_market_retail_investor_Portfolio,04040_Investment_objective_Portfolio,04050_Risk_narrative_Portfolio,04060_Other_materially_relevant_risk_narrative_Portfolio,
                04070_Type_of_underlying_Investment_Option,04080_Capital_Guarantee,04081_Capital_Guarantee_Level,04082_Capital_Guarantee_Limitations,04083_Capital_Guarantee_Early_Exit_Conditions,04084_Capital_guarantee_Portfolio,
                04085_Possible_maximum_loss_Portfolio,04086_Description_Past_Interval_Unfavourable_Scenario,04087_Description_Past_Interval_Moderate_Scenario,04088_Description_Past_Interval_Favourable_Scenario,04089_Was_Benchmark_Used_Performance_Calculation,
                04090_Portfolio_Performance_Fees_Carried_Interest_Narrative,04100_Portolio_Carried_Interest_Narrative,04110_Other_comment,04120_One_Off_Cost_Portfolio_Entry_Cost_Description,04130_One_Off_Cost_Portfolio_Exit_Cost_Description,
                04140_Ongoing_Costs_Portfolio_Management_Costs_Description,04150_Do_Costs_Depend_On_Invested_Amount,04160_Cost_Dependence_Explanation,05010_PRIIP_data_delivery,05020_UCITS_data_delivery,05030_Portfolio_UCITS_SRRI,05040_Portfolio_UCITS_Vol,
                05050_Ongoing_costs_Portfolio_other_costs_UCITS,05060_Ongoing_costs_Portfolio_transaction_costs,05065_Transactions_costs_methodology,05070_Incidental_costs_Portfolio_performance_fees_UCITS,05080_Incidental_costs_Portfolio_carried_interest_UCITS,
                05090_UCITS_KID_Web_Address,06005_German_MOPs_Reference_Date,06010_Bonds_Weight,06020_Annualized_Return_Volatility,06030_Duration_Bonds,06040_Existing_Capital_Preservation,06050_Capital_Preservation_Level,06060_Time_Interval_Maximum_Loss,06070_Uses_PI,
                06080_Multiplier_PI,07005_First_Possible_Call_Date,07010_Total_Cost_1_Year_Or_First_Call,07020_RIY_1_Year_Or_First_Call,07030_Total_cost_half_RHP,07040_RIY_half_RHP,07050_Total_cost_RHP,07060_RIY_RHP,07070_One_Off_Costs_Portfolio_Entry_Cost,
                07080_One_off_costs_Portfolio_exit_cost_RIY,07090_Ongoing_Costs_Portfolio_Transaction_Costs,07100_Ongoing_Costs_Management_Fees_And_Other_Administrative_Or_Operating_Costs,07110_Incidental_Costs_Portfolio_Performance_Fees_Carried_Interest,
                07120_Incidental_costs_Portfolio_carried_interests_RIY,08010_UK_PRIIP_Or_UCITS_Or_Both_data_delivery,08020_UK_Ongoing_Costs_Portfolio_Transaction_Costs,08030_UK_Transactions_costs_methodology,08040_UK_Anti_Dilution_Benefit_Derived,08045_UK_PRIIPs_Data_Reference_Date,
                08050_UK_PRIIPs_KID_Publication_Date,08060_UK_PRIIPs_KID_Web_Address,08070_Investment_Objective_Portfolio,08080_UK_Other_Materially_Relevant_Risk_Narrative_Portfolio,08090_UK_Performance_Information_Main_Factors,08100_UK_Performance_Information_Comparator,
                08110_UK_Performance_Information_Higher_Returns,08120_UK_Performance_Information_Lower_Returns_Or_Loss,08130_UK_Performance_Information_Adverse_Conditions,08140_UK_Assumed_Portfolio_Return,08150_UCITS_KIID_Publication_Date,08160_UCITS_KIID_Web_Address,
                08170_UCITS_SRRI,08180_UCITS_Ongoing_Charges,08190_UCITS_Existing_Performance_Fees,08200_UCITS_Performance_Fees,Tech_Load_TimeStamp,Tech_Mnemo_Fonds_Parts,Tech_Reporting_Date,Tech_ID)

                VALUES ('{row['00001_EPT_Version']}','{row['00002_EPT_Producer_Name']}','{row['00004_EPT_Producer_Email']}','{row['00005_File_Generation_Date_And_Time']}','{row['00006_EPT_Data_Reporting_Narratives']}',
                           '{row['00007_EPT_Data_Reporting_Costs']}','{row['00008_EPT_Data_Reporting_Additional_Requirements_German_MOPs']}','{row['00009_EPT_Additional_Information_Structured_Products']}','{row['00010_Portfolio_Manufacturer_Name']}',
                           '{row['00015_Portfolio_Manufacturer_Group_Name']}','{row['00016_Portfolio_Manufacturer_LEI']}','{row['00017_Portfolio_Manufacturer_Email']}','{row['00020_Portfolio_Guarantor_Name']}','{row['00030_Portfolio_Identifying_Data']}',
                           {row['00040_Type_Of_Identification_Code_For_The_Fund_Share_Or_Portfolio']},'{row['00050_Portfolio_Name']}','{row['00060_Portfolio_Or_Share_Class_Currency']}','{row['00070_PRIIPs_KID_Publication_Date']}',
                           '{row['00075_PRIIPs_KID_Web_Address']}',{row['00080_Portfolio_PRIIPS_Category']},'{row['00090_Fund_CIC_code']}','{row['00110_Is_An_Autocallable_Product']}','{row['00120_Reference_Language']}',{row['01010_Valuation_Frequency']},
                           {row['01020_Portfolio_VEV_Reference']},'{row['01030_IS_Flexible']}',{row['01040_Flex_VEV_Historical']},{row['01050_Flex_VEV_Ref_Asset_Allocation']},'{row['01060_IS_Risk_Limit_Relevant']}',{row['01070_Flex_VEV_Risk_Limit']},
                           '{row['01080_Existing_Credit_Risk']}',{row['01090_SRI']},'{row['01095_IS_SRI_Adjusted']}',{row['01100_MRM']},{row['01110_CRM']},{row['01120_Recommended_Holding_Period']},'{row['01125_Has_A_Contractual_Maturity_Date']}',
                           '{row['01130_Maturity_Date']}','{row['01140_Liquidity_Risk']}',{row['02010_Portfolio_Return_Unfavourable_Scenario_1_Year']},{row['02020_Portfolio_Return_Unfavourable_Scenario_Half_RHP']},
                           {row['02030_Portfolio_Return_Unfavourable_Scenario_RHP_Or_First_Call_Date']},'{row['02032_Autocall_Applied_Unfavourable_Scenario']}','{row['02035_Autocall_Date_Unfavourable_Scenario']}',{row['02040_Portfolio_Return_Moderate_Scenario_1_Year']},
                           {row['02050_Portfolio_Return_Moderate_Scenario_Half_RHP']},{row['02060_Portfolio_Return_Moderate_Scenario_RHP_Or_First_Call_Date']},'{row['02062_Autocall_Applied_Moderate_Scenario']}','{row['02065_Autocall_Date_Moderate_Scenario']}',
                           {row['02070_Portfolio_Return_Favourable_Scenario_1_Year']},{row['02080_Portfolio_Return_Favourable_Scenario_Half_RHP']},{row['02090_Portfolio_Return_Favourable_Scenario_RHP_Or_First_Call_Date']},'{row['02092_Autocall_Applied_Favourable_Scenario']}',
                           '{row['02095_Autocall_Date_Favourable_Scenario']}',{row['02100_Portfolio_return_stress_scenario_1_year']},{row['02110_Portfolio_return_stress_scenario_half_RHP']},{row['02120_Portfolio_Return_Stress_Scenario_RHP_Or_First_Call_Date']},
                           '{row['02122_Autocall_Applied_Stress_Scenario']}','{row['02125_Autocall_Date_Stress_Scenario']}',{row['02130_Portfolio_Number_Of_Observed_Return_M0']},{row['02140_Portfolio_Mean_Observed_Returns_M1']},{row['02150_Portfolio_Observed_Sigma']},
                           {row['02160_Portfolio_Observed_Skewness']},{row['02170_Portfolio_Observed_Excess_Kurtosis']},{row['02180_Portfolio_Observed_Stressed_Volatility']},'{row['02185_Portfolio_Past_Performance_Disclosure_Required']}',
                           '{row['02190_Past_Performance_Link']}','{row['02200_Previous_Performance_Scenarios_Calculation_Link']}',{row['02210_Past_Performance_Number_Of_Years']},{row['02220_Reference_Invested_Amount']},{row['03010_One_off_cost_Portfolio_entry_cost']},
                           {row['03015_One_off_cost_Portfolio_entry_cost_Acquired']},{row['03020_One_off_costs_Portfolio_exit_cost_at_RHP']},{row['03030_One_off_costs_Portfolio_exit_cost_at_1_year']},{row['03040_One_off_costs_Portfolio_exit_cost_at_half_RHP']},
                           '{row['03050_One_off_costs_Portfolio_sliding_exit_cost_Indicator']}',{row['03060_Ongoing_Costs_Management_Fees_And_Other_Administrative_Or_Operating_Costs']},NULL,{row['03080_Ongoing_costs_Portfolio_transaction_costs']},
                           '{row['03090_Existing_Incidental_Costs_Portfolio']}',{row['03095_Incidental_costs']},NULL,NULL,NULL,'{row['04020_Comprehension_Alert_Portfolio']}','{row['04030_Intended_target_market_retail_investor_Portfolio']}',
                           '{row['04040_Investment_objective_Portfolio']}','{row['04050_Risk_narrative_Portfolio']}','{row['04060_Other_materially_relevant_risk_narrative_Portfolio']}','{row['04070_Type_of_underlying_Investment_Option']}',
                           '{row['04080_Capital_Guarantee']}',{row['04081_Capital_Guarantee_Level']},'{row['04082_Capital_Guarantee_Limitations']}','{row['04083_Capital_Guarantee_Early_Exit_Conditions']}','{row['04084_Capital_guarantee_Portfolio']}',
                           {row['04085_Possible_maximum_loss_Portfolio']},'{row['04086_Description_Past_Interval_Unfavourable_Scenario']}','{row['04087_Description_Past_Interval_Moderate_Scenario']}','{row['04088_Description_Past_Interval_Favourable_Scenario']}',
                           '{row['04089_Was_Benchmark_Used_Performance_Calculation']}','{row['04090_Portfolio_Performance_Fees_Carried_Interest_Narrative']}',NULL,NULL,'{row['04120_One_Off_Cost_Portfolio_Entry_Cost_Description']}',
                           '{row['04130_One_Off_Cost_Portfolio_Exit_Cost_Description']}','{row['04140_Ongoing_Costs_Portfolio_Management_Costs_Description']}','{row['04150_Do_Costs_Depend_On_Invested_Amount']}','{row['04160_Cost_Dependence_Explanation']}',
                           NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'{row['06005_German_MOPs_Reference_Date']}',{row['06010_Bonds_Weight']},{row['06020_Annualized_Return_Volatility']},{row['06030_Duration_Bonds']},'{row['06040_Existing_Capital_Preservation']}',
                           {row['06050_Capital_Preservation_Level']},{row['06060_Time_Interval_Maximum_Loss']},'{row['06070_Uses_PI']}',{row['06080_Multiplier_PI']},'{row['07005_First_Possible_Call_Date']}',{row['07010_Total_Cost_1_Year_Or_First_Call']},
                           {row['07020_RIY_1_Year_Or_First_Call']},{row['07030_Total_Cost_Half_RHP']},{row['07040_RIY_Half_RHP']},{row['07050_Total_Cost_RHP']},{row['07060_RIY_RHP']},{row['07070_One_Off_Costs_Portfolio_Entry_Cost']},
                           {row['07080_One_Off_Costs_Portfolio_Exit_Cost']},{row['07090_Ongoing_Costs_Portfolio_Transaction_Costs']},{row['07100_Ongoing_Costs_Management_Fees_And_Other_Administrative_Or_Operating_Costs']},
                           {row['07110_Incidental_Costs_Portfolio_Performance_Fees_Carried _Interest']},NULL,'{row['08010_UK_PRIIP_Or_UCITS_Or_Both_data_delivery']}',{row['08020_UK_Ongoing_Costs_Portfolio_Transaction_Costs']},'{row['08030_UK_Transactions_costs_methodology']}',
                           '{row['08040_UK_Anti_Dilution_Benefit_Derived']}','{row['08045_UK_PRIIPs_Data_Reference_Date']}','{row['08050_UK_PRIIPs_KID_Publication_Date']}','{row['08060_UK_PRIIPs_KID_Web_Address']}','{row['08070_Investment_Objective_Portfolio']}',
                           '{row['08080_UK_Other_Materially_Relevant_Risk_Narrative_Portfolio']}','{row['08090_UK_Performance_Information_Main_Factors']}','{row['08100_UK_Performance_Information_Comparator']}','{row['08110_UK_Performance_Information_Higher_Returns']}',
                           '{row['08120_UK_Performance_Information_Lower_Returns_Or_Loss']}','{row['08130_UK_Performance_Information_Adverse_Conditions']}',{row['08140_UK_Assumed_Portfolio_Return']},'{row['08150_UCITS_KIID_Publication_Date']}',
                           '{row['08160_UCITS_KIID_Web_Address']}',{row['08170_UCITS_SRRI']},{row['08180_UCITS_Ongoing_Charges']},{row['08190_UCITS_Existing_Performance_Fees']},{row['08200_UCITS_Performance_Fees']},GETDATE(),'{row['Tech_Reporting_Date']}',
                           '{row['Tech_Reporting_Date']}','{row['Tech_ID']}');
            """

        merge_query = merge_query.replace("'None'", "NULL")
        merge_query = merge_query.replace("None", "NULL")
        merge_query = merge_query.replace("'nan'", "NULL")
        merge_query = merge_query.replace("nan", "NULL")
        merge_query = merge_query.replace("'NaT'", "NULL")
        print(merge_query)





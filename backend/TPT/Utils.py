
import warnings
import pyodbc

import re
import tkinter as tk
import pandas as pd

from tkinter import simpledialog, ttk
from datetime import datetime, timedelta

print('================================')
print('start')
print('================================')

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
                          f'Trusted_Connection=yes;')
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

def Get_Ref_Product(List_Key_Valeur, List_Labels=['*'], Server='10.130.1.20',
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
                          f'Trusted_Connection=yes;')
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


def Get_Ref_Data_Histo(List_Key_Valeur, Date, Server='10.130.1.20', database='MandarineGestion_Datawarehouse'):
    """
    This function retrieves reference product data based on the provided key values.

    Parameters:
    - List_Key_Valeur (list): A list of Id_Ref_Valeur values to find in the reference database.
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
                          f'Trusted_Connection=yes;')
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


def Get_Ptf(fund_id, Date, List_Labels=['*']):
    """
    This function retrieves data of a specific portfolio (Ptf) from the database
    based on the provided portfolio name, date, and optional list of labels.

    Parameters:
    - fund_id (str): The ID of the investment portfolio to retrieve data from.
    - Date (str): The date for which to retrieve portfolio data in the format 'YYYY-MM-DD'.
    - List_Labels (list): A list of labels specifying the columns to retrieve (default is ['*'] for all columns).

    Returns:
    - df (pd.DataFrame): A pandas DataFrame containing the portfolio data for the specified name and date.
    """
    Server = '10.130.1.20'
    database = 'MandarineGestion_Datawarehouse'
    Str_Labels = ', '.join(List_Labels)
    Ptf_Name = " WHERE fund_id = '" + str(fund_id) + "'"
    Ptf_Date = " AND Date_Contrib = '" + Date + "' AND Id_Ref_Valeur IS NOT NULL"  # AND Positions_Fo <> 0
    # Establish a connection to the SQL Server database
    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                          f'SERVER={Server};'
                          f'DATABASE={database};'
                          f'Trusted_Connection=yes;')
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


def Get_Fund_Details(Key_Fund, List_Labels=['*']):
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
    requete_SQL = "SELECT " + Str_Labels + " FROM Ref_Funds RF LEFT JOIN (SELECT * FROM Ref_Partenaires WHERE categorie = 'DEPOSITAIRE' ) RP ON RF.Nom_Depositaire = RP.nom_court " + Ptf_Name

    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                          f'SERVER={Server};'
                          f'DATABASE={database};'
                          f'Trusted_Connection=yes;')
    cursor = conn.cursor()
    cursor.execute(requete_SQL)
    results = cursor.fetchall()
    results = [list(row) for row in results]
    columns = [column[0] for column in cursor.description]
    cursor.close()
    conn.close()
    df = pd.DataFrame(results, columns=columns)


def Get_Fund_List(List_Labels=['*'], PTF_Reel=1, Open_Fund=1, Public_Dedie=None, Freq_VL=None, Additionnal_Filter=None):
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
    List_Labels = ['*']
    requete_SQL = f"""SELECT RF.{', '.join(List_Labels)},
        RP.lei AS '140_Custodian_identification_code',
        CASE WHEN RP.lei IS NULL THEN 9 ELSE 1 END AS '141_Type_of_custodian_identification_code',
        '0' AS '142_Bail-in_Rule',
        NULL AS '143_Maturity_date_expected',
        NULL AS '144_Modified_duration_to_maturity_date_expected',
        NULL AS '145_Credit_sensitivity_expected',
        NULL AS '146_PIK',
        NULL AS '147_Infrastructure_investment_additional_QRT',
        NULL AS '148_Economic_sector_NACE2.1' FROM Ref_Funds RF LEFT JOIN (SELECT * FROM Ref_Partenaires WHERE categorie = 'DEPOSITAIRE' ) RP ON RF.Nom_Depositaire = RP.nom_court WHERE 1=1"""

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
                          f'Trusted_Connection=yes;')
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


def Get_Fund_Part_List(Key_Fund, List_Labels=['*'], Statut_Part='Active', Code_Part=None, Public_Dedie=None,
                       Additionnal_Filter=None):
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
                          f'Trusted_Connection=yes;')
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


def Get_Last_Nav_Date(fund_id, Date):
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
                              f'Trusted_Connection=yes;')
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


def Get_Funds_VL(ref_funds_part_id, Date, List_Labels=['*']):
    '''
    Function to retrieve fund values based on the reference funds part ID and a specific date.
    Parameters:
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
                              f'Trusted_Connection=yes;')
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


def Get_Ref_Pays():
    '''
    Function to retrieve reference data for countries from a SQL Server database.

    Returns:
    - pd.DataFrame: A pandas DataFrame containing reference data for countries.
    '''
    Server = '10.130.1.20'
    database = 'MandarineGestion_Datawarehouse'
    requete_SQL = "SELECT * FROM Ref_Pays"
    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                          f'SERVER={Server};'
                          f'DATABASE={database};'
                          f'Trusted_Connection=yes;')
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
                              f'Trusted_Connection=yes;')
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
                print(f"\nAucune valeur n'a été retournée par la requête {change} a la date : {date}.")
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
            cleaned = nace_code.strip().replace(".", "")
            if len(cleaned) > 1 and cleaned[0].isalpha() and cleaned[1:].isdigit():
                return cleaned
            elif cleaned and cleaned[0].isalpha():  # retourne uniquement si c'est une lettre
                return cleaned[0]
            else:
                return None
        else:
            # warnings.warn('NACE code is empty')
            return None


def Process_Economic_Area_Code(val):
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
    Ref_Pays = Get_Ref_Pays()
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


def Get_Economic_Area_Code_Opti():
    '''

    '''
    Ref_Pays = Get_Ref_Pays()
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
                          f'Trusted_Connection=yes;')

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

    Sql_Query = f"SELECT RF.Key_Valeur, RTG.Rtg_MDY , RTG.Rtg_SP , RTG.Rtg_Fitch , RTG.Rtg_MG_1 FROM Tb_MO_Rating AS RTG LEFT JOIN Ref_Valeurs AS RF ON RF.Code_ISIN_Valeur = RTG.Isin WHERE RTG.Date_Rating = '{Date}' AND RTG.Isin IN {List_Oblig}  AND ( RF.Date_Echeance IS NULL OR RF.Date_Echeance >= GETDATE()) ORDER BY RF.Key_Valeur"

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

# Function to map custodian names to countries
def map_custodian_to_country(custodian_name):
    correspondence_data = {
        "133_custodian_name": ["Bank Of New York Mellon", "BNP Paribas", "BNP Paribas Succursale de Luxembourg",
                               "CACEIS Bank", "Caceis Bank France", "Caceis Bank Luxembourg"],
        "123a_Fund_custodian_country": ["US", "FR", "LU", "FR", "FR", "LU"]}
    correspondence_df = pd.DataFrame(correspondence_data)
    correspondence_dict = dict(
        zip(correspondence_df["133_custodian_name"], correspondence_df["123a_Fund_custodian_country"]))

    return correspondence_dict.get(custodian_name, None)


def get_public_dedie_list():
    Server = '10.130.1.20'
    database = 'MandarineGestion_Datawarehouse'
    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                          f'SERVER={Server};'
                          f'DATABASE={database};'
                          f'Trusted_Connection=yes')

    Sql_Query = f"""
    SELECT 
	Mnemo_Fund,
	CASE WHEN TRIM(UPPER(Public_Dedie)) = 'P' THEN 'Public' ELSE 'Dédié' END AS Public_Dedie
    FROM Ref_Funds 
    WHERE PTF_Reel = 1
    """
    cursor = conn.cursor()
    cursor.execute(Sql_Query)
    results = cursor.fetchall()
    results = [list(row) for row in results]
    columns = [column[0] for column in cursor.description]
    cursor.close()
    conn.close()
    status_dict = {mnemo: statut for mnemo, statut in results}
    return status_dict


def Transform_Rating(Rtg):
    Transformation_Vector = {}



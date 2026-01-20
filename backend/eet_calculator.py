import pandas as pd
import datetime as dt
import re
import dwh_connect as dc


def get_datafunds(fund, lib):
    """Récupère une donnée spécifique d'un fonds depuis Ref_Funds"""
    sql_str = f""" select {lib} from Ref_Funds where Mnemo_Fund='{fund}' """
    cnxn = dc.connect_dwh()
    df = pd.read_sql(sql_str, cnxn)
    return df.iloc[0, 0]


def get_active_part(fund):
    """Récupère les parts actives d'un fonds"""
    sql_str = f""" SELECT Mnemo_Fund_Part FROM Ref_Funds_Parts WHERE Mnemo_Fund_Group='{fund}' AND Statut_Part = 'Active'"""
    cnxn = dc.connect_dwh()
    df = pd.read_sql(sql_str, cnxn)
    return df['Mnemo_Fund_Part'].tolist()


def get_eet_fields(EET_version='EET_1_1_3'):
    """Récupère les champs EET pour une version donnée"""
    query = f"""SELECT * FROM tb_eet_fields where version ='{EET_version}'"""
    cnxn = dc.connect_dwh()
    df = pd.read_sql(query, cnxn)
    return df


def controle_result(result, liste):
    """Vérifie si le résultat est dans la liste de valeurs autorisées"""
    liste = liste.replace('[', '').replace(']', '').replace(';', ',')
    mavar_list = liste.split(',')
    if result in mavar_list:
        return result
    else:
        return ''


def query_return(query_string, mavar, eet_field=None, override=False, key_fund=None, connect=None):
    """Exécute une requête SQL dynamique basée sur query_string"""
    # Séparer les différentes parties de la chaîne
    parts = query_string.split(';')

    # Initialiser les variables
    table = ''
    field = ''
    condition = ''
    verification = ''
    dflt = ''
    inverse = False

    # Parcourir chaque partie pour extraire les informations
    for part in parts:
        if part.startswith('TABLE '):
            table = part.replace('TABLE ', '').strip()
        elif part.startswith('FIELD '):
            field = part.replace('FIELD ', '').strip()
        elif part.startswith('ONKEY '):
            condition = part.replace('ONKEY ', '').strip()
            condition = condition.replace('&', 'and')
            condition = condition.replace('||', 'or')
            for i, var in enumerate(mavar, start=1):
                condition = condition.replace(f'[mavar{i}]', f"'{var}'")
            condition = condition.replace('[', "'")
            condition = condition.replace(']', "'")
        elif part.startswith('TESTS '):
            verification = part.replace('TESTS ', '').strip()
        elif part.startswith('DFLT '):
            dflt = part.replace('DFLT ', '').strip()
            dflt_match = re.search(r'\[(\d+)\]', dflt)
            dflt = int(dflt_match.group(1)) if dflt_match else ''
        elif part.startswith('INV '):
            inverse = True

    # Construire la requête SQL
    sql_query = f"select {field} from {table} where {condition}"

    # Gestion des max date pour tb_eet_data
    if table == 'tb_eet_data':
        sql_max_date = f"date_data = (select max(date_data) from {table} where {condition})"
        sql_query = sql_query + ' and ' + sql_max_date

    df = pd.read_sql(sql_query, connect)

    if df.shape[0] == 1:
        if verification != "":
            result = controle_result(df.iloc[0, 0], verification)
        else:
            if pd.isnull(df.iloc[0, 0]):
                result = ''
            else:
                result = df.iloc[0, 0]
        if inverse:
            result = 1 - result
    else:
        result = ''
        if dflt != '':
            result = dflt

    # Gestion des overrides
    if override and eet_field is not None:
        sql_query = f"""select top 1 eet_value from tb_eet_override
                        where eet_field ='{eet_field}' and ref_fund_id= '{key_fund}'
                        order by id desc """
        df_override = pd.read_sql(sql_query, connect)
        if df_override.shape[0] == 1:
            result = df_override.iloc[0, 0]

    return result


def Calcul_df_final(funds, EET_version, date_calcul='31/12/2024'):
    """Calcule le dataframe final avec les résultats pour chaque fonds"""
    df_calcul = EET_version
    cnxn = dc.connect_dwh()

    for fund in funds:
        keyfund = get_datafunds(fund, 'Key_Fund')
        lib_fund = get_datafunds(fund, 'Lib_Fund')
        lib_fund_str = lib_fund.replace(' ', '-').lower()

        liste_part = get_active_part(fund)
        col_dep = df_calcul.shape[1]

        for part in liste_part:
            df_calcul.insert(df_calcul.shape[1], part, [None] * len(df_calcul))
        col_fin = df_calcul.shape[1]

        # Gestion des valeurs fixes
        fixed_value_rows = df_calcul['is_fixed_value'] == '1'
        for col in df_calcul.columns[col_dep:col_fin]:
            df_calcul.loc[fixed_value_rows, col] = df_calcul.loc[fixed_value_rows, 'value_source']

        # Gestion des dates
        fixed_value_rows = df_calcul['value_source'] == 'Date(now)'
        for col in df_calcul.columns[col_dep:col_fin]:
            df_calcul.loc[fixed_value_rows, col] = dt.date.today()

        fixed_value_rows = df_calcul['value_source'] == 'Date(calcul)'
        for col in df_calcul.columns[col_dep:col_fin]:
            df_calcul.loc[fixed_value_rows, col] = date_calcul

        # Calculs pour chaque colonne
        for column in df_calcul.columns[col_dep:col_fin]:
            # Ref_funds
            df_calcul.loc[df_calcul['value_source'].str.startswith('TABLE ref_funds;', na=False), column] = \
                df_calcul.loc[df_calcul['value_source'].str.startswith('TABLE ref_funds;', na=False)].apply(
                    lambda row: query_return(row['value_source'], [fund], connect=cnxn), axis=1)

            df_calcul.loc[df_calcul['value_source'].str.startswith('TABLE ref_funds_p', na=False), column] = \
                df_calcul.loc[df_calcul['value_source'].str.startswith('TABLE ref_funds_p', na=False)].apply(
                    lambda row: query_return(row['value_source'], [column], connect=cnxn), axis=1)

            # tb_eet_data
            df_calcul.loc[df_calcul['value_source'].str.startswith('TABLE tb_eet_data;', na=False), column] = \
                df_calcul.loc[df_calcul['value_source'].str.startswith('TABLE tb_eet_data;', na=False)].apply(
                    lambda row: query_return(row['value_source'], [keyfund, row['field_name']], connect=cnxn), axis=1)

            # URLs https
            df_calcul.loc[df_calcul['value_source'].str.startswith('https://', na=False), column] = \
                df_calcul.loc[df_calcul['value_source'].str.startswith('https://', na=False)].apply(
                    lambda row: row['value_source'].replace('[mavar]', lib_fund_str), axis=1)

            # Tb_ESG_Histo_Ptf
            df_calcul.loc[df_calcul['value_source'].str.startswith('TABLE Tb_ESG_Histo_Ptf', na=False), column] = \
                df_calcul.loc[df_calcul['value_source'].str.startswith('TABLE Tb_ESG_Histo_Ptf', na=False)].apply(
                    lambda row: query_return(row['value_source'], [fund, date_calcul],
                                           eet_field=row['field_name'], override=True,
                                           key_fund=keyfund, connect=cnxn), axis=1)

            # tb_esg_calculs_indicateurs
            df_calcul.loc[df_calcul['value_source'].str.startswith('TABLE tb_esg_calculs_indicateurs', na=False), column] = \
                df_calcul.loc[df_calcul['value_source'].str.startswith('TABLE tb_esg_calculs_indicateurs', na=False)].apply(
                    lambda row: query_return(row['value_source'], [fund, date_calcul],
                                           eet_field=row['field_name'], connect=cnxn), axis=1)

    df_tmp = df_calcul
    df_calcul = df_calcul[['field_name'] + list(df_calcul.columns[9:])]
    return df_calcul, df_tmp


def calculate_fund_results(fund, version='EET_1_1_3', date_calcul='31/12/2024'):
    """
    Calcule les résultats pour un seul fonds
    Retourne un dictionnaire {field_name: résultat}
    """
    try:
        df_eet = get_eet_fields(version)
        df_final, df_tmp = Calcul_df_final([fund], df_eet, date_calcul)

        # Créer un dictionnaire field_name -> résultat
        # On prend la première colonne de résultat (après field_name)
        results = {}
        if df_final.shape[1] > 1:
            result_column = df_final.columns[1]  # Première colonne après field_name
            for idx, row in df_final.iterrows():
                field_name = row['field_name']
                result_value = row[result_column]
                results[field_name] = result_value if pd.notna(result_value) else ''

        return results
    except Exception as e:
        print(f"Erreur dans calculate_fund_results: {str(e)}")
        return {}

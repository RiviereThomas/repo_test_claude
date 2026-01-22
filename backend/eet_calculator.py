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
        elif part.startswith(' INV '):
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
            result = 1 - float(result)
    else:
        result = ''
        if dflt != '':
            result = dflt

    # Gestion des overrides
    if override and eet_field is not None:
        sql_query = f"""select top 1 eet_value from tb_eet_override
                        where eet_field ='{eet_field}' and ref_fund_id= '{key_fund}' and date_data ='{mavar[1]}'
                        order by id desc """

        df_override = pd.read_sql(sql_query, connect)
        if df_override.shape[0] == 1:
            result = df_override.iloc[0, 0]

    return result


def Calcul_df_final_all_parts(fund, EET_version, date_calcul='31/12/2024'):
    """
    Calcule le dataframe final avec les résultats pour toutes les parts d'un fonds
    Retourne df_calcul avec toutes les colonnes de parts, et df_tmp
    """
    df_calcul = EET_version.copy()
    cnxn = dc.connect_dwh()

    # Récupération des infos du fonds
    keyfund = get_datafunds(fund, 'Key_Fund')
    lib_fund = get_datafunds(fund, 'Lib_Fund')
    lib_fund_str = lib_fund.replace(' ', '-').lower()

    # Récupérer toutes les parts actives
    liste_part = get_active_part(fund)
    if not liste_part:
        # Si aucune part, on utilise le fonds lui-même
        liste_part = [fund]

    # Ajouter une colonne pour chaque part
    col_dep = df_calcul.shape[1]

    for part in liste_part:
        df_calcul.insert(df_calcul.shape[1], part, [None] * len(df_calcul))

    col_fin = df_calcul.shape[1]

    # Calculer pour chaque part
    for column in liste_part:
        # Gestion des valeurs fixes
        fixed_value_rows = df_calcul['is_fixed_value'] == '1'
        df_calcul.loc[fixed_value_rows, column] = df_calcul.loc[fixed_value_rows, 'value_source']

        # Gestion des dates
        date_now_rows = df_calcul['value_source'] == 'Date(now)'
        df_calcul.loc[date_now_rows, column] = dt.date.today()

        date_calcul_rows = df_calcul['value_source'] == 'Date(calcul)'
        df_calcul.loc[date_calcul_rows, column] = date_calcul

        # Calculs pour la colonne
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
    df_calcul = df_calcul[['field_name'] + list(df_calcul.columns[col_dep:col_fin])]
    return df_calcul, df_tmp


def Calcul_df_final(fund, EET_version, date_calcul='31/12/2024'):
    """Calcule le dataframe final avec les résultats pour un seul fonds (première part uniquement)"""
    df_calcul = EET_version.copy()
    cnxn = dc.connect_dwh()

    # Récupération des infos du fonds
    keyfund = get_datafunds(fund, 'Key_Fund')
    lib_fund = get_datafunds(fund, 'Lib_Fund')
    lib_fund_str = lib_fund.replace(' ', '-').lower()

    # Récupérer uniquement la première part active
    liste_part = get_active_part(fund)
    if not liste_part:
        # Si aucune part, on utilise le fonds lui-même
        first_part = fund
    else:
        first_part = liste_part[0]
    # Ajouter une seule colonne pour la première part
    col_dep = df_calcul.shape[1]
    df_calcul.insert(df_calcul.shape[1], first_part, [None] * len(df_calcul))
    col_fin = df_calcul.shape[1]

    column = first_part  # On travaille uniquement avec cette colonne

    # Gestion des valeurs fixes
    fixed_value_rows = df_calcul['is_fixed_value'] == '1'
    df_calcul.loc[fixed_value_rows, column] = df_calcul.loc[fixed_value_rows, 'value_source']

    # Gestion des dates
    date_now_rows = df_calcul['value_source'] == 'Date(now)'
    df_calcul.loc[date_now_rows, column] = dt.date.today()

    date_calcul_rows = df_calcul['value_source'] == 'Date(calcul)'
    df_calcul.loc[date_calcul_rows, column] = date_calcul

    # Calculs pour la colonne
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
    df_calcul = df_calcul[['field_name'] + list(df_calcul.columns[col_dep:col_fin])]
    return df_calcul, df_tmp


def calculate_fund_results(fund, version='EET_1_1_3', date_calcul='31/12/2024'):
    """
    Calcule les résultats pour un seul fonds
    Retourne un dictionnaire {field_name: résultat}
    """
    try:
        df_eet = get_eet_fields(version)
        df_final, df_tmp = Calcul_df_final(fund, df_eet, date_calcul)  # Plus de liste, un seul fonds
        # Créer un dictionnaire field_name -> résultat
        # On prend la première colonne de résultat (après field_name)
        results = {}
        if df_final.shape[1] > 1:
            result_column = df_final.columns[1]  # Première colonne après field_name
            for idx, row in df_final.iterrows():
                field_name = row['field_name']
                result_value = row[result_column]
                # Convertir en type JSON-serializable
                if pd.notna(result_value):
                    # Convertir datetime/date en string
                    if isinstance(result_value, (dt.date, dt.datetime, pd.Timestamp)):
                        result_value = str(result_value)
                    # Convertir les types numpy en types Python natifs
                    elif hasattr(result_value, 'item'):
                        result_value = result_value.item()
                    results[field_name] = result_value
                else:
                    results[field_name] = ''

        return results
    except Exception as e:
        print(f"Erreur dans calculate_fund_results: {str(e)}")
        import traceback
        traceback.print_exc()
        return {}


def generate_eet_excel(funds, version='EET_1_1_3', date_calcul='31/12/2024'):
    """
    Génère un fichier Excel avec les résultats EET pour plusieurs fonds (toutes les parts)
    Retourne le chemin du fichier généré
    """
    import os
    import tempfile

    try:
        df_eet = get_eet_fields(version)

        # Calculer les résultats pour tous les fonds avec toutes leurs parts
        df_combined = None
        df_tmp_combined = None

        for fund in funds:
            # Utiliser Calcul_df_final_all_parts pour obtenir toutes les parts
            df_final, df_tmp = Calcul_df_final_all_parts(fund, df_eet.copy(), date_calcul)

            if df_combined is None:
                df_combined = df_final
                df_tmp_combined = df_tmp
            else:
                # Concaténer horizontalement (ajouter les colonnes du nouveau fonds)
                df_combined = pd.concat([df_combined, df_final.iloc[:, 1:]], axis=1)
                df_tmp_combined = pd.concat([df_tmp_combined, df_tmp.iloc[:, df_tmp_combined.shape[1]:]], axis=1)

        # Transposer le dataframe pour avoir les parts en lignes
        df_transpose = df_combined.transpose().reset_index(drop=True)
        df_transpose.columns = df_transpose.iloc[0]
        df_transpose = df_transpose[1:]

        # Créer le nom du fichier
        date_str = date_calcul.replace('/', '')
        if len(funds) == 1:
            filename = f'EET_{date_str}_{funds[0]}.xlsx'
        else:
            filename = f'EET_{date_str}.xlsx'

        # Créer un fichier temporaire
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)

        # Écrire le fichier Excel
        with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
            df_transpose.to_excel(writer, sheet_name='Data', index=False)
            df_tmp_combined.to_excel(writer, sheet_name='check', index=False)

        return filepath, filename

    except Exception as e:
        print(f"Erreur dans generate_eet_excel: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

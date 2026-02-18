import sys
from Utils import *
from Input import *
import warnings

warnings.filterwarnings("ignore")

pd.set_option('display.max_rows', None)
# username, password = Get_Credentials()
# Nav_Date = Get_Last_Nav_Date( username , password , 'MV' , '2023-28-11')

#   Retrieve the list of funds using the Get_Fund_List function, providing the specified 'username' and 'password' and extract the Key_Fund
Fund_List = Get_Fund_List()
Key_Fund_List = Fund_List['Key_Fund']

# Fund_List.to_excel('C:\\Users\\abouygues\\Documents\\Fund_List_Mandarine.xlsx', index=False)

#   Initialize the Funds_TPT_Dictionary
Funds_TPT_Dictionnary = {}
TPT_Concatenated = pd.DataFrame()

#   Initialize the Warning_Dictionnary
Warning_Dictionnary = {}

#   Create a dictionnary for economic area code
Dict_Economic_Area_Code = Get_Economic_Area_Code_Opti()

while True:
    reponse = input(
        f"Voulez-vous continuer, la date actuelle est : {Get_Last_Previous_Month_Date(Reporting_Date)} (oui/non): ").lower()
    if reponse == 'oui':
        break
    elif reponse == 'non':
        while True:
            Reporting_Date = input("Veuillez saisir une date au format 'yyyy-dd-mm': ")
            try:
                # Tentative de conversion de la chaîne en objet datetime
                Reporting_Date = datetime.strptime(Reporting_Date, "%Y-%d-%m") + timedelta(days=15)
                Reporting_Date = Reporting_Date.strftime('%Y-%d-%m')
                break  # Sortir de la boucle si la conversion a réussi
            except ValueError:
                print("Format de date invalide. Assurez-vous de saisir la date au format 'yyyy-mm-dd'.")
                sys.exit("Arrêt du code en raison d'une date invalide.")
    else:
        print("Réponse invalide. Veuillez répondre par 'oui' ou 'non'.")
        sys.exit("Arrêt du code en raison d'une date invalide.")

    break

#############################################################################################
#    Define Scope Public/Private
#############################################################################################
scope_Public_Private = get_public_dedie_list()

# Reporting_Date = '2025-15-04'
#   Loop on the funds

#############################################################################################
#    Run for single Fund
#############################################################################################
# Key_Fund_List = Key_Fund_List[Key_Fund_List == 13]     # MCS
# Key_Fund_List = Key_Fund_List[Key_Fund_List == 239]     Mandarine Premium Europe
# Key_Fund_List = Key_Fund_List[Key_Fund_List == 133]    # Ethicare
# Key_Fund_List = Key_Fund_List[Key_Fund_List == 57]     # NOVESS
# Key_Fund_List = Key_Fund_List[Key_Fund_List == 158]    # Proclero

#############################################################################################

for Key_Fund in tqdm(Key_Fund_List, desc="Processing Funds"):

    Warning_List = list()
    Mnemo = Fund_List.loc[Fund_List['Key_Fund'] == Key_Fund, 'Mnemo_Fund'].iloc[0]
    Fund_Part_List = Get_Fund_Part_List(Key_Fund)
    Nav_Date = Get_Last_Nav_Date(Key_Fund, Get_Last_Previous_Month_Date(Reporting_Date))
    Shares_TPT_Dictionnary = {}

    # if Key_Fund == 57 :
    #    continue

    # Check if Nav_Date is None or if the length of Fund_Part_List is 0
    if Nav_Date == None:
        # print(f"{Fund_List[Fund_List['Key_Fund'] == Key_Fund]['Lib_Fund'].values[0]} as no data")
        Warning_List.append(
            f"{Fund_List[Fund_List['Key_Fund'] == Key_Fund]['Lib_Fund'].values[0]} as no data (Nav_Date = None)")
    elif len(Fund_Part_List) == 0:
        # print(f"{Fund_List[Fund_List['Key_Fund'] == Key_Fund]['Lib_Fund'].values[0]} as no data")
        Warning_List.append(
            f"{Fund_List[Fund_List['Key_Fund'] == Key_Fund]['Lib_Fund'].values[0]} as no data (No Part Found)")
    else:
        #   Get the portfolio relevant to the NAV date
        Ptf = Get_Ptf(Key_Fund, Nav_Date)

        #  DEBUG ############################################################################################
        #
        # if Key_Fund == 131 or Key_Fund == 133 or Key_Fund == 134 :
        #     print("")
        #     print (f"Ptf = {Key_Fund} ")
        #     print (f"Nav_Date = {Nav_Date}")
        #     print (f"PTF : ")
        #     print (Ptf)
        #####################################################################################################

        #   Retrieve the details of the portfolio product
        Fund_Ref_Product = Get_Ref_Product(Ptf['Id_Ref_Valeur'])
        Fund_Data_Histo = Get_Ref_Data_Histo(Ptf['Id_Ref_Valeur'], Nav_Date)

        # Fund_Ref_Product.to_excel('C:\\Users\\abouygues\\Documents\\Alexandre\\Developpement\\Reporting\\Fund_Ref_Product.xlsx', index=False)
        # Fund_Data_Histo.to_excel('C:\\Users\\abouygues\\Documents\\Alexandre\\Developpement\\Reporting\\Fund_Data_Histo.xlsx', index=False)

        #   Count the rows present in the portfolio
        Num_Rows_Ptf = len(Ptf)
        Num_Rows_Ref_Product = len(Fund_Ref_Product)
        Num_Rows_Data_Histo = len(Fund_Data_Histo)
        Num_Rows_NC = len(
            Fund_Ref_Product[(Fund_Ref_Product['Cotation_Type'] == 'NC') & (Fund_Ref_Product['Type_Actif'] != 'Cash')])

        # Check for inconsistencies in Id_Ref_Valeur values
        missing_in_Ref_Product = set(Ptf['Id_Ref_Valeur']) - set(Fund_Ref_Product['Key_Valeur'])
        missing_in_Data_Histo = set(Ptf[Ptf['Type_Actif2'] != 'Cash']['Id_Ref_Valeur']) - set(
            Fund_Data_Histo['ID_Ref_Valeur'])

        #   Ensure the number of values is correct for every variable
        ligne_Cash = (Ptf['Type_Actif2'] == 'Cash').sum()
        if Num_Rows_Ptf != Num_Rows_Ref_Product:
            Warning_List.append(
                f"Inconsistent number of rows between Ptf ({Num_Rows_Ptf} rows) and Fund_Ref_Product ({Num_Rows_Ref_Product} rows).")
            Warning_List.append(f"Id_Ref_Valeur values missing in Fund_Ref_Product: {missing_in_Ref_Product}")
        if Num_Rows_Ptf != (Num_Rows_Data_Histo + ligne_Cash + Num_Rows_NC):
            Warning_List.append(
                f"Warning : Inconsistent number of rows between Ptf ({Num_Rows_Ptf} rows) and Fund_Data_Histo ({Num_Rows_Data_Histo} rows + {ligne_Cash} Cash rows):")
            Warning_List.append(f"Id_Ref_Valeur values missing in Fund_Data_Histo: {missing_in_Data_Histo}")

        ##################################################################################################################
        #   Re-order Ref_Valeurs to match TPT Format (Using Id_Ref_Valeur as Key for upcoming  merge)                    #
        ##################################################################################################################
        Fund_Product_Details = {'Id_Ref_Valeur': Fund_Ref_Product['Key_Valeur'],
                                '12_CIC_code_of_the_instrument': Fund_Ref_Product['Code_CIC'],
                                '13_Economic_zone_of_the_quotation_place': Fund_Ref_Product['Code_Pays_Valeur'],
                                '14_Identification_code_of_the_instrument': Fund_Ref_Product['Code_ISIN_Valeur'],
                                '15_Type_of_identification_code_for_the_instrument': Fund_Ref_Product[
                                    'Code_ISIN_Valeur'],
                                '17_Instrument_name': Fund_Ref_Product['Lib_Valeur'],
                                '19_Nominal_amount': Fund_Ref_Product['Nominal_Montant'],
                                '20_Contract_size_for_derivatives': Fund_Ref_Product['Quotite'],
                                '31_Market_exposure_for_the_3rd_currency_in_weight_over_NAV': None,
                                '32_Interest_rate_type': Fund_Ref_Product['Coupon_Type'],
                                '33_Coupon_rate': Fund_Ref_Product['Taux_CC'],
                                '34_Interest_rate_reference_identification': Fund_Ref_Product['reset_idx'],
                                '35_Identification_type_for_interest_rate_index': "",
                                '36_Interest_rate_index_name': "",
                                '37_Interest_rate_margin': "",
                                '38_Coupon_payment_frequency': Fund_Ref_Product['Frequence_Coupon'],
                                '39_Maturity_date': Fund_Ref_Product['Date_Echeance'],
                                '40_Redemption_type': '',
                                '41_Redemption_rate': '',
                                '44_Issuer_bearer_option_exercise': '',
                                '45_Strike_price_for_embedded_(call_put)_options': Fund_Ref_Product['Strike'],
                                '46_Issuer_name': Fund_Ref_Product['Issuer_Name'],
                                '47_Issuer_identification_code': Fund_Ref_Product['LEI_Code'],
                                '48_Type_of_identification_code_for_issuer': None,
                                '49_Name_of_the_group_of_the_issuer': Fund_Ref_Product['Issuer_Name_Final'],
                                '50_Identification_of_the_group': Fund_Ref_Product['LEI_PARENT_Code'],
                                '51_Type_of_identification_code_for_issuer_group': None,
                                # '52_Issuer_country' : Fund_Ref_Product['Headquarter_ISO'],
                                # '53_Issuer_economic_area' : Fund_Ref_Product['Headquarter_ISO'],

                                '52_Issuer_country': Fund_Ref_Product['Headquarter_ISO'] if Fund_Ref_Product[
                                                                                                'Headquarter_ISO'] is not None else
                                Fund_Ref_Product['Code_Pays_Iso'],
                                '53_Issuer_economic_area': Fund_Ref_Product['Headquarter_ISO'] if Fund_Ref_Product[
                                                                                                      'Headquarter_ISO'] is not None else
                                Fund_Ref_Product['Code_Pays_Iso'],

                                #
                                '54_Economic_sector': Fund_Ref_Product['Code_NACE'],
                                '55_Covered_not_covered': Fund_Ref_Product['is_covered'],
                                '56_Securitisation': None,
                                '57_Explicit_guarantee_by_the_country_of_issue': Fund_Ref_Product['guarantor_type'],
                                '58_Subordinated_debt': None,
                                '58b_Nature_of_the_tranche': None,
                                '59_Credit_quality_step': None,
                                '60_Call_Put_Cap_Floor': Fund_Ref_Product['Call_Put'],
                                '61_Strike_price': Fund_Ref_Product['Strike'],
                                '62_Conversion_factor_(convertibles)_concordance_factor_parity_(options)':
                                    Fund_Ref_Product['fut_cnvs_factor'],
                                '63_Effective_date_of_instrument': '',
                                '64_Exercise_type': Fund_Ref_Product['Exercise_Type'],
                                '65_Hedging_rolling': None,
                                'Sous_Jacent_Id_Ref_Valeur': Fund_Ref_Product['Sous_Jacent'],
                                'PUTABLE': Fund_Ref_Product['putable'],
                                'Coef_Devise': Fund_Ref_Product['Coef_Devise'],
                                'Nominal_Type': Fund_Ref_Product['Nominal_Type'],
                                'Cotation_Type': Fund_Ref_Product['Cotation_Type']
                                }

        ##################################################################################################################
        #   Data processing for Fund_Product_Details                                                                     #
        ##################################################################################################################
        #   The choice of interest rate margin is contingent on whether the value in 'spread_to_mid' is null
        Fund_Product_Details['37_Interest_rate_margin'] = Fund_Ref_Product['spread_to_mid'] if Fund_Ref_Product[
            'spread_to_mid'].empty else Fund_Ref_Product['disc_mrgn_mid']

        #   Transform the dictionary into a DataFrame
        Fund_Product_Details_pd = pd.DataFrame(Fund_Product_Details)

        # Process ISIN and Call_Put Format
        Fund_Product_Details_pd['15_Type_of_identification_code_for_the_instrument'] = Fund_Product_Details_pd[
            '15_Type_of_identification_code_for_the_instrument'].apply(Process_ISIN)
        Fund_Product_Details_pd['60_Call_Put_Cap_Floor'] = Fund_Product_Details_pd['60_Call_Put_Cap_Floor'].apply(
            Process_Call_Put)

        #   Remove '19_Nominal_amount' for equity and cash
        condition_action_cash = (
                (Fund_Product_Details_pd['12_CIC_code_of_the_instrument'].astype(str).str[2] == '3') |
                (Fund_Product_Details_pd['12_CIC_code_of_the_instrument'].astype(str).str[2] == '7')
        )
        Fund_Product_Details_pd.loc[condition_action_cash, '19_Nominal_amount'] = None

        #   Remove '20_Contract_size_for_derivatives' for non-derivative product
        condition_for_derivatives = (
                (Fund_Product_Details_pd['12_CIC_code_of_the_instrument'].astype(str).str[2] == 'A') |
                (Fund_Product_Details_pd['12_CIC_code_of_the_instrument'].astype(str).str[2] == 'B') |
                (Fund_Product_Details_pd['12_CIC_code_of_the_instrument'].astype(str).str[2] == 'C') |
                (Fund_Product_Details_pd['12_CIC_code_of_the_instrument'].astype(str).str[2] == 'D') |
                (Fund_Product_Details_pd['12_CIC_code_of_the_instrument'].astype(str).str[2] == 'E') |
                (Fund_Product_Details_pd['12_CIC_code_of_the_instrument'].astype(str).str[2] == 'F')
        )
        Fund_Product_Details_pd.loc[~condition_for_derivatives, '20_Contract_size_for_derivatives'] = None

        #   Replace empty values in the '33_Coupon_rate' column with None in the Fund_Product_Details_pd DataFrame.
        Fund_Product_Details_pd['33_Coupon_rate'] = Fund_Product_Details_pd['33_Coupon_rate'].replace('', None)

        #   Set '35_Identification_type_for_interest_rate_index' to '5' for non-null values in the '33_Coupon_rate' column in Fund_Product_Details_pd DataFrame.
        Fund_Product_Details_pd.loc[
            ~Fund_Product_Details_pd['33_Coupon_rate'].isnull(), '35_Identification_type_for_interest_rate_index'] = '5'

        Fund_Product_Details_pd['39_Maturity_date'] = pd.to_datetime(Fund_Product_Details_pd['39_Maturity_date'],
                                                                     errors='coerce')
        Fund_Product_Details_pd['39_Maturity_date'] = Fund_Product_Details_pd['39_Maturity_date'].dt.strftime(
            '%Y-%m-%d')

        #   Apply the Redemption_type function to determine '40_Redemption_type' values based on the conditions in the Fund_Ref_Product DataFrame.
        Fund_Product_Details_pd['40_Redemption_type'] = Fund_Ref_Product.apply(Redemption_type, axis=1)

        #   Put Type of identification code for issuer if needed
        Fund_Product_Details_pd['48_Type_of_identification_code_for_issuer'] = Fund_Product_Details_pd[
            '47_Issuer_identification_code'].apply(assign_value_LEI_Or_Empty)
        Fund_Product_Details_pd['51_Type_of_identification_code_for_issuer_group'] = Fund_Product_Details_pd[
            '50_Identification_of_the_group'].apply(assign_value_LEI_Or_Empty)

        #   Process the Code NACE
        Fund_Product_Details_pd['54_Economic_sector'] = Fund_Product_Details_pd['54_Economic_sector'].apply(
            Process_NACE_Code)

        #   Process the issuer economic area
        # Fund_Product_Details_pd['53_Issuer_economic_area'] = Fund_Product_Details_pd['53_Issuer_economic_area'].apply(Process_Economic_Area_Code, args=(username, password))

        #   Add '57_Explicit_guarantee_by_the_country_of_issue' for Goverment Bonds (CIC 1), Corporate Bonds (CIC 2),Structured notes (CIC 5) and Collateralized securities (CIC 6)
        condition_for_Govt_Bond_Notes_Collat = (
                (Fund_Product_Details_pd['12_CIC_code_of_the_instrument'].astype(str).str[2] == '1') |
                (Fund_Product_Details_pd['12_CIC_code_of_the_instrument'].astype(str).str[2] == '2') |
                (Fund_Product_Details_pd['12_CIC_code_of_the_instrument'].astype(str).str[2] == '5') |
                (Fund_Product_Details_pd['12_CIC_code_of_the_instrument'].astype(str).str[2] == '6')
        )
        Fund_Product_Details_pd['57_Explicit_guarantee_by_the_country_of_issue'] = Fund_Product_Details_pd[
            '57_Explicit_guarantee_by_the_country_of_issue'].apply(Process_Guarantee)
        Fund_Product_Details_pd.loc[
            ~condition_for_Govt_Bond_Notes_Collat, '57_Explicit_guarantee_by_the_country_of_issue'] = None

        Fund_Product_Details_pd['65_Hedging_rolling'] = Fund_Product_Details_pd['12_CIC_code_of_the_instrument'].apply(
            Process_Hedge)

        # If the line is an equity no underlying
        condition_for_underlyings = (
                    Fund_Product_Details_pd['12_CIC_code_of_the_instrument'].astype(str).str[2:4] == '31')
        Fund_Product_Details_pd.loc[condition_for_underlyings, 'Sous_Jacent_Id_Ref_Valeur'] = None

        # Transform '12_CIC_code_of_the_instrument' using Process_Underlying_asset_category and store in '131_Underlying_asset_category'
        Fund_Product_Details_pd['131_Underlying_asset_category'] = Fund_Product_Details_pd[
            '12_CIC_code_of_the_instrument'].apply(Process_Underlying_asset_category)

        #   Save the Fund_Product_Details_pd DataFrame to an Excel file at the specified path without including the index
        # Fund_Product_Details_pd.to_excel('C:\\Users\\abouygues\\Documents\\Alexandre\\Developpement\\3_Reporting\\Fund_Product_Details.xlsx', index=False)

        ##################################################################################################################
        #   Re-order Tb_Mo_Data_Histo to match TPT Format  (Using Id_Ref_Valeur as Key for upcoming  merge)              #
        ##################################################################################################################
        Fund_Product_Details_Data_Histo = {'Id_Ref_Valeur': Fund_Data_Histo['ID_Ref_Valeur'],
                                           'NXT_CAL_DT': Fund_Data_Histo['Next_Callable_DT'],
                                           'NXT_PUT_DT': Fund_Data_Histo['NXT_PUT_DT'],
                                           'CALLABLE': Fund_Data_Histo['Callable'],
                                           '42_Callable_putable': None,
                                           '43_Call_put_date': None,
                                           '68_Identification_code_of_the_underlying_asset': Fund_Data_Histo[
                                               'Underlying'],
                                           '69_Type_of_identification_code_for_the_underlying_asset': None,
                                           '72_Last_valuation_price_of_the_underlying_asset': Fund_Data_Histo[
                                               'Underlying_Prix'],
                                           '90_Modified_duration_to_maturity_date': Fund_Data_Histo[
                                               'Duration_To_Maturity'],
                                           '91_Modified_duration_to_next_option_exercise_date': Fund_Data_Histo[
                                               'Duration'],
                                           '92_Credit_sensitivity': Fund_Data_Histo['Credit_sensitivity'],
                                           '93_Sensitivity_to_underlying_asset_price_(delta)': Fund_Data_Histo['Delta'],
                                           '94_Convexity_gamma_for_derivatives': None,
                                           '94b_Vega': None,
                                           '95_Identification_of_the_original_portfolio_for_positions_embedded_in_a_fund': None,
                                           '106_Asset_pledged_as_collateral': None,
                                           '107_Place_of_deposit': None,
                                           '108_Participation': None,
                                           '110_Valorisation_method': None,
                                           '111_Value_of_acquisition': None,
                                           '112_Credit_rating': None,
                                           '113_Rating_agency': None,
                                           '114_Issuer_economic_area': None,
                                           '127_Bond_floor_(convertible_instrument_only)': None,
                                           '128_Option_premium_(convertible_instrument_only)': None,
                                           '129_Valuation_yield': None,
                                           '130_Valuation_z_spread': None,
                                           '134_type1_private_equity_portfolio_eligibility': None,
                                           '135_type1_private_equity_issuer_beta': None,
                                           '137_Counterparty_sector': None,
                                           '138_Collateral_eligibility': None,
                                           '139_Collateral_Market_valuation_in_portfolio_currency': None
                                           }

        #   Calculate the sum of 'Valeur_Boursiere_MO' in the Ptf DataFrame and assign it to the variable 'Actif'.
        Actif = sum(Ptf['Valeur_Boursiere_MO'])

        ##################################################################################################################
        #   Re-order Tb_MO_Contribution to match TPT Format  (Using Id_Ref_Valeur as Key for upcoming  merge)            #
        ##################################################################################################################
        Fund_Product_Valuation = {'Id_Ref_Valeur': Ptf['Id_Ref_Valeur'],
                                  'Type_Actif2': Ptf['Type_Actif2'],
                                  'Type_Support2': Ptf['Type_Support2'],
                                  'Devise_1d': Ptf['Devise_1d'],
                                  '18_Quantity': Ptf['Positions_Fo'],
                                  '21_Quotation_currency_(A)': Ptf['Devise'],
                                  '22_Market_valuation_in_quotation_currency_(A)': (
                                              Ptf['Valeur_Boursiere_MO'] * Ptf['Devise_1d']).round(2),
                                  '23_Clean_market_valuation_in_quotation_currency_(A)': (
                                              Ptf['Positions_Fo'] * Ptf['Px_Close_Inventaire']).round(2),
                                  # '23_Clean_market_valuation_in_quotation_currency_(A)' : (Ptf['Valeur_Boursiere_MO']*Ptf['Devise_1d']).round(2),
                                  '24_Market_valuation_in_portfolio_currency_(B)': Ptf['Valeur_Boursiere_MO'].round(2),
                                  '25_Clean_market_valuation_in_portfolio_currency_(B)': (
                                              Ptf['Positions_Fo'] * Ptf['Px_Close_Inventaire'] / Ptf[
                                          'Devise_1d']).round(2),
                                  # '25_Clean_market_valuation_in_portfolio_currency_(B)' : Ptf['Valeur_Boursiere_MO'].round(2),
                                  '26_Valuation_weight': Ptf['poids_inv_no_roundup'],
                                  '27_Market_exposure_amount_in_quotation_currency_(A)': (
                                              Ptf['Engagement'] * Ptf['Devise_1d']).round(2),
                                  '28_Market_exposure_amount_in_portfolio_currency_(B)': (Ptf['Engagement']).round(2),
                                  '29_Market_exposure_amount_for_the_3rd_quotation_currency_(C)': None}

        # print(Ptf[['Id_Ref_Valeur','Type_Actif2','Positions_Fo','Px_Close_Inventaire','Devise_1d']])
        ##################################################################################################################
        #   Data processing for Tb_MO_Contribution                                                                     #
        #################################################################################################################
        #   Transform the dictionary into a DataFrame
        Fund_Product_Details_Data_Histo_pd = pd.DataFrame(Fund_Product_Details_Data_Histo)

        #   Transform the dictionary into a DataFrame
        Fund_Product_Valuation_pd = pd.DataFrame(Fund_Product_Valuation)

        #   Get PUTABLE Label from ref_valeur
        Fund_Product_Details_Data_Histo_pd = pd.merge(
            Fund_Product_Details_pd[['Id_Ref_Valeur', 'PUTABLE']],
            Fund_Product_Details_Data_Histo_pd,
            on='Id_Ref_Valeur',
            how='outer'
        )

        #   Get Type_Actif2 & Type_Support2 Label from ref_valeur
        Fund_Product_Details_Data_Histo_pd = pd.merge(
            Fund_Product_Valuation_pd[['Id_Ref_Valeur', 'Type_Actif2', 'Type_Support2']],
            Fund_Product_Details_Data_Histo_pd,
            on='Id_Ref_Valeur',
            how='inner'
        )

        #   Clean empty value not set as 'None' and Nan value as 'None'
        Fund_Product_Details_Data_Histo_pd = Fund_Product_Details_Data_Histo_pd.replace('', None)

        #   Update '42_Callable_putable' and '43_Call_put_date' based on '42_Callable_putable': 'NXT_CAL_DT' if 'CAL', 'NXT_PUT_DT' if 'PUT'
        condition_putable = Fund_Product_Details_Data_Histo_pd['PUTABLE'] == 'Y'
        condition_callable = Fund_Product_Details_Data_Histo_pd['CALLABLE'] == 'Y'

        Fund_Product_Details_Data_Histo_pd.loc[condition_putable, '42_Callable_putable'] = 'PUT'
        Fund_Product_Details_Data_Histo_pd.loc[condition_callable, '42_Callable_putable'] = 'CAL'

        Fund_Product_Details_Data_Histo_pd.loc[~condition_putable & ~condition_callable, '42_Callable_putable'] = None

        condition_cal = Fund_Product_Details_Data_Histo_pd['42_Callable_putable'] == 'CAL'
        condition_put = Fund_Product_Details_Data_Histo_pd['42_Callable_putable'] == 'PUT'

        # Fund_Product_Details_Data_Histo_pd['NXT_CAL_DT'] = pd.to_datetime(Fund_Product_Details_Data_Histo_pd['NXT_CAL_DT'])
        # Fund_Product_Details_Data_Histo_pd['NXT_PUT_DT'] = pd.to_datetime(Fund_Product_Details_Data_Histo_pd['NXT_PUT_DT'])

        # Fund_Product_Details_Data_Histo_pd['NXT_CAL_DT'] = Fund_Product_Details_Data_Histo_pd['NXT_CAL_DT'].dt.strftime('%Y-%m-%d')
        # Fund_Product_Details_Data_Histo_pd['NXT_PUT_DT'] = Fund_Product_Details_Data_Histo_pd['NXT_PUT_DT'].dt.strftime('%Y-%m-%d')

        Fund_Product_Details_Data_Histo_pd.loc[condition_cal, '43_Call_put_date'] = \
        Fund_Product_Details_Data_Histo_pd.loc[condition_cal, 'NXT_CAL_DT']
        Fund_Product_Details_Data_Histo_pd.loc[condition_put, '43_Call_put_date'] = \
        Fund_Product_Details_Data_Histo_pd.loc[condition_put, 'NXT_PUT_DT']

        Fund_Product_Details_Data_Histo_pd.loc[~condition_put & ~condition_cal, '43_Call_put_date'] = None

        #   Update value to to '5' if '68_...' is not null
        condition_if_68 = Fund_Product_Details_Data_Histo_pd['68_Identification_code_of_the_underlying_asset'].notnull()
        Fund_Product_Details_Data_Histo_pd.loc[
            condition_if_68, '69_Type_of_identification_code_for_the_underlying_asset'] = '5'
        Fund_Product_Details_Data_Histo_pd.loc[
            ~condition_if_68, '69_Type_of_identification_code_for_the_underlying_asset'] = None
        Fund_Product_Details_Data_Histo_pd.loc[
            ~condition_if_68, '68_Identification_code_of_the_underlying_asset'] = None

        ##################################################################################################################
        #   Data processing for Fund_Product_Details                                                                     #
        ##################################################################################################################
        #   Update '27' and '28' columns in the Fund_Product_Valuation_pd DataFrame for rows where 'Type_Actif2' is 'Cash'
        #   The values are calculated based on the product of '26_Valuation_weight', 'Actif', and the respective currency conversion factors, rounded to 2 decimal places
        # Fund_Product_Valuation_pd.loc[Fund_Product_Valuation_pd['Type_Actif2'] == 'Cash', '27_Market_exposure_amount_in_quotation_currency_(A)'] = (Fund_Product_Valuation_pd['26_Valuation_weight'] * Actif / Fund_Product_Valuation_pd['Devise_1d']).round(2)
        # Fund_Product_Valuation_pd.loc[Fund_Product_Valuation_pd['Type_Actif2'] == 'Cash', '28_Market_exposure_amount_in_portfolio_currency_(B)'] = (Fund_Product_Valuation_pd['26_Valuation_weight'] * Actif ).round(2)

        # Calculate and assign values to the '30_Market_exposure_in_weight' column in the Fund_Product_Valuation_pd DataFrame
        Fund_Product_Valuation_pd['30_Market_exposure_in_weight'] = Fund_Product_Valuation_pd[
                                                                        '28_Market_exposure_amount_in_portfolio_currency_(B)'] / Actif

        #   Save the Fund_Product_Valuation_pd DataFrame to an Excel file at the specified path without including the index
        # Fund_Product_Valuation_pd.to_excel('C:\\Users\\abouygues\\Documents\\Alexandre\\Developpement\\3_Reporting\\Fund_Product_Valuation.xlsx', index=False)

        ##################################################################################################################
        #   Get And Re-order Data for underlying asset  (Using Id_Ref_Valeur as Key for upcoming merge)                  #
        ##################################################################################################################
        #   Select the key and underlying assets of the fund (non-null Sous_Jacent_Id_Ref_Valeur)
        underlying_asset_List = Fund_Product_Details_pd[['Id_Ref_Valeur', 'Sous_Jacent_Id_Ref_Valeur']]
        condition_if_None = underlying_asset_List['Sous_Jacent_Id_Ref_Valeur'].notnull()
        underlying_asset_List = underlying_asset_List[condition_if_None]

        #   If no Sous_Jacent_Id_Ref_Valeur, create a warning message
        if len(underlying_asset_List) == 0:

            # Warning_List.append( f"Fund {Fund_List[Fund_List['Key_Fund'] == Key_Fund]['Lib_Fund'].values[0]} as no underlying assets" )
            Fund_Underlying_Details = {
                'Sous_Jacent_Id_Ref_Valeur': None,
                '67_CIC_of_the_underlying_asset': None,
                '70_Name_of_the_underlying_asset': None,
                '71_Quotation_currency_of_the_underlying_asset_(C)': None,
                '73_Country_of_quotation_of_the_underlying_asset': None,
                '74_Economic_area_of_quotation_of_the_underlying_asset': None,
                '75_Coupon_rate_of_the_underlying_asset': None,
                '76_Coupon_payment_frequency_of_the_underlying_asset': None,
                '77_Maturity_date_of_the_underlying_asset': None,
                '78_Redemption_profile_of_the_underlying_asset': None,
                '79_Redemption_rate_of_the_underlying_asset': None,
                '80_Issuer_name_of_the_underlying_asset': None,
                '81_Issuer_identification_code_of_the_underlying_asset': None,
                '82_Type_of_issuer_identification_code_of_the_underlying_asset': None,
                '83_Name_of_the_group_of_the_issuer_of_the_underlying_asset': None,
                '84_Identification_of_the_group_of_the_underlying_asset': None,
                '85_Type_of_the_group_identification_code_of_the_underlying_asset': None,
                '86_Issuer_country_of_the_underlying_asset': None,
                '87_Issuer_economic_area_of_the_underlying_asset': None,
                '88_Explicit_guarantee_by_the_country_of_issue_of_the_underlying_asset': None,
                '89_Credit_quality_step_of_the_underlying_asset': None}

            #   Transform the dictionary into a DataFrame
            Fund_Underlying_Details_pd = pd.DataFrame(
                [Fund_Underlying_Details.copy() for _ in range(len(Fund_Product_Valuation_pd))])
            Fund_Product_Valuation_pd = pd.concat([Fund_Product_Valuation_pd, Fund_Underlying_Details_pd], axis=1)


        #   Otherwise, retrieve characteristics of the product
        else:
            Underlying_Ref_Product = Get_Ref_Product(underlying_asset_List['Sous_Jacent_Id_Ref_Valeur'])
            Fund_Underlying_Details = {
                'Sous_Jacent_Id_Ref_Valeur': Underlying_Ref_Product['Key_Valeur'],
                '67_CIC_of_the_underlying_asset': Underlying_Ref_Product['Code_CIC'],
                '70_Name_of_the_underlying_asset': Underlying_Ref_Product['Lib_Valeur'],
                '71_Quotation_currency_of_the_underlying_asset_(C)': Underlying_Ref_Product['Devise_Valeur'],
                '73_Country_of_quotation_of_the_underlying_asset': Underlying_Ref_Product['Code_Pays_Valeur'],
                '74_Economic_area_of_quotation_of_the_underlying_asset': Underlying_Ref_Product['Code_Pays_Valeur'],
                '75_Coupon_rate_of_the_underlying_asset': Underlying_Ref_Product['Taux_CC'],
                '76_Coupon_payment_frequency_of_the_underlying_asset': Underlying_Ref_Product['Frequence_Coupon'],
                '77_Maturity_date_of_the_underlying_asset': Underlying_Ref_Product['Date_Echeance'],
                '78_Redemption_profile_of_the_underlying_asset': None,
                '79_Redemption_rate_of_the_underlying_asset': None,
                '80_Issuer_name_of_the_underlying_asset': Underlying_Ref_Product['Issuer_Name'],
                '81_Issuer_identification_code_of_the_underlying_asset': Underlying_Ref_Product['LEI_Code'],
                '82_Type_of_issuer_identification_code_of_the_underlying_asset': None,
                '83_Name_of_the_group_of_the_issuer_of_the_underlying_asset': Underlying_Ref_Product[
                    'Issuer_Name_Final'],
                '84_Identification_of_the_group_of_the_underlying_asset': Underlying_Ref_Product['LEI_PARENT_Code'],
                '85_Type_of_the_group_identification_code_of_the_underlying_asset': None,
                '86_Issuer_country_of_the_underlying_asset': Underlying_Ref_Product['Issuer_Country_Iso'],
                '87_Issuer_economic_area_of_the_underlying_asset': None,
                '88_Explicit_guarantee_by_the_country_of_issue_of_the_underlying_asset': None,
                '89_Credit_quality_step_of_the_underlying_asset': None}

            #   Transform the dictionary into a DataFrame
            Fund_Underlying_Details_pd = pd.DataFrame(Fund_Underlying_Details)

            #   Process the issuer economic area
            Fund_Underlying_Details_pd['74_Economic_area_of_quotation_of_the_underlying_asset'] = \
            Fund_Underlying_Details_pd['74_Economic_area_of_quotation_of_the_underlying_asset'].apply(
                Process_Economic_Area_Code, args=())

            #   Apply the Redemption_type function to determine '78_Redemption_profile_of_the_underlying_asset' values based on the conditions in the Fund_Ref_Product DataFrame.
            # Fund_Underlying_Details_pd['78_Redemption_profile_of_the_underlying_asset'] = Fund_Underlying_Details_pd.apply(Redemption_type, axis=1)

            #   Put Type of identification code for issuer if needed
            Fund_Underlying_Details_pd['82_Type_of_issuer_identification_code_of_the_underlying_asset'] = \
            Fund_Underlying_Details_pd['81_Issuer_identification_code_of_the_underlying_asset'].apply(
                assign_value_LEI_Or_Empty)
            Fund_Underlying_Details_pd['85_Type_of_the_group_identification_code_of_the_underlying_asset'] = \
            Fund_Underlying_Details_pd['84_Identification_of_the_group_of_the_underlying_asset'].apply(
                assign_value_LEI_Or_Empty)

            underlying_asset_List['Sous_Jacent_Id_Ref_Valeur'] = underlying_asset_List[
                'Sous_Jacent_Id_Ref_Valeur'].astype(int)
            Fund_Product_Valuation_pd = pd.merge(Fund_Product_Valuation_pd,
                                                 pd.merge(Fund_Underlying_Details_pd, underlying_asset_List,
                                                          on='Sous_Jacent_Id_Ref_Valeur', how='outer'),
                                                 on='Id_Ref_Valeur', how='outer')

        len(Fund_Product_Valuation_pd)
        len(Fund_Product_Details_Data_Histo_pd)

        # Fund_Product_Valuation_pd.to_excel('C:\\Users\\abouygues\\Documents\\Alexandre\\Developpement\\Reporting\\Table_1.xlsx', index=False)
        # Fund_Product_Details_pd.to_excel('C:\\Users\\abouygues\\Documents\\Alexandre\\Developpement\\Reporting\\Table_2.xlsx', index=False)
        # Fund_Product_Details_Data_Histo_pd.to_excel('C:\\Users\\abouygues\\Documents\\Alexandre\\Developpement\\Reporting\\Table_3.xlsx', index=False)

        Fund_Data_Merge = pd.merge(
            pd.merge(Fund_Product_Valuation_pd, Fund_Product_Details_pd, on='Id_Ref_Valeur', how='inner'),
            Fund_Product_Details_Data_Histo_pd, on='Id_Ref_Valeur', how='inner')

        # Fund_Data_Merge.to_excel('C:\\Users\\abouygues\\Documents\\Alexandre\\Developpement\\3_Reporting\\Table_Result.xlsx', index=False)

        # Creates a boolean condition for direct bonds.
        condition = (Fund_Data_Merge['Type_Actif2_x'] == 'Obligations') & (
                    Fund_Data_Merge['Type_Support2_x'] == 'Lignes')

        List_Oblig = Fund_Data_Merge[condition]["14_Identification_code_of_the_instrument"]
        List_Rating = Get_Rtg_Dictionnary(List_Oblig, Nav_Date)

        # try:
        #     Fund_Data_Merge = pd.merge(Fund_Data_Merge, List_Rating, on='Id_Ref_Valeur', how='left')
        #     Fund_Data_Merge['112_Credit_rating'] = Fund_Data_Merge['Rtg_MG_1']
        #     Fund_Data_Merge['113_Rating_agency'] = Fund_Data_Merge['Rating_Agency']
        # except Exception as e:
        #     print(f"Une erreur s'est produite : {e}")

        #   For every fund shares create TPT
        for Num_Rows in range(len(Fund_Part_List)):
            ISIN_Shares = Fund_Part_List.at[Num_Rows, 'ISIN_Fund']
            ID_Fund_Part = Fund_Part_List.at[Num_Rows, 'Key_Fund_Part']
            Mnemo_Fund_Part = Fund_Part_List.at[Num_Rows, 'Mnemo_Fund_Part']
            Funds_VL = Get_Funds_VL(ID_Fund_Part, Nav_Date)

            #########################################################################
            # Tester le 5 pour etre sur qu'il y a une VL  !!!!!!
            #########################################################################

            if len(Funds_VL) == 0:
                print(f'\n No VL Find for : {ISIN_Shares}   \n')
                continue
            # print ( Fund_Part_List.at[Num_Rows,'Lib_Fund_Part'])

            Base_Data = {'1_Portfolio_identifying_data': [ISIN_Shares] * Num_Rows_Ptf,
                         '2_Type_of_identification_code_for_the_fund_share_or_portfolio': [1] * Num_Rows_Ptf,
                         '3_Portfolio_name': Fund_Part_List.at[Num_Rows, 'Lib_Fund_Part'],
                         '4_Portfolio_currency_(B)': Fund_Part_List.at[Num_Rows, 'Devise_Part'],
                         '5_Net_asset_valuation_of_the_portfolio_or_the_share_class_in_portfolio_currency': Funds_VL.at[
                             0, 'Actif_Part_Dev_PTF'],
                         '6_Valuation_date': [datetime.strptime(Nav_Date, '%Y-%d-%m').strftime(
                             '%Y-%m-%d')] * Num_Rows_Ptf,
                         '7_Reporting_date': [datetime.strptime(Get_Last_Previous_Month_Date(Reporting_Date),
                                                                '%Y-%d-%m').strftime('%Y-%m-%d')] * Num_Rows_Ptf,
                         '8_Share_price': Funds_VL.at[0, 'VL_Dev_PTF'],
                         '8b_Total_number_of_shares': Funds_VL.at[0, 'Nb_Parts'],
                         '9_Cash_ratio': sum(Ptf[Ptf['Type_Actif2'] == 'Cash']['poids_inv_no_roundup']),
                         '10_Portfolio_modified_duration': "",
                         '11_Complete_SCR_delivery': "N",
                         '16_Grouping_code_for_multiple_leg_instruments': "",
                         '17b_Asset_liability': "",
                         '97_SCR_mrkt_IR_up_weight_over_NAV': "",
                         '98_SCR_mrkt_IR_down_weight_over_NAV': "",
                         '99_SCR_mrkt_eq_type1_weight_over_NAV': "",
                         '100_SCR_mrkt_eq_type2_weight_over_NAV': "",
                         '101_SCR_mrkt_prop_weight_over_NAV': "",
                         '102_SCR_mrkt_spread_bonds_weight_over_NAV': "",
                         '103_SCR_mrkt_spread_structured_weight_over_NAV': "",
                         '104_SCR_mrkt_spread_derivatives_up_weight_over_NAV': "",
                         '105_SCR_mrkt_spread_derivatives_down_weight_over_NAV': "",
                         '105a_SCR_mrkt_FX_up_weight_over_NAV': "",
                         '105b_SCR_mrkt_FX_down_weight_over_NAV': "",
                         '115_Fund_issuer_code': Fund_List[Fund_List['Key_Fund'] == Key_Fund]['LEI_ManCo'].values[0],
                         '116_Fund_issuer_code_type': None,
                         '117_Fund_issuer_name': Fund_List[Fund_List['Key_Fund'] == Key_Fund]['sdg_kiid'].values[0],
                         '118_Fund_issuer_sector':
                             Fund_List[Fund_List['Key_Fund'] == Key_Fund]['issuer_nace_code'].values[0],
                         '119_Fund_issuer_group_code': Fund_List[Fund_List['Key_Fund'] == Key_Fund]['LEI_ManCo'].values[
                             0],
                         '120_Fund_issuer_group_code_type': None,
                         '121_Fund_issuer_group_name': Fund_List[Fund_List['Key_Fund'] == Key_Fund]['sdg_kiid'].values[
                             0],
                         '122_Fund_issuer_country': Fund_List[Fund_List['Key_Fund'] == Key_Fund]['Pays_Fund'].values[0],
                         '123_Fund_CIC': Fund_List[Fund_List['Key_Fund'] == Key_Fund]['cic_code'].values[0],
                         '123a_Fund_custodian_country': None,
                         '124_Duration': None,
                         '125_Accrued_income_(Security Denominated Currency)': None,
                         '126_Accrued_income_(Portfolio Denominated Currency)': None,
                         '132_Infrastructure_investment': '0',
                         '133_custodian_name': Fund_List[Fund_List['Key_Fund'] == Key_Fund]['Nom_Depositaire'].values[
                             0],
                         '140_Custodian_identification_code':
                             Fund_List[Fund_List['Key_Fund'] == Key_Fund]['140_Custodian_identification_code'].values[
                                 0],
                         '141_Type_of_custodian_identification_code': Fund_List[Fund_List['Key_Fund'] == Key_Fund][
                             '141_Type_of_custodian_identification_code'].values[0],
                         '142_Bail-in_Rule': Fund_List[Fund_List['Key_Fund'] == Key_Fund]['142_Bail-in_Rule'].values[0],
                         '143_Maturity_date_expected':
                             Fund_List[Fund_List['Key_Fund'] == Key_Fund]['143_Maturity_date_expected'].values[0],
                         '144_Modified_duration_to_maturity_date_expected':
                             Fund_List[Fund_List['Key_Fund'] == Key_Fund][
                                 '144_Modified_duration_to_maturity_date_expected'].values[0],
                         '145_Credit_sensitivity_expected':
                             Fund_List[Fund_List['Key_Fund'] == Key_Fund]['145_Credit_sensitivity_expected'].values[0],
                         '146_PIK': Fund_List[Fund_List['Key_Fund'] == Key_Fund]['146_PIK'].values[0],
                         '147_Infrastructure_investment_additional_QRT': Fund_List[Fund_List['Key_Fund'] == Key_Fund][
                             '147_Infrastructure_investment_additional_QRT'].values[0],
                         '148_Economic_sector_NACE2.1':
                             Fund_List[Fund_List['Key_Fund'] == Key_Fund]['148_Economic_sector_NACE2.1'].values[0],

                         '1000_TPT_Version': 'V7.0'}

            # '12_CIC_code_of_the_instrument' : ""}

            Base_Data_df = pd.DataFrame(Base_Data)

            #   Put Type of identification code for issuer if needed
            Base_Data_df['116_Fund_issuer_code_type'] = Base_Data_df['115_Fund_issuer_code'].apply(
                assign_value_LEI_Or_Empty)
            Base_Data_df['120_Fund_issuer_group_code_type'] = Base_Data_df['119_Fund_issuer_group_code'].apply(
                assign_value_LEI_Or_Empty)

            TPT_df = pd.concat([Base_Data_df, Fund_Data_Merge], axis=1)

            #   Clean 18_Quantity and fill 19_Nominal amount if needed
            condition_if_Oblig_Nominal_Type_100 = (TPT_df['Type_Actif2_x'] == 'Obligations') & (
                        TPT_df['Type_Support2_x'] == 'Lignes') & (TPT_df['Nominal_Type'] == '100')
            TPT_df.loc[condition_if_Oblig_Nominal_Type_100, '19_Nominal_amount'] = TPT_df.loc[
                condition_if_Oblig_Nominal_Type_100, '18_Quantity']
            TPT_df.loc[condition_if_Oblig_Nominal_Type_100, '18_Quantity'] = None
            #   Correct 23_, 25_ if Nominal is 100
            TPT_df.loc[condition_if_Oblig_Nominal_Type_100, '25_Clean_market_valuation_in_portfolio_currency_(B)'] = \
            TPT_df.loc[condition_if_Oblig_Nominal_Type_100, '25_Clean_market_valuation_in_portfolio_currency_(B)'] / 100
            TPT_df.loc[condition_if_Oblig_Nominal_Type_100, '23_Clean_market_valuation_in_quotation_currency_(A)'] = \
            TPT_df.loc[condition_if_Oblig_Nominal_Type_100, '23_Clean_market_valuation_in_quotation_currency_(A)'] / 100

            #   Clean 19_Nominal
            condition_if_Oblig_Nominal_Type_1 = ((TPT_df['Type_Actif2_x'] == 'Obligations') & (
                        TPT_df['Type_Support2_x'] == 'Lignes') & (TPT_df['Nominal_Type'] == '1')) | (
                                                            (TPT_df['Type_Actif2_x'] == 'Obligations') & (
                                                                TPT_df['Type_Support2_x'] == 'OPCVM'))
            TPT_df.loc[condition_if_Oblig_Nominal_Type_1, '19_Nominal_amount'] = None

            #   Check for floating rates
            condition_if_32_Floating = (TPT_df['32_Interest_rate_type'] != 'FLOATING')

            TPT_df.loc[condition_if_32_Floating, '34_Interest_rate_reference_identification'] = None
            TPT_df.loc[condition_if_32_Floating, '35_Identification_type_for_interest_rate_index'] = None
            TPT_df.loc[condition_if_32_Floating, '36_Interest_rate_index_name'] = None
            TPT_df.loc[condition_if_32_Floating, '37_Interest_rate_margin'] = None

            if TPT_df.loc[~condition_if_32_Floating, '34_Interest_rate_reference_identification'].isnull().any():
                Warning_List.append(
                    f"Warning : Fund {Fund_List[Fund_List['Key_Fund'] == Key_Fund]['Lib_Fund'].values[0]} 34_Interest_rate_reference_identification is missing")

            TPT_df.loc[TPT_df['12_CIC_code_of_the_instrument'].str[2].isin(
                ['2', '5', '6', '8']), '138_Collateral_eligibility'] = 0
            # TPT_df['137_Counterparty_sector']
            # TPT_df.loc[TPT_df['15_Type_of_identification_code_for_the_instrument'].isin(['99']), '137_Counterparty_sector'] = 12

            ##################################################################################################################
            #   Final Correction                                                                                             #
            ##################################################################################################################
            # print(TPT_df[['Type_Actif2_x' ,'Type_Support2_x','18_Quantity','21_Quotation_currency_(A)','22_Market_valuation_in_quotation_currency_(A)','23_Clean_market_valuation_in_quotation_currency_(A)','24_Market_valuation_in_portfolio_currency_(B)','25_Clean_market_valuation_in_portfolio_currency_(B)','27_Market_exposure_amount_in_quotation_currency_(A)','28_Market_exposure_amount_in_portfolio_currency_(B)']])

            TPT_df.columns

            # Creates a boolean condition where the value is 'Cash'.
            condition = TPT_df['Type_Actif2_x'] == 'Cash'

            # Replaces the values in the column '12_CIC_code_of_the_instrument' with 'XT72' for the rows where the condition is True.
            TPT_df.loc[condition, '12_CIC_code_of_the_instrument'] = 'XT72'

            Devise_Fund = Fund_List[Fund_List['Key_Fund'] == Key_Fund]['Devise_PTF'].values[0]

            TPT_df['21_Quotation_currency_(A)'] = TPT_df['21_Quotation_currency_(A)'].astype(str)
            TPT_df['21_Quotation_currency_(A)'] = TPT_df['21_Quotation_currency_(A)'].apply(lambda x: x.upper())
            TPT_df['Adjust_Cash'] = Devise_Fund + TPT_df['21_Quotation_currency_(A)']
            Devises = TPT_df['21_Quotation_currency_(A)'].unique().tolist()
            Fx_Dictionnary = Fx_Opti(Devises, Devise_Fund, Nav_Date)
            TPT_df['Adjust_Cash'] = TPT_df['Adjust_Cash'].map(Fx_Dictionnary)

            condition = (TPT_df['Type_Actif2_x'] == 'Cash') & (TPT_df['Type_Support2_x'] == 'Lignes')
            TPT_df.loc[condition, '22_Market_valuation_in_quotation_currency_(A)'] = TPT_df.loc[
                condition, '18_Quantity']  # ok
            TPT_df.loc[condition, '23_Clean_market_valuation_in_quotation_currency_(A)'] = TPT_df.loc[
                condition, '18_Quantity']  # ok

            # TPT_df.loc[condition, '18_Quantity'] = TPT_df.loc[condition, '18_Quantity'] * TPT_df.loc[condition,'Adjust_Cash'] # ok
            # TPT_df.loc[condition, '22_Market_valuation_in_quotation_currency_(A)'] = TPT_df.loc[condition, '18_Quantity'] # ok
            # TPT_df.loc[condition, '23_Clean_market_valuation_in_quotation_currency_(A)'] = TPT_df.loc[condition, '18_Quantity'] # ok
            # TPT_df.loc[condition, '27_Market_exposure_amount_in_quotation_currency_(A)'] = TPT_df.loc[condition, '18_Quantity'] # ok

            # TPT_df.loc[condition, '24_Market_valuation_in_portfolio_currency_(B)'] = TPT_df.loc[condition, '24_Market_valuation_in_portfolio_currency_(B)'] * TPT_df.loc[condition,'Adjust_Cash']
            # TPT_df.loc[condition, '25_Clean_market_valuation_in_portfolio_currency_(B)'] = TPT_df.loc[condition, '25_Clean_market_valuation_in_portfolio_currency_(B)'] * TPT_df.loc[condition,'Adjust_Cash']
            # TPT_df.loc[condition, '28_Market_exposure_amount_in_portfolio_currency_(B)'] = TPT_df.loc[condition, '28_Market_exposure_amount_in_portfolio_currency_(B)'] * TPT_df.loc[condition,'Adjust_Cash']

            # Creates a boolean condition where the value is 'Cash' and 'Forward'.
            condition = (TPT_df['Type_Actif2_x'] == 'Cash') & (TPT_df['Type_Support2_x'] == 'Forward')
            TPT_df.loc[condition, '27_Market_exposure_amount_in_quotation_currency_(A)'] = TPT_df.loc[
                condition, '18_Quantity']

            # Create the condition to select rows
            condition = ((TPT_df['Type_Support2_x'] == 'Options') | (TPT_df['Type_Support2_x'] == 'Futures'))

            # Update specific columns in TPT_df based on the condition
            TPT_df.loc[condition, '23_Clean_market_valuation_in_quotation_currency_(A)'] = TPT_df.loc[
                condition, '22_Market_valuation_in_quotation_currency_(A)']
            TPT_df.loc[condition, '25_Clean_market_valuation_in_portfolio_currency_(B)'] = TPT_df.loc[
                condition, '24_Market_valuation_in_portfolio_currency_(B)']

            # Create the condition to select rows
            condition = ~((TPT_df['Type_Actif2_x'] == 'Obligations') & (TPT_df['Type_Support2_x'] == 'Lignes'))

            # Update specific columns in TPT_df based on the condition
            TPT_df.loc[condition, '22_Market_valuation_in_quotation_currency_(A)'] = TPT_df.loc[
                condition, '23_Clean_market_valuation_in_quotation_currency_(A)']
            TPT_df.loc[condition, '25_Clean_market_valuation_in_portfolio_currency_(B)'] = TPT_df.loc[
                condition, '24_Market_valuation_in_portfolio_currency_(B)']

            # Condition to check if the column '20_Contract_size_for_derivatives' has a value
            condition = ~TPT_df['20_Contract_size_for_derivatives'].isnull()

            # Replace values according to the condition
            TPT_df.loc[condition, '15_Type_of_identification_code_for_the_instrument'] = '5'

            # Condition si ti fill 46_Issuer_name if empty for cash and Derivatives
            # For Cash Fill it anyway
            condition = (TPT_df['Type_Actif2_x'] == 'Cash')
            TPT_df.loc[condition, "46_Issuer_name"] = TPT_df.loc[condition, "133_custodian_name"]
            TPT_df.loc[condition, "54_Economic_sector"] = 'K6419'

            # For Derivatives if issuer is empty check if an issuer ManCo is available
            condition = ((TPT_df['Type_Support2_y'] == 'Forward') | (TPT_df['Type_Support2_y'] == 'Futures') | (
                        TPT_df['Type_Support2_y'] == 'Options')) & TPT_df["46_Issuer_name"].isnull() & ~TPT_df[
                "49_Name_of_the_group_of_the_issuer"].isnull()
            TPT_df.loc[condition, "46_Issuer_name"] = TPT_df.loc[condition, "49_Name_of_the_group_of_the_issuer"]
            # For Derivatives if issuer is empty check if an LEI issuer ManCo is available
            condition = ((TPT_df['Type_Support2_y'] == 'Forward') | (TPT_df['Type_Support2_y'] == 'Futures') | (
                        TPT_df['Type_Support2_y'] == 'Options')) & TPT_df["47_Issuer_identification_code"].isnull() & ~ \
                        TPT_df["50_Identification_of_the_group"].isnull()
            TPT_df.loc[condition, "47_Issuer_identification_code"] = TPT_df.loc[
                condition, "50_Identification_of_the_group"]
            # For Derivatives if issuer is empty check if an issuer ManCo is available
            condition = ((TPT_df['Type_Support2_y'] == 'Forward') | (TPT_df['Type_Support2_y'] == 'Futures') | (
                        TPT_df['Type_Support2_y'] == 'Options')) & TPT_df["46_Issuer_name"].isnull()
            TPT_df.loc[condition, "46_Issuer_name"] = TPT_df.loc[condition, "133_custodian_name"]

            condition = TPT_df["46_Issuer_name"] == 'Bank Of New York Mellon Corp/T'
            TPT_df.loc[condition, "47_Issuer_identification_code"] = 'HPFHU0OQ28E4N0NFVK49'
            TPT_df.loc[condition, "49_Name_of_the_group_of_the_issuer"] = 'Bank of New York Mellon Corp/T'
            condition = TPT_df["49_Name_of_the_group_of_the_issuer"] == 'Bank Of New York Mellon Corp/T'
            TPT_df.loc[condition, "50_Identification_of_the_group"] = 'HPFHU0OQ28E4N0NFVK49'
            TPT_df.loc[condition, "52_Issuer_country"] = 'US'
            TPT_df.loc[condition, "53_Issuer_economic_area"] = 'US'

            condition = TPT_df["46_Issuer_name"] == 'BNP Paribas'
            TPT_df.loc[condition, "47_Issuer_identification_code"] = '549300WCGB70D06XZS54'
            TPT_df.loc[condition, "49_Name_of_the_group_of_the_issuer"] = 'BNP Paribas SA'
            TPT_df.loc[condition, "50_Identification_of_the_group"] = 'R0MUWSFPU8MPRO8K5P83'
            TPT_df.loc[condition, "52_Issuer_country"] = 'FR'
            TPT_df.loc[condition, "53_Issuer_economic_area"] = 'FR'

            condition = TPT_df["46_Issuer_name"] == 'BNP Paribas Succursale de Luxembourg'
            TPT_df.loc[condition, "47_Issuer_identification_code"] = 'UAIAINAJ28P30E5GWE37'
            TPT_df.loc[condition, "49_Name_of_the_group_of_the_issuer"] = 'BNP Paribas SA'
            TPT_df.loc[condition, "50_Identification_of_the_group"] = 'R0MUWSFPU8MPRO8K5P83'
            TPT_df.loc[condition, "52_Issuer_country"] = 'LU'
            TPT_df.loc[condition, "53_Issuer_economic_area"] = 'LU'

            condition = TPT_df["46_Issuer_name"] == 'CACEIS Bank'
            TPT_df.loc[condition, "47_Issuer_identification_code"] = '96950023SCR9X9F3L662'
            TPT_df.loc[condition, "49_Name_of_the_group_of_the_issuer"] = 'CREDIT AGRICOLE SA'

            condition = TPT_df["46_Issuer_name"] == 'Caceis Bank France'
            TPT_df.loc[condition, "47_Issuer_identification_code"] = '96950023SCR9X9F3L662'
            TPT_df.loc[condition, "49_Name_of_the_group_of_the_issuer"] = 'CREDIT AGRICOLE SA'

            condition = TPT_df["46_Issuer_name"] == 'Caceis Bank Luxembourg'
            TPT_df.loc[condition, "47_Issuer_identification_code"] = '96950023SCR9X9F3L662'
            TPT_df.loc[condition, "49_Name_of_the_group_of_the_issuer"] = 'CREDIT AGRICOLE SA'

            condition = (TPT_df["49_Name_of_the_group_of_the_issuer"] == 'CREDIT AGRICOLE SA') | (
                        TPT_df["49_Name_of_the_group_of_the_issuer"] == 'Credit Agricole Group') | (
                                    TPT_df["49_Name_of_the_group_of_the_issuer"] == 'Credit Agricole Groupe')
            TPT_df.loc[condition, "50_Identification_of_the_group"] = '969500TJ5KRTCJQWXH05'
            TPT_df.loc[condition, "52_Issuer_country"] = 'FR'
            TPT_df.loc[condition, "53_Issuer_economic_area"] = 'FR'

            condition = TPT_df["46_Issuer_name"] == 'State Street'
            TPT_df.loc[condition, "47_Issuer_identification_code"] = '549300NTJWXBTICDZY51'
            TPT_df.loc[condition, "49_Name_of_the_group_of_the_issuer"] = 'State Street'
            TPT_df.loc[condition, "50_Identification_of_the_group"] = '549300NTJWXBTICDZY51'
            TPT_df.loc[condition, "52_Issuer_country"] = 'US'
            TPT_df.loc[condition, "53_Issuer_economic_area"] = 'US'

            TPT_df.loc[:, "47_Issuer_identification_code"] = TPT_df["47_Issuer_identification_code"].replace(
                ["#N/A N/A", "Error"], None)
            TPT_df.loc[:, "50_Identification_of_the_group"] = TPT_df["50_Identification_of_the_group"].replace(
                ["#N/A N/A", "Error"], None)

            TPT_df.loc[TPT_df["49_Name_of_the_group_of_the_issuer"].isna() | (TPT_df[
                                                                                  "49_Name_of_the_group_of_the_issuer"].str.strip() == ""), "50_Identification_of_the_group"] = \
            TPT_df["47_Issuer_identification_code"]
            TPT_df.loc[TPT_df["49_Name_of_the_group_of_the_issuer"].isna() | (TPT_df[
                                                                                  "49_Name_of_the_group_of_the_issuer"].str.strip() == ""), "49_Name_of_the_group_of_the_issuer"] = \
            TPT_df["46_Issuer_name"]

            TPT_df['48_Type_of_identification_code_for_issuer'] = TPT_df['47_Issuer_identification_code'].apply(
                assign_value_LEI_Or_Empty)
            TPT_df['51_Type_of_identification_code_for_issuer_group'] = TPT_df['50_Identification_of_the_group'].apply(
                assign_value_LEI_Or_Empty)

            TPT_df['53_Issuer_economic_area'] = TPT_df['53_Issuer_economic_area'].map(Dict_Economic_Area_Code)
            TPT_df['13_Economic_zone_of_the_quotation_place'] = TPT_df['13_Economic_zone_of_the_quotation_place'].map(
                Dict_Economic_Area_Code)

            ##################################################################
            # condition = TPT_df['Type_Actif2_x'] == 'Change_Fx'
            # TPT_df[condition]
            ##################################################################

            # Condition to check if neither '18_Quantity' nor '19_Nominal_amount' have non-zero values
            condition = ~((TPT_df['26_Valuation_weight'].isnull() | (TPT_df['26_Valuation_weight'] == 0)) & (
                        TPT_df['27_Market_exposure_amount_in_quotation_currency_(A)'].isnull() | (
                            TPT_df['27_Market_exposure_amount_in_quotation_currency_(A)'] == 0)))

            # Remove rows where the condition is False
            TPT_df = TPT_df.loc[condition]

            # TPT_df = TPT_df.loc[condition,['14_Identification_code_of_the_instrument', '12_CIC_code_of_the_instrument', '17_Instrument_name', '21_Quotation_currency_(A)','Type_Actif2_x']]

            #   Format for TPT Coupon frequency (0=other than below options: 1=annual 2=biannual 4=quarterly 12=monthly 52=weekly)
            TPT_df['38_Coupon_payment_frequency'] = TPT_df['38_Coupon_payment_frequency'].apply(Process_Coupon)

            ####################################################################
            Coef_Part = Funds_VL.at[0, 'Actif_Part_Dev_PTF'] / Funds_VL.at[0, 'Actif_Net']

            columns_to_multiply = [
                "18_Quantity",
                "19_Nominal_amount",
                "22_Market_valuation_in_quotation_currency_(A)",
                "23_Clean_market_valuation_in_quotation_currency_(A)",
                "24_Market_valuation_in_portfolio_currency_(B)",
                "25_Clean_market_valuation_in_portfolio_currency_(B)",
                "27_Market_exposure_amount_in_quotation_currency_(A)",
                "28_Market_exposure_amount_in_portfolio_currency_(B)"
            ]
            ####################################################################

            # Itération sur chaque colonne pour appliquer la multiplication
            for column in columns_to_multiply:
                # Multiplication de chaque valeur dans la colonne par Coef_Part
                TPT_df[column] = TPT_df[column] * Coef_Part

            Shares_TPT_Dictionnary[ID_Fund_Part] = TPT_df

            TPT_df = TPT_df[['1_Portfolio_identifying_data',
                             '2_Type_of_identification_code_for_the_fund_share_or_portfolio',
                             '3_Portfolio_name', '4_Portfolio_currency_(B)',
                             '5_Net_asset_valuation_of_the_portfolio_or_the_share_class_in_portfolio_currency',
                             '6_Valuation_date',
                             '7_Reporting_date',
                             '8_Share_price',
                             '8b_Total_number_of_shares',
                             '9_Cash_ratio',
                             '10_Portfolio_modified_duration',
                             '11_Complete_SCR_delivery',
                             '12_CIC_code_of_the_instrument',
                             '13_Economic_zone_of_the_quotation_place',
                             '14_Identification_code_of_the_instrument',
                             '15_Type_of_identification_code_for_the_instrument',
                             '16_Grouping_code_for_multiple_leg_instruments',
                             '17_Instrument_name', '17b_Asset_liability',
                             '18_Quantity',
                             '19_Nominal_amount',
                             '20_Contract_size_for_derivatives',
                             '21_Quotation_currency_(A)',
                             '22_Market_valuation_in_quotation_currency_(A)',
                             '23_Clean_market_valuation_in_quotation_currency_(A)',
                             '24_Market_valuation_in_portfolio_currency_(B)',
                             '25_Clean_market_valuation_in_portfolio_currency_(B)',
                             '26_Valuation_weight', '27_Market_exposure_amount_in_quotation_currency_(A)',
                             '28_Market_exposure_amount_in_portfolio_currency_(B)',
                             '29_Market_exposure_amount_for_the_3rd_quotation_currency_(C)',
                             '30_Market_exposure_in_weight',
                             '31_Market_exposure_for_the_3rd_currency_in_weight_over_NAV',
                             '32_Interest_rate_type',
                             '33_Coupon_rate',
                             '34_Interest_rate_reference_identification',
                             '35_Identification_type_for_interest_rate_index',
                             '36_Interest_rate_index_name',
                             '37_Interest_rate_margin',
                             '38_Coupon_payment_frequency',
                             '39_Maturity_date',
                             '40_Redemption_type',
                             '41_Redemption_rate',
                             '42_Callable_putable',
                             '43_Call_put_date',
                             '44_Issuer_bearer_option_exercise',
                             '45_Strike_price_for_embedded_(call_put)_options',
                             '46_Issuer_name',
                             '47_Issuer_identification_code',
                             '48_Type_of_identification_code_for_issuer',
                             '49_Name_of_the_group_of_the_issuer',
                             '50_Identification_of_the_group',
                             '51_Type_of_identification_code_for_issuer_group',
                             '52_Issuer_country',
                             '53_Issuer_economic_area',
                             '54_Economic_sector',
                             '55_Covered_not_covered',
                             '56_Securitisation',
                             '57_Explicit_guarantee_by_the_country_of_issue',
                             '58_Subordinated_debt',
                             '58b_Nature_of_the_tranche',
                             '59_Credit_quality_step',
                             '60_Call_Put_Cap_Floor',
                             '61_Strike_price',
                             '62_Conversion_factor_(convertibles)_concordance_factor_parity_(options)',
                             '63_Effective_date_of_instrument',
                             '64_Exercise_type',
                             '65_Hedging_rolling',
                             '67_CIC_of_the_underlying_asset',
                             '68_Identification_code_of_the_underlying_asset',
                             '69_Type_of_identification_code_for_the_underlying_asset',
                             '70_Name_of_the_underlying_asset',
                             '71_Quotation_currency_of_the_underlying_asset_(C)',
                             '72_Last_valuation_price_of_the_underlying_asset',
                             '73_Country_of_quotation_of_the_underlying_asset',
                             '74_Economic_area_of_quotation_of_the_underlying_asset',
                             '75_Coupon_rate_of_the_underlying_asset',
                             '76_Coupon_payment_frequency_of_the_underlying_asset',
                             '77_Maturity_date_of_the_underlying_asset',
                             '78_Redemption_profile_of_the_underlying_asset',
                             '79_Redemption_rate_of_the_underlying_asset',
                             '80_Issuer_name_of_the_underlying_asset',
                             '81_Issuer_identification_code_of_the_underlying_asset',
                             '82_Type_of_issuer_identification_code_of_the_underlying_asset',
                             '83_Name_of_the_group_of_the_issuer_of_the_underlying_asset',
                             '84_Identification_of_the_group_of_the_underlying_asset',
                             '85_Type_of_the_group_identification_code_of_the_underlying_asset',
                             '86_Issuer_country_of_the_underlying_asset',
                             '87_Issuer_economic_area_of_the_underlying_asset',
                             '88_Explicit_guarantee_by_the_country_of_issue_of_the_underlying_asset',
                             '89_Credit_quality_step_of_the_underlying_asset',
                             '90_Modified_duration_to_maturity_date',
                             '91_Modified_duration_to_next_option_exercise_date',
                             '92_Credit_sensitivity',
                             '93_Sensitivity_to_underlying_asset_price_(delta)',
                             '94_Convexity_gamma_for_derivatives',
                             '94b_Vega', '95_Identification_of_the_original_portfolio_for_positions_embedded_in_a_fund',
                             '97_SCR_mrkt_IR_up_weight_over_NAV',
                             '98_SCR_mrkt_IR_down_weight_over_NAV',
                             '99_SCR_mrkt_eq_type1_weight_over_NAV',
                             '100_SCR_mrkt_eq_type2_weight_over_NAV',
                             '101_SCR_mrkt_prop_weight_over_NAV',
                             '102_SCR_mrkt_spread_bonds_weight_over_NAV',
                             '103_SCR_mrkt_spread_structured_weight_over_NAV',
                             '104_SCR_mrkt_spread_derivatives_up_weight_over_NAV',
                             '105_SCR_mrkt_spread_derivatives_down_weight_over_NAV',
                             '105a_SCR_mrkt_FX_up_weight_over_NAV',
                             '105b_SCR_mrkt_FX_down_weight_over_NAV',
                             '106_Asset_pledged_as_collateral',
                             '107_Place_of_deposit',
                             '108_Participation',
                             '110_Valorisation_method',
                             '111_Value_of_acquisition',
                             '112_Credit_rating',
                             '113_Rating_agency',
                             '114_Issuer_economic_area',
                             '115_Fund_issuer_code',
                             '116_Fund_issuer_code_type',
                             '117_Fund_issuer_name',
                             '118_Fund_issuer_sector',
                             '119_Fund_issuer_group_code',
                             '120_Fund_issuer_group_code_type',
                             '121_Fund_issuer_group_name',
                             '122_Fund_issuer_country',
                             '123_Fund_CIC',
                             '123a_Fund_custodian_country',
                             '124_Duration',
                             '125_Accrued_income_(Security Denominated Currency)',
                             '126_Accrued_income_(Portfolio Denominated Currency)',
                             '127_Bond_floor_(convertible_instrument_only)',
                             '128_Option_premium_(convertible_instrument_only)',
                             '129_Valuation_yield',
                             '130_Valuation_z_spread',
                             '131_Underlying_asset_category',
                             '132_Infrastructure_investment',
                             '133_custodian_name',
                             '134_type1_private_equity_portfolio_eligibility',
                             '135_type1_private_equity_issuer_beta',
                             '137_Counterparty_sector',
                             '138_Collateral_eligibility',
                             '139_Collateral_Market_valuation_in_portfolio_currency',
                             '140_Custodian_identification_code',
                             '141_Type_of_custodian_identification_code',
                             '142_Bail-in_Rule',
                             '143_Maturity_date_expected',
                             '144_Modified_duration_to_maturity_date_expected',
                             '145_Credit_sensitivity_expected',
                             '146_PIK',
                             '147_Infrastructure_investment_additional_QRT',
                             '148_Economic_sector_NACE2.1',
                             '1000_TPT_Version']]

            '''
            TPT_df['9_Cash_ratio'] = TPT_df['9_Cash_ratio'].round(5)
            TPT_df['18_Quantity'] = TPT_df['18_Quantity'].round(5)
            TPT_df['22_Market_valuation_in_quotation_currency_(A)'] = TPT_df['22_Market_valuation_in_quotation_currency_(A)'].round(5)
            TPT_df['23_Clean_market_valuation_in_quotation_currency_(A)'] = TPT_df['23_Clean_market_valuation_in_quotation_currency_(A)'].round(5)
            TPT_df['24_Market_valuation_in_portfolio_currency_(B)'] = TPT_df['24_Market_valuation_in_portfolio_currency_(B)'].round(5)
            TPT_df['25_Clean_market_valuation_in_portfolio_currency_(B)'] = TPT_df['25_Clean_market_valuation_in_portfolio_currency_(B)'].round(5)
            TPT_df['26_Valuation_weight'] = TPT_df['26_Valuation_weight'].round(4)
            TPT_df['27_Market_exposure_amount_in_quotation_currency_(A)'] = TPT_df['27_Market_exposure_amount_in_quotation_currency_(A)'].round(5)
            TPT_df['28_Market_exposure_amount_in_portfolio_currency_(B)'] = TPT_df['28_Market_exposure_amount_in_portfolio_currency_(B)'].round(5)
            TPT_df['30_Market_exposure_in_weight'] = TPT_df['30_Market_exposure_in_weight'].round(4)
            '''

            TPT_df.loc[:, '9_Cash_ratio'] = TPT_df['9_Cash_ratio'].round(5)
            TPT_df.loc[:, '18_Quantity'] = TPT_df['18_Quantity'].round(5)
            TPT_df.loc[:, '22_Market_valuation_in_quotation_currency_(A)'] = TPT_df[
                '22_Market_valuation_in_quotation_currency_(A)'].round(5)
            TPT_df.loc[:, '23_Clean_market_valuation_in_quotation_currency_(A)'] = TPT_df[
                '23_Clean_market_valuation_in_quotation_currency_(A)'].round(5)
            TPT_df.loc[:, '24_Market_valuation_in_portfolio_currency_(B)'] = TPT_df[
                '24_Market_valuation_in_portfolio_currency_(B)'].round(5)
            TPT_df.loc[:, '25_Clean_market_valuation_in_portfolio_currency_(B)'] = TPT_df[
                '25_Clean_market_valuation_in_portfolio_currency_(B)'].round(5)
            TPT_df.loc[:, '26_Valuation_weight'] = TPT_df['26_Valuation_weight'].round(4)
            TPT_df.loc[:, '27_Market_exposure_amount_in_quotation_currency_(A)'] = TPT_df[
                '27_Market_exposure_amount_in_quotation_currency_(A)'].round(5)
            TPT_df.loc[:, '28_Market_exposure_amount_in_portfolio_currency_(B)'] = TPT_df[
                '28_Market_exposure_amount_in_portfolio_currency_(B)'].round(5)
            TPT_df.loc[:, '30_Market_exposure_in_weight'] = TPT_df['30_Market_exposure_in_weight'].round(4)

            TPT_df.loc[:, '17b_Asset_liability'] = "A"

            condition = (TPT_df['52_Issuer_country'].isnull() & (
                        (TPT_df['49_Name_of_the_group_of_the_issuer'] == 'LFPI Groupe') | (
                            TPT_df['49_Name_of_the_group_of_the_issuer'] == 'French Republic')))
            TPT_df.loc[condition, "52_Issuer_country"] = 'FR'
            TPT_df.loc[condition, "53_Issuer_economic_area"] = 1

            condition = (TPT_df['32_Interest_rate_type'] == 'ZERO COUPON')
            TPT_df.loc[condition, "32_Interest_rate_type"] = 'FIXED'

            TPT_df.loc[:, "123a_Fund_custodian_country"] = TPT_df["133_custodian_name"].apply(map_custodian_to_country)

            Date_Forlder = datetime.strptime(Get_Last_Previous_Month_Date(Reporting_Date), '%Y-%d-%m').strftime('%Y-%m')
            P_D = scope_Public_Private[Mnemo]

            Folder = f'S:\\Dev\\5_Reporting\\1_Regulatory_Reports\\1_TPT\\1_Archives\\{Date_Forlder}\\{P_D}'
            if not os.path.exists(Folder):
                os.makedirs(Folder)

            formatted_date_ref = datetime.strptime(Nav_Date, '%Y-%d-%m').strftime("%Y%m%d")
            formatted_date_reporting = datetime.now().strftime("%Y%m%d")
            File_Name = f"{formatted_date_ref}_TPTV7_{ISIN_Shares}_{formatted_date_reporting}_{Mnemo_Fund_Part}"

            if not TPT_df.empty:
                # print(f'La part est : {Fund_Part_List.loc[Num_Rows, "Mnemo_Fund_Part"]}. Les fichiers à concaténer ont un format comme suit:')
                # print(f'Nombre de lignes à concaténer de TPT_df: {TPT_df.shape[0]}')
                # print(f'Nombre de colonnes à concaténer de TPT_df: {TPT_df.shape[1]}')
                # print(f'Nombre de lignes à concaténer de TPT_Concatenated: {TPT_Concatenated.shape[0]}')
                # print(f'Nombre de colonnes à concaténer de TPT_Concatenated: {TPT_Concatenated.shape[1]}')

                TPT_Concatenated = pd.concat([TPT_Concatenated, TPT_df], ignore_index=True)

            #  DEBUG ############################################################################################
            #
            # if Key_Fund == 131 or Key_Fund == 133 or Key_Fund == 134 :
            #     print("")
            #     print (f"Ptf = {Key_Fund} ")
            #     print (f"Nav_Date = {Nav_Date}")
            #     print (f"TPT : ")
            #     print (TPT_df)
            #####################################################################################################

            TPT_df.to_excel(f'{Folder}\\{File_Name}.xlsx', index=False)

        Warning_Dictionnary[Key_Fund] = Warning_List
        Funds_TPT_Dictionnary[Key_Fund] = Shares_TPT_Dictionnary

for cle, valeur in Warning_Dictionnary.items():
    print("\n================================================================")
    print(f"    {Fund_List[Fund_List['Key_Fund'] == cle]['Lib_Fund'].values[0]} :")
    print("================================================================")
    for value in valeur:
        print(f"         - {value}")

# TPT_Concatenated.to_excel(f'{Folder}\\TPT_Concatenated.xlsx', index=False)




from Utils import *
from Input import *

import datetime
import pandas as pd
from pandas.tseries.offsets import BDay

pd.set_option('display.max_rows', None)
####################################################################################
# Setup                                                                            #
####################################################################################
# Reporting Language
LANG = 'FRA'
# LANG = 'ENG'
# LANG = 'DEU'

# Date For Fees (End of Year)
aujourdhui = datetime.date.today()
# aujourdhui = datetime.date(2025,7,15)  # For Testing

dernier_jour_annee_passee = datetime.date(aujourdhui.year - 1, 12, 31)
dernier_jour_ouvre_annee_passee = pd.date_range(end=dernier_jour_annee_passee, periods=1, freq=BDay())[-1].date()
cobdate = dernier_jour_ouvre_annee_passee.strftime('%d/%m/%Y')
KID_Date = dernier_jour_ouvre_annee_passee.strftime('%Y-%m-%d')
print(
    "=                                                                                                                                                         =")
print(
    f"= Le dernier jour ouvré de l'année dernière était le: {cobdate}                                                                                          =")

# Date For Other Calculation (Last Bday of previous month)
premier_jour_mois_actuel = datetime.date(aujourdhui.year, aujourdhui.month, 1)
dernier_jour_mois_passe = premier_jour_mois_actuel - datetime.timedelta(days=1)
dernier_jour_ouvre_mois_passe = pd.date_range(end=dernier_jour_mois_passe, periods=1, freq=BDay())[-1].date()
Last_Month = dernier_jour_ouvre_mois_passe.strftime('%d/%m/%Y')
print(
    f"= Le dernier jour ouvré du mois passé était le: {Last_Month}                                                                                                =")
print(
    "=                                                                                                                                                         =")
#############################################################################################################
#   Add For Run Late On January                                                                             #
#############################################################################################################
# premier_jour_mois_actuel = datetime.date(2025, 1, 1)
# dernier_jour_mois_passe = datetime.date(2024, 12, 31)
# Last_Month = dernier_jour_ouvre_mois_passe.strftime('%d/%m/%Y')

#############################################################################################################

# Create And Check Folder
mois = dernier_jour_mois_passe.strftime('%m')
annee = dernier_jour_mois_passe.strftime('%Y')
nom_dossier = f"{annee}-{mois}"
chemin_dossier = os.path.join('\\\\10.130.1.100\\mandarine\\PUBLIC\\MANDARINE SYSTEME DEVELOPPEMENT\\Dev\\5_Reporting\\1_Regulatory_Reports\\2_EPT\\1_Archives\\',nom_dossier)
print(
    "=                                                                                                                                                         =")
print(
    "= Chemin du dossier:                                                                                                                                      =")
print(
    "=                                                                                                                                                         =")
print(
    f"= {chemin_dossier}                                                                                                                                        =")
# Vérifier si le dossier existe déjà, sinon le créer
if not os.path.exists(chemin_dossier):
    os.makedirs(chemin_dossier)

Dict_Lang = {'FRA': ('FR', 'fr'),
             'DEU': ('DE', 'de'),
             'ENG': ('INT', 'en'),
             'ITA': ('IT', 'it')}

if LANG == 'FRA' or LANG == 'ENG':

    # ,CONCAT('https://www.mandarine-gestion.com/FR/fr/docs/funds/',LOWER(REPLACE(RF.Lib_Fund, ' ', '-')),'/',UPPER(RFP.ISIN_Fund),'/KID') AS '00075_PRIIPs_KID_Web_Address'
    # ,RF.cic_code AS '00090_Fund_CIC_code'
    # ,RF.Freq_VL AS '01010_Valuation_Frequency'

    # ,CONCAT('https://www.mandarine-gestion.com/{Dict_Lang[LANG][0]}/{Dict_Lang[LANG][1]}/funds/',LOWER(REPLACE(RF.Lib_Fund, ' ', '-')),'/shares/',LOWER(RFP.ISIN_Fund)) AS '02190_Past_Performance_Link'
    # ,CONCAT('https://www.mandarine-gestion.com/{Dict_Lang[LANG][0]}/{Dict_Lang[LANG][1]}/funds/',LOWER(REPLACE(RF.Lib_Fund, ' ', '-')),'/shares/',LOWER(RFP.ISIN_Fund)) AS '02200_Previous_Performance_Scenarios_Calculation_Link'
    # ,10 AS '02210_Past_Performance_Number_Of_Years'
    Req_SQL = f"""

    WITH #LAST_EPT AS (
    SELECT 
    ISIN,
    Mnemo_Fund_Part,  
    TRIM(REPLACE(Mnemo_Fund_Group, CHAR(160), '')) AS Mnemo_Fund_Group, 
    MAX(DATE_MAJ) AS DATE_MAJ 
    FROM Tb_MO_Ref_EPT 
    GROUP BY 
    ISIN, 
    Mnemo_Fund_Part, 
    TRIM(REPLACE(Mnemo_Fund_Group, CHAR(160), '')) 
    ),

    #FILTER_EPT AS (
    SELECT TMRE.* FROM #LAST_EPT LE LEFT JOIN Tb_MO_Ref_EPT TMRE ON LE.DATE_MAJ = TMRE.DATE_MAJ AND LE.ISIN = TMRE.ISIN
    )
    SELECT 
    'V21' AS '00001_EPT_Version'
    ,NULL AS '00002_EPT_Producer_Name'
    ,NULL AS '00004_EPT_Producer_Email'
    ,FORMAT( GETDATE() , 'yyyy-MM-dd HH:mm:ss') AS '00005_File_Generation_Date_And_Time'
    ,'N' AS '00006_EPT_Data_Reporting_Narratives'
    ,'Y' AS '00007_EPT_Data_Reporting_Costs'
    ,'N' AS '00008_EPT_Data_Reporting_Additional_Requirements_German_MOPs'
    ,'N' AS '00009_EPT_Additional_Information_Structured_Products'
    ,'Mandarine Gestion' AS '00010_Portfolio_Manufacturer_Name'
    ,'Mandarine Gestion' AS '00015_Portfolio_Manufacturer_Group_Name'
    ,NULL AS '00016_Portfolio_Manufacturer_LEI'
    ,NULL AS '00017_Portfolio_Manufacturer_Email'
    ,NULL AS '00020_Portfolio_Guarantor_Name'
    ,RFP.ISIN_Fund AS '00030_Portfolio_Identifying_Data'
    ,1 AS '00040_Type_Of_Identification_Code_For_The_Fund_Share_Or_Portfolio'
    ,RFP.Lib_Fund_Part AS '00050_Portfolio_Name'
    ,RFP.Devise_Part AS '00060_Portfolio_Or_Share_Class_Currency'
    ,'{KID_Date}' AS '00070_PRIIPs_KID_Publication_Date'
    ,NULL AS '00075_PRIIPs_KID_Web_Address'
    ,2 AS '00080_Portfolio_PRIIPS_Category'
    ,RF.cic_code AS '00090_Fund_CIC_code'
    ,'N' AS '00110_Is_An_Autocallable_Product'
    ,'{LANG}' AS '00120_Reference_Language'
    ,NULL AS '01010_Valuation_Frequency'
    ,TB_SRI.vev AS '01020_Portfolio_VEV_Reference'
    ,NULL AS '01030_IS_Flexible'
    ,NULL AS '01040_Flex_VEV_Historical'
    ,NULL AS '01050_Flex_VEV_Ref_Asset_Allocation'
    ,'N' AS '01060_IS_Risk_Limit_Relevant'
    ,NULL AS '01070_Flex_VEV_Risk_Limit'
    ,'N' AS '01080_Existing_Credit_Risk'
    ,TB_SRI.sri AS '01090_SRI'
    ,'N' AS '01095_IS_SRI_Adjusted'
    ,TB_SRI.sri AS '01100_MRM'
    ,TB_SRI.CRM AS '01110_CRM'
    ,TB_SRI.RHP AS'01120_Recommended_Holding_Period'
    ,CASE WHEN RF.Date_Maturite_Fonds IS NULL THEN 'N' ELSE 'Y' END AS '01125_Has_A_Contractual_Maturity_Date'
    ,RF.Date_Maturite_Fonds AS '01130_Maturity_Date'
    ,'L' AS '01140_Liquidity_Risk'
    ,TB_SRI.ReturnValue_UnFav_1 AS '02010_Portfolio_Return_Unfavourable_Scenario_1_Year'
    ,TB_SRI.ReturnValue_UnFav_Hrhp AS '02020_Portfolio_Return_Unfavourable_Scenario_Half_RHP'
    ,TB_SRI.ReturnValue_UnFav_Rhp AS '02030_Portfolio_Return_Unfavourable_Scenario_RHP_Or_First_Call_Date'
    ,'N' AS '02032_Autocall_Applied_Unfavourable_Scenario'
    ,NULL AS '02035_Autocall_Date_Unfavourable_Scenario'
    ,TB_SRI.ReturnValue_Mod_1 AS '02040_Portfolio_Return_Moderate_Scenario_1_Year'
    ,TB_SRI.ReturnValue_Mod_Hrhp AS '02050_Portfolio_Return_Moderate_Scenario_Half_RHP'
    ,TB_SRI.ReturnValue_Mod_Rhp AS '02060_Portfolio_Return_Moderate_Scenario_RHP_Or_First_Call_Date'
    ,'N' AS '02062_Autocall_Applied_Moderate_Scenario'
    ,NULL AS '02065_Autocall_Date_Moderate_Scenario'
    ,TB_SRI.ReturnValue_Fav_1 AS '02070_Portfolio_Return_Favourable_Scenario_1_Year'
    ,TB_SRI.ReturnValue_Fav_Hrhp AS '02080_Portfolio_Return_Favourable_Scenario_Half_RHP'
    ,TB_SRI.ReturnValue_Fav_Rhp AS '02090_Portfolio_Return_Favourable_Scenario_RHP_Or_First_Call_Date'
    ,'N' AS '02092_Autocall_Applied_Favourable_Scenario'
    ,NULL AS '02095_Autocall_Date_Favourable_Scenario'
    ,TB_SRI.ReturnValue_Stress_1 AS '02100_Portfolio_return_stress_scenario_1_year'
    ,TB_SRI.ReturnValue_Stress_Hrhp AS '02110_Portfolio_return_stress_scenario_half_RHP'
    ,TB_SRI.ReturnValue_Stress_Rhp AS '02120_Portfolio_Return_Stress_Scenario_RHP_Or_First_Call_Date'
    ,'N' AS '02122_Autocall_Applied_Stress_Scenario'
    ,NULL AS '02125_Autocall_Date_Stress_Scenario'
    ,TB_SRI.m0 AS '02130_Portfolio_Number_Of_Observed_Return_M0'
    ,TB_SRI.m1 AS '02140_Portfolio_Mean_Observed_Returns_M1'
    ,TB_SRI.volatility AS'02150_Portfolio_Observed_Sigma'
    ,TB_SRI.Skewness AS '02160_Portfolio_Observed_Skewness'
    ,TB_SRI.Kurtosis AS '02170_Portfolio_Observed_Excess_Kurtosis'
    ,TB_SRI.Stressed_Volatility AS '02180_Portfolio_Observed_Stressed_Volatility'
    ,'N' AS '02185_Portfolio_Past_Performance_Disclosure_Required'
    ,NULL AS '02190_Past_Performance_Link'
    ,NULL AS '02200_Previous_Performance_Scenarios_Calculation_Link'
    ,NULL AS '02210_Past_Performance_Number_Of_Years'
    ,10000 AS '02220_Reference_Invested_Amount'
    ,RFP.Tx_Frais_Entree_Max AS '03010_One_off_cost_Portfolio_entry_cost'
    ,0 AS '03015_One_off_cost_Portfolio_entry_cost_Acquired'
    ,RFP.Tx_Frais_Sortie_Max AS '03020_One_off_costs_Portfolio_exit_cost_at_RHP'
    ,RFP.Tx_Frais_Sortie_Max AS '03030_One_off_costs_Portfolio_exit_cost_at_1_year'
    ,RFP.Tx_Frais_Sortie_Max AS '03040_One_off_costs_Portfolio_exit_cost_at_half_RHP'
    ,'N' AS '03050_One_off_costs_Portfolio_sliding_exit_cost_Indicator'
    ,REPT.PTF_OTHER_COSTS_UCITS AS '03060_Ongoing_Costs_Management_Fees_And_Other_Administrative_Or_Operating_Costs'
    ,REPT.PTF_TRANSACTION_COSTS AS '03080_Ongoing_costs_Portfolio_transaction_costs'
    ,CASE WHEN RFP.Perf_Fees IS NULL OR RFP.Perf_Fees = '' OR RFP.Perf_Fees = '-'THEN 'N' ELSE 'Y' END AS '03090_Existing_Incidental_Costs_Portfolio'
    ,CASE WHEN RFP.Perf_Fees IS NULL OR RFP.Perf_Fees = '' OR RFP.Perf_Fees = '-'THEN NULL ELSE REPT.PTF_PERFORMANCE_FEES_UCITS END AS '03095_Incidental_costs'
    ,NULL AS '04020_Comprehension_Alert_Portfolio'
    ,NULL AS '04030_Intended_target_market_retail_investor_Portfolio'
    ,NULL AS '04040_Investment_objective_Portfolio'
    ,NULL AS '04050_Risk_narrative_Portfolio'
    ,NULL AS '04060_Other_materially_relevant_risk_narrative_Portfolio'
    ,NULL AS '04070_Type_of_underlying_Investment_Option'
    ,NULL AS '04080_Capital_Guarantee'
    ,NULL AS '04081_Capital_Guarantee_Level'
    ,NULL AS '04082_Capital_Guarantee_Limitations'
    ,NULL AS '04083_Capital_Guarantee_Early_Exit_Conditions'
    ,NULL AS '04084_Capital_guarantee_Portfolio'
    ,NULL AS '04085_Possible_maximum_loss_Portfolio'
    ,NULL AS '04086_Description_Past_Interval_Unfavourable_Scenario'
    ,NULL AS '04087_Description_Past_Interval_Moderate_Scenario'
    ,NULL AS '04088_Description_Past_Interval_Favourable_Scenario'
    ,NULL AS '04089_Was_Benchmark_Used_Performance_Calculation'
    ,NULL AS '04090_Portfolio_Performance_Fees_Carried_Interest_Narrative'
    ,NULL AS '04120_One_Off_Cost_Portfolio_Entry_Cost_Description'
    ,NULL AS '04130_One_Off_Cost_Portfolio_Exit_Cost_Description'
    ,NULL AS '04140_Ongoing_Costs_Portfolio_Management_Costs_Description'
    ,NULL AS '04150_Do_Costs_Depend_On_Invested_Amount'
    ,NULL AS '04160_Cost_Dependence_Explanation'
    ,NULL AS '06005_German_MOPs_Reference_Date'
    ,NULL AS '06010_Bonds_Weight'
    ,NULL AS '06020_Annualized_Return_Volatility'
    ,NULL AS '06030_Duration_Bonds'
    ,NULL AS '06040_Existing_Capital_Preservation'
    ,NULL AS '06050_Capital_Preservation_Level'
    ,NULL AS '06060_Time_Interval_Maximum_Loss'
    ,NULL AS '06070_Uses_PI'
    ,NULL AS '06080_Multiplier_PI'
    ,NULL AS '07005_First_Possible_Call_Date'
    ,NULL AS '07010_Total_Cost_1_Year_Or_First_Call'
    ,NULL AS '07020_RIY_1_Year_Or_First_Call'
    ,NULL AS '07030_Total_Cost_Half_RHP'
    ,NULL AS '07040_RIY_Half_RHP'
    ,NULL AS '07050_Total_Cost_RHP'
    ,NULL AS '07060_RIY_RHP'
    ,NULL AS '07070_One_Off_Costs_Portfolio_Entry_Cost'
    ,NULL AS '07080_One_Off_Costs_Portfolio_Exit_Cost'
    ,NULL AS '07090_Ongoing_Costs_Portfolio_Transaction_Costs'
    ,NULL AS '07100_Ongoing_Costs_Management_Fees_And_Other_Administrative_Or_Operating_Costs'
    ,NULL AS '07110_Incidental_Costs_Portfolio_Performance_Fees_Carried _Interest'
    ,NULL AS '08010_UK_PRIIP_Or_UCITS_Or_Both_data_delivery'
    ,NULL AS '08020_UK_Ongoing_Costs_Portfolio_Transaction_Costs'
    ,NULL AS '08030_UK_Transactions_costs_methodology'
    ,NULL AS '08040_UK_Anti_Dilution_Benefit_Derived'
    ,NULL AS '08045_UK_PRIIPs_Data_Reference_Date'
    ,NULL AS '08050_UK_PRIIPs_KID_Publication_Date'
    ,NULL AS '08060_UK_PRIIPs_KID_Web_Address'
    ,NULL AS '08070_Investment_Objective_Portfolio'
    ,NULL AS '08080_UK_Other_Materially_Relevant_Risk_Narrative_Portfolio'
    ,NULL AS '08090_UK_Performance_Information_Main_Factors'
    ,NULL AS '08100_UK_Performance_Information_Comparator'
    ,NULL AS '08110_UK_Performance_Information_Higher_Returns'
    ,NULL AS '08120_UK_Performance_Information_Lower_Returns_Or_Loss'
    ,NULL AS '08130_UK_Performance_Information_Adverse_Conditions'
    ,NULL AS '08140_UK_Assumed_Portfolio_Return'
    ,NULL AS '08150_UCITS_KIID_Publication_Date'
    ,NULL AS '08160_UCITS_KIID_Web_Address'
    ,NULL AS '08170_UCITS_SRRI'
    ,NULL AS '08180_UCITS_Ongoing_Charges'
    ,NULL AS '08190_UCITS_Existing_Performance_Fees'
    ,NULL AS '08200_UCITS_Performance_Fees'

    FROM Ref_Funds AS RF 
    LEFT JOIN Ref_Funds_Parts AS RFP ON RFP.ref_fund_id = RF.Key_Fund
    FULL OUTER JOIN ( SELECT DISTINCT * FROM fundinfo_dts_file_legaldocs WHERE DocumentType = 'PRP' AND publicationCountry = 'FR') AS LD ON RFP.ISIN_Fund =  LD.ShareClass
    FULL OUTER JOIN #FILTER_EPT AS REPT ON RFP.Mnemo_Fund_Part = REPT.Mnemo_Fund_Part
    LEFT JOIN (SELECT DISTINCT * FROM tb_mo_priips_narratives WHERE language = 'FRA') AS PRIIPS ON RF.Key_Fund = PRIIPS.Key_Funds
    LEFT JOIN (
          SELECT * FROM Tb_rm_CALCULS_JASE_PRIIPS
          LEFT JOIN Ref_Funds_Parts AS RFP ON Tb_rm_CALCULS_JASE_PRIIPS.fundid = RFP.ISIN_Fund
          WHERE MONTH(cobdate)={mois} AND YEAR(cobdate)={annee}
        ) AS TB_SRI ON RFP.Key_Fund_Part = TB_SRI.Key_Fund_Part
    WHERE 
      RF.PTF_Reel = 1 
      AND RF.Date_Cloture IS NULL 
      AND RF.Mnemo_Fund NOT IN ('PE-A','PE-O','PE-D','NOVESS','SELENE','LIAGK','KLIAGK') 
      AND RFP.Code_Part <> 'MG'
      AND RFP.ISIN_Fund NOT IN ('ISINXXXXXXXX','LUXXXXXXXXXX','I','ISINXXXXXXXO',
                                'ISINXXXXXXXS','FRXXXXXXXXXX','ISINXXXKSQRF','ISINXXXXXDDL',
                                'ISINXXXXXGGI','ISINXXXXXGGR')
    ORDER BY Key_Fund
  """
    print(Req_SQL)

    Server = '10.130.1.20'
    database = 'MandarineGestion_Datawarehouse'
    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                          f'SERVER={Server};'
                          f'DATABASE={database};'
                          f'Trusted_Connection=yes')

    cursor = conn.cursor()
    cursor.execute(Req_SQL)
    results = cursor.fetchall()
    results = [list(row) for row in results]
    columns = [column[0] for column in cursor.description]
    cursor.close()
    conn.close()
    print('Dataframe created !')
    df = pd.DataFrame(results, columns=columns)
elif LANG == 'ENG':

    Server = '10.130.1.20'
    database = 'MandarineGestion_Datawarehouse'
    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                          f'SERVER={Server};'
                          f'DATABASE={database};'
                          f'Trusted_Connection=yes')

    List_Mnemo = """
  SELECT DISTINCT RFE.Mnemo_Fund_Part,RFP.Mnemo_Fund_Group   FROM Ref_Funds_Enregistement AS RFE 
  LEFT JOIN Ref_Funds_Parts AS RFP ON RFP.Mnemo_Fund_Part = RFE.Mnemo_Fund_Part
  LEFT JOIN Ref_Funds AS RF ON RF.Mnemo_Fund = RFP.Mnemo_Fund_Group
  WHERE RFE.Distribution_yes_no_res = 'YES' AND (RFE.Pays_Enregistrement = 'DE' OR  RFE.Pays_Enregistrement = 'IT') AND RF.PTF_Reel = 1 AND RF.Date_Cloture IS NULL
  """
    cursor = conn.cursor()
    cursor.execute(List_Mnemo)
    results = cursor.fetchall()
    results = [list(row) for row in results]
    columns = [column[0] for column in cursor.description]
    cursor.close()
    conn.close()
    List_Mnemo = pd.DataFrame(results, columns=columns)
    List_Mnemo_Filter = ','.join(["'" + str(value) + "'" for value in List_Mnemo['Mnemo_Fund_Part']])
    List_Mnemo_Filter = "(" + List_Mnemo_Filter + ")"

    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                          f'SERVER={Server};'
                          f'DATABASE={database};'
                          f'Trusted_Connection=yes')

    Req_SQL = f"""

  WITH #LAST_EPT AS (
  SELECT 
  ISIN,
  Mnemo_Fund_Part,  
  TRIM(REPLACE(Mnemo_Fund_Group, CHAR(160), '')) AS Mnemo_Fund_Group, 
  MAX(DATE_MAJ) AS DATE_MAJ 
  FROM Tb_MO_Ref_EPT 
  GROUP BY 
  ISIN, 
  Mnemo_Fund_Part, 
  TRIM(REPLACE(Mnemo_Fund_Group, CHAR(160), '')) 
  ),

  #FILTER_EPT AS (
  SELECT TMRE.* FROM #LAST_EPT LE LEFT JOIN Tb_MO_Ref_EPT TMRE ON LE.DATE_MAJ = TMRE.DATE_MAJ AND LE.ISIN = TMRE.ISIN
  ),

  LAST_BENCH AS (
	SELECT id_fund_part AS ID, MAX(start_bench_date) AS Max_Date FROM Ref_funds_part_benchs GROUP BY id_fund_part
  ),

  PART_BENCH_DISTINCT AS (
  SELECT * FROM LAST_BENCH LB LEFT JOIN Ref_funds_part_benchs  RFPB ON LB.ID = RFPB.id_fund_part AND LB.Max_Date = RFPB.start_bench_date
  )

  SELECT 
  'V21' AS '00001_EPT_Version'
  ,NULL AS '00002_EPT_Producer_Name'
  ,NULL AS '00004_EPT_Producer_Email'
  ,FORMAT( GETDATE() , 'yyyy-MM-dd HH:mm:ss') AS '00005_File_Generation_Date_And_Time'
  ,'Y' AS '00006_EPT_Data_Reporting_Narratives'
  ,'Y' AS '00007_EPT_Data_Reporting_Costs'
  ,'N' AS '00008_EPT_Data_Reporting_Additional_Requirements_German_MOPs'
  ,'N' AS '00009_EPT_Additional_Information_Structured_Products'
  ,'Mandarine Gestion' AS '00010_Portfolio_Manufacturer_Name'
  ,'Mandarine Gestion' AS '00015_Portfolio_Manufacturer_Group_Name'
  ,NULL AS '00016_Portfolio_Manufacturer_LEI'
  ,NULL AS '00017_Portfolio_Manufacturer_Email'
  ,NULL AS '00020_Portfolio_Guarantor_Name'
  ,RFP.ISIN_Fund AS '00030_Portfolio_Identifying_Data'
  ,1 AS '00040_Type_Of_Identification_Code_For_The_Fund_Share_Or_Portfolio'
  ,RFP.Lib_Fund_Part AS '00050_Portfolio_Name'
  ,RFP.Devise_Part AS '00060_Portfolio_Or_Share_Class_Currency'
  ,'{KID_Date}' AS '00070_PRIIPs_KID_Publication_Date'
  ,NULL AS '00075_PRIIPs_KID_Web_Address'
  ,2 AS '00080_Portfolio_PRIIPS_Category'
  ,RF.cic_code AS '00090_Fund_CIC_code'
  ,'N' AS '00110_Is_An_Autocallable_Product'
  ,'{LANG}' AS '00120_Reference_Language'
  ,NULL AS '01010_Valuation_Frequency'
  ,TB_SRI.vev AS '01020_Portfolio_VEV_Reference'
  ,NULL AS '01030_IS_Flexible'
  ,NULL AS '01040_Flex_VEV_Historical'
  ,NULL AS '01050_Flex_VEV_Ref_Asset_Allocation'
  ,'N' AS '01060_IS_Risk_Limit_Relevant'
  ,NULL AS '01070_Flex_VEV_Risk_Limit'
  ,'N' AS '01080_Existing_Credit_Risk'
  ,TB_SRI.sri AS '01090_SRI'
  ,'N' AS '01095_IS_SRI_Adjusted'
  ,TB_SRI.sri AS '01100_MRM'
  ,TB_SRI.CRM AS '01110_CRM'
  ,TB_SRI.RHP AS'01120_Recommended_Holding_Period'
  ,CASE WHEN RF.Date_Maturite_Fonds IS NULL THEN 'N' ELSE 'Y' END AS '01125_Has_A_Contractual_Maturity_Date'
  ,RF.Date_Maturite_Fonds AS '01130_Maturity_Date'
  ,'L' AS '01140_Liquidity_Risk'
  ,TB_SRI.ReturnValue_UnFav_1 AS '02010_Portfolio_Return_Unfavourable_Scenario_1_Year'
  ,TB_SRI.ReturnValue_UnFav_Hrhp AS '02020_Portfolio_Return_Unfavourable_Scenario_Half_RHP'
  ,TB_SRI.ReturnValue_UnFav_Rhp AS '02030_Portfolio_Return_Unfavourable_Scenario_RHP_Or_First_Call_Date'
  ,'N' AS '02032_Autocall_Applied_Unfavourable_Scenario'
  ,NULL AS '02035_Autocall_Date_Unfavourable_Scenario'
  ,TB_SRI.ReturnValue_Mod_1 AS '02040_Portfolio_Return_Moderate_Scenario_1_Year'
  ,TB_SRI.ReturnValue_Mod_Hrhp AS '02050_Portfolio_Return_Moderate_Scenario_Half_RHP'
  ,TB_SRI.ReturnValue_Mod_Rhp AS '02060_Portfolio_Return_Moderate_Scenario_RHP_Or_First_Call_Date'
  ,'N' AS '02062_Autocall_Applied_Moderate_Scenario'
  ,NULL AS '02065_Autocall_Date_Moderate_Scenario'
  ,TB_SRI.ReturnValue_Fav_1 AS '02070_Portfolio_Return_Favourable_Scenario_1_Year'
  ,TB_SRI.ReturnValue_Fav_Hrhp AS '02080_Portfolio_Return_Favourable_Scenario_Half_RHP'
  ,TB_SRI.ReturnValue_Fav_Rhp AS '02090_Portfolio_Return_Favourable_Scenario_RHP_Or_First_Call_Date'
  ,'N' AS '02092_Autocall_Applied_Favourable_Scenario'
  ,NULL AS '02095_Autocall_Date_Favourable_Scenario'
  ,TB_SRI.ReturnValue_Stress_1 AS '02100_Portfolio_return_stress_scenario_1_year'
  ,TB_SRI.ReturnValue_Stress_Hrhp AS '02110_Portfolio_return_stress_scenario_half_RHP'
  ,TB_SRI.ReturnValue_Stress_Rhp AS '02120_Portfolio_Return_Stress_Scenario_RHP_Or_First_Call_Date'
  ,'N' AS '02122_Autocall_Applied_Stress_Scenario'
  ,NULL AS '02125_Autocall_Date_Stress_Scenario'
  ,TB_SRI.m0 AS '02130_Portfolio_Number_Of_Observed_Return_M0'
  ,TB_SRI.m1 AS '02140_Portfolio_Mean_Observed_Returns_M1'
  ,TB_SRI.volatility AS'02150_Portfolio_Observed_Sigma'
  ,TB_SRI.Skewness AS '02160_Portfolio_Observed_Skewness'
  ,TB_SRI.Kurtosis AS '02170_Portfolio_Observed_Excess_Kurtosis'
  ,TB_SRI.Stressed_Volatility AS '02180_Portfolio_Observed_Stressed_Volatility'
  ,'N' AS '02185_Portfolio_Past_Performance_Disclosure_Required'
  ,NULL AS '02190_Past_Performance_Link'
  ,NULL AS '02200_Previous_Performance_Scenarios_Calculation_Link'
  ,NULL AS '02210_Past_Performance_Number_Of_Years'
  ,10000 AS '02220_Reference_Invested_Amount'
  ,RFP.Tx_Frais_Entree_Max AS '03010_One_off_cost_Portfolio_entry_cost'
  ,0 AS '03015_One_off_cost_Portfolio_entry_cost_Acquired'
  ,RFP.Tx_Frais_Sortie_Max AS '03020_One_off_costs_Portfolio_exit_cost_at_RHP'
  ,RFP.Tx_Frais_Sortie_Max AS '03030_One_off_costs_Portfolio_exit_cost_at_1_year'
  ,RFP.Tx_Frais_Sortie_Max AS '03040_One_off_costs_Portfolio_exit_cost_at_half_RHP'
  ,'N' AS '03050_One_off_costs_Portfolio_sliding_exit_cost_Indicator'
  ,REPT.PTF_OTHER_COSTS_UCITS AS '03060_Ongoing_Costs_Management_Fees_And_Other_Administrative_Or_Operating_Costs'
  ,REPT.PTF_TRANSACTION_COSTS AS '03080_Ongoing_costs_Portfolio_transaction_costs'
  ,CASE WHEN RFP.Perf_Fees IS NULL OR RFP.Perf_Fees = '' OR RFP.Perf_Fees = '-'THEN 'N' ELSE 'Y' END AS '03090_Existing_Incidental_Costs_Portfolio'
  ,CASE WHEN RFP.Perf_Fees IS NULL OR RFP.Perf_Fees = '' OR RFP.Perf_Fees = '-'THEN NULL ELSE REPT.PTF_PERFORMANCE_FEES_UCITS END AS '03095_Incidental_costs'
  ,'N' AS '04020_Comprehension_Alert_Portfolio'
  ,PRIIPS.[04030_Intended_target_market_retail_investor_Portfolio] AS '04030_Intended_target_market_retail_investor_Portfolio'
  ,PRIIPS.[04040_Investment_objective_Portfolio] AS '04040_Investment_objective_Portfolio'
  ,PRIIPS.[04050_Risk_narrative_Portfolio] AS '04050_Risk_narrative_Portfolio'
  ,PRIIPS.[04060_Other_materially_relevant_risk_narrative_Portfolio] AS '04060_Other_materially_relevant_risk_narrative_Portfolio'
  ,PRIIPS.[04070_Type_of_underlying_Investment_Option] AS '04070_Type_of_underlying_Investment_Option'
  ,'N' AS '04080_Capital_Guarantee'
  ,NULL AS '04081_Capital_Guarantee_Level'
  ,NULL AS '04082_Capital_Guarantee_Limitations'
  ,NULL AS '04083_Capital_Guarantee_Early_Exit_Conditions'
  ,NULL AS '04084_Capital_guarantee_Portfolio'
  ,NULL AS '04085_Possible_maximum_loss_Portfolio'
  ,CONCAT(CONVERT(VARCHAR,TB_SRI.unfavourable_scenario_startdate, 23),'/',CONVERT(VARCHAR,TB_SRI.unfavourable_scenario_enddate, 23)) AS '04086_Description_Past_Interval_Unfavourable_Scenario'
  ,CONCAT(CONVERT(VARCHAR,TB_SRI.moderate_scenario_startdate, 23),'/', CONVERT(VARCHAR,TB_SRI.moderate_scenario_enddate, 23)) AS '04087_Description_Past_Interval_Moderate_Scenario'
  ,CONCAT(CONVERT(VARCHAR,TB_SRI.favourable_scenario_startdate, 23),'/', CONVERT(VARCHAR,TB_SRI.favourable_scenario_enddate, 23)) AS '04088_Description_Past_Interval_Favourable_Scenario'
  ,CASE WHEN RFPB.id_bench IS NULL THEN 'N' ELSE 'Y' END AS '04089_Was_Benchmark_Used_Performance_Calculation'
  ,PRIIPS.[04090_Portfolio_Performance_Fees_Narrative] AS '04090_Portfolio_Performance_Fees_Carried_Interest_Narrative'
  ,NULL AS '04120_One_Off_Cost_Portfolio_Entry_Cost_Description'
  ,PRIIPS.exit_cost_narrative AS '04130_One_Off_Cost_Portfolio_Exit_Cost_Description'
  ,CONCAT(REPT.PTF_PERFORMANCE_FEES_UCITS, PRIIPS.mgmt_cost_description) AS '04140_Ongoing_Costs_Portfolio_Management_Costs_Description'
  ,'N' AS '04150_Do_Costs_Depend_On_Invested_Amount'
  ,NULL AS '04160_Cost_Dependence_Explanation'
  ,NULL AS '06005_German_MOPs_Reference_Date'
  ,NULL AS '06010_Bonds_Weight'
  ,NULL AS '06020_Annualized_Return_Volatility'
  ,NULL AS '06030_Duration_Bonds'
  ,'N' AS '06040_Existing_Capital_Preservation'
  ,NULL AS '06050_Capital_Preservation_Level'
  ,NULL AS '06060_Time_Interval_Maximum_Loss'
  ,'N' AS '06070_Uses_PI'
  ,NULL AS '06080_Multiplier_PI'
  ,NULL AS '07005_First_Possible_Call_Date'
  ,NULL AS '07010_Total_Cost_1_Year_Or_First_Call'
  ,NULL AS '07020_RIY_1_Year_Or_First_Call'
  ,NULL AS '07030_Total_Cost_Half_RHP'
  ,NULL AS '07040_RIY_Half_RHP'
  ,NULL AS '07050_Total_Cost_RHP'
  ,NULL AS '07060_RIY_RHP'
  ,NULL AS '07070_One_Off_Costs_Portfolio_Entry_Cost'
  ,NULL AS '07080_One_Off_Costs_Portfolio_Exit_Cost'
  ,NULL AS '07090_Ongoing_Costs_Portfolio_Transaction_Costs'
  ,NULL AS '07100_Ongoing_Costs_Management_Fees_And_Other_Administrative_Or_Operating_Costs'
  ,NULL AS '07110_Incidental_Costs_Portfolio_Performance_Fees_Carried _Interest'
  ,NULL AS '08010_UK_PRIIP_Or_UCITS_Or_Both_data_delivery'
  ,NULL AS '08020_UK_Ongoing_Costs_Portfolio_Transaction_Costs'
  ,NULL AS '08030_UK_Transactions_costs_methodology'
  ,NULL AS '08040_UK_Anti_Dilution_Benefit_Derived'
  ,NULL AS '08045_UK_PRIIPs_Data_Reference_Date'
  ,NULL AS '08050_UK_PRIIPs_KID_Publication_Date'
  ,NULL AS '08060_UK_PRIIPs_KID_Web_Address'
  ,NULL AS '08070_Investment_Objective_Portfolio'
  ,NULL AS '08080_UK_Other_Materially_Relevant_Risk_Narrative_Portfolio'
  ,NULL AS '08090_UK_Performance_Information_Main_Factors'
  ,NULL AS '08100_UK_Performance_Information_Comparator'
  ,NULL AS '08110_UK_Performance_Information_Higher_Returns'
  ,NULL AS '08120_UK_Performance_Information_Lower_Returns_Or_Loss'
  ,NULL AS '08130_UK_Performance_Information_Adverse_Conditions'
  ,NULL AS '08140_UK_Assumed_Portfolio_Return'
  ,NULL AS '08150_UCITS_KIID_Publication_Date'
  ,NULL AS '08160_UCITS_KIID_Web_Address'
  ,NULL AS '08170_UCITS_SRRI'
  ,NULL AS '08180_UCITS_Ongoing_Charges'
  ,NULL AS '08190_UCITS_Existing_Performance_Fees'
  ,NULL AS '08200_UCITS_Performance_Fees'
  FROM Ref_Funds AS RF 
  LEFT JOIN Ref_Funds_Parts AS RFP ON RFP.ref_fund_id = RF.Key_Fund
  LEFT JOIN PART_BENCH_DISTINCT RFPB ON RFP.Key_Fund_Part = RFPB.id_fund_part
  FULL OUTER JOIN #FILTER_EPT AS REPT ON RFP.Mnemo_Fund_Part = REPT.Mnemo_Fund_Part
  LEFT JOIN (SELECT DISTINCT * FROM tb_mo_priips_narratives WHERE language = 'ENG') AS PRIIPS ON RF.Key_Fund = PRIIPS.Key_Funds
  LEFT JOIN (
			  SELECT *
			  FROM [MandarineGestion_Datawarehouse].[dbo].[Tb_rm_CALCULS_JASE_PRIIPS]
			  LEFT JOIN Ref_Funds_Parts AS RFP ON Tb_rm_CALCULS_JASE_PRIIPS.fundid = RFP.ISIN_Fund
			  WHERE MONTH(cobdate)={mois} AND YEAR(cobdate)={annee}
			) AS TB_SRI ON RFP.Key_Fund_Part = TB_SRI.Key_Fund_Part
  WHERE RF.PTF_Reel = 1 AND RF.Date_Cloture IS NULL AND RF.Mnemo_Fund NOT IN ('PE-A','PE-O','PE-D') AND RFP.Statut_Part = 'Active' AND RFP.Mnemo_Fund_Part IN {List_Mnemo_Filter} AND RFP.Code_Part <> 'MG'
  AND RFP.ISIN_Fund NOT IN ('ISINXXXXXXXX','LUXXXXXXXXXX','I','ISINXXXXXXXO',
                            'ISINXXXXXXXS','FRXXXXXXXXXX','ISINXXXKSQRF','ISINXXXXXDDL',
                            'ISINXXXXXGGI','ISINXXXXXGGR')
  ORDER BY Key_Fund
"""

    cursor = conn.cursor()
    cursor.execute(Req_SQL)
    results = cursor.fetchall()
    results = [list(row) for row in results]
    columns = [column[0] for column in cursor.description]
    cursor.close()
    conn.close()
    df = pd.DataFrame(results, columns=columns)

elif LANG == 'DEU' or LANG == 'ITA':

    Server = '10.130.1.20'
    database = 'MandarineGestion_Datawarehouse'
    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                          f'SERVER={Server};'
                          f'DATABASE={database};'
                          f'Trusted_Connection=yes')

    List_Mnemo = """
  SELECT DISTINCT RFE.Mnemo_Fund_Part,RFP.Mnemo_Fund_Group   FROM Ref_Funds_Enregistement AS RFE 
  LEFT JOIN Ref_Funds_Parts AS RFP ON RFP.Mnemo_Fund_Part = RFE.Mnemo_Fund_Part
  LEFT JOIN Ref_Funds AS RF ON RF.Mnemo_Fund = RFP.Mnemo_Fund_Group
  WHERE RFE.Distribution_yes_no_res = 'YES' AND (RFE.Pays_Enregistrement = 'DE' OR  RFE.Pays_Enregistrement = 'IT') AND RF.PTF_Reel = 1 AND RF.Date_Cloture IS NULL
  """
    cursor = conn.cursor()
    cursor.execute(List_Mnemo)
    results = cursor.fetchall()
    results = [list(row) for row in results]
    columns = [column[0] for column in cursor.description]
    cursor.close()
    conn.close()
    List_Mnemo = pd.DataFrame(results, columns=columns)
    List_Mnemo_Filter = ','.join(["'" + str(value) + "'" for value in List_Mnemo['Mnemo_Fund_Part']])
    List_Mnemo_Filter = "(" + List_Mnemo_Filter + ")"

    List_Mnemo_Filter = "('PME_F','PME_G','PME_I','PME_L','PME_M','PME_R')"

    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                          f'SERVER={Server};'
                          f'DATABASE={database};'
                          f'Trusted_Connection=yes')

    # Additional Data For Germany

    # Req_Bond_Weight = f"SELECT CASE WHEN SUM(poids_inventaire) IS NULL THEN 0 ELSE SUM(poids_inventaire) END AS [06010_Bonds_Weight] FROM tb_mo_contribution WHERE Date_Contrib = '31/07/2024' AND nom_fonds = 'PME' AND type_actif2 = 'Obligations'"
    # Req_Bond_Duration = f"SELECT CASE WHEN SUM(expo_sensibilite) IS NULL THEN 0 ELSE SUM(poids_inventaire) END AS [06030_Duration_Bonds] FROM tb_mo_contribution WHERE Date_Contrib = '31/07/2024' AND nom_fonds = 'PME' AND type_actif2 = 'Obligations'"

    # cursor = conn.cursor()
    # cursor.execute(Req_Bond_Weight)
    # results = cursor.fetchall()

    Req_SQL = f"""

  WITH #LAST_EPT AS (
  SELECT 
  ISIN,
  Mnemo_Fund_Part,  
  TRIM(REPLACE(Mnemo_Fund_Group, CHAR(160), '')) AS Mnemo_Fund_Group, 
  MAX(DATE_MAJ) AS DATE_MAJ 
  FROM Tb_MO_Ref_EPT 
  GROUP BY 
  ISIN, 
  Mnemo_Fund_Part, 
  TRIM(REPLACE(Mnemo_Fund_Group, CHAR(160), '')) 
  ),

  #FILTER_EPT AS (
  SELECT TMRE.* FROM #LAST_EPT LE LEFT JOIN Tb_MO_Ref_EPT TMRE ON LE.DATE_MAJ = TMRE.DATE_MAJ AND LE.ISIN = TMRE.ISIN
  ),

  LAST_BENCH AS (
	SELECT id_fund_part AS ID, MAX(start_bench_date) AS Max_Date FROM Ref_funds_part_benchs GROUP BY id_fund_part
  ),

  PART_BENCH_DISTINCT AS (
  SELECT * FROM LAST_BENCH LB LEFT JOIN Ref_funds_part_benchs  RFPB ON LB.ID = RFPB.id_fund_part AND LB.Max_Date = RFPB.start_bench_date
  )

  SELECT 
  'V21' AS '00001_EPT_Version'
  ,NULL AS '00002_EPT_Producer_Name'
  ,NULL AS '00004_EPT_Producer_Email'
  ,FORMAT( GETDATE() , 'yyyy-MM-dd HH:mm:ss') AS '00005_File_Generation_Date_And_Time'
  ,'Y' AS '00006_EPT_Data_Reporting_Narratives'
  ,'Y' AS '00007_EPT_Data_Reporting_Costs'
  ,'Y' AS '00008_EPT_Data_Reporting_Additional_Requirements_German_MOPs'
  ,'N' AS '00009_EPT_Additional_Information_Structured_Products'
  ,'Mandarine Gestion' AS '00010_Portfolio_Manufacturer_Name'
  ,'Mandarine Gestion' AS '00015_Portfolio_Manufacturer_Group_Name'
  ,NULL AS '00016_Portfolio_Manufacturer_LEI'
  ,NULL AS '00017_Portfolio_Manufacturer_Email'
  ,NULL AS '00020_Portfolio_Guarantor_Name'
  ,RFP.ISIN_Fund AS '00030_Portfolio_Identifying_Data'
  ,1 AS '00040_Type_Of_Identification_Code_For_The_Fund_Share_Or_Portfolio'
  ,RFP.Lib_Fund_Part AS '00050_Portfolio_Name'
  ,RFP.Devise_Part AS '00060_Portfolio_Or_Share_Class_Currency'
  ,'{KID_Date}' AS '00070_PRIIPs_KID_Publication_Date'
  ,NULL AS '00075_PRIIPs_KID_Web_Address'
  ,2 AS '00080_Portfolio_PRIIPS_Category'
  ,RF.cic_code AS '00090_Fund_CIC_code'
  ,'N' AS '00110_Is_An_Autocallable_Product'
  ,'{LANG}' AS '00120_Reference_Language'
  ,NULL AS '01010_Valuation_Frequency'
  ,TB_SRI.vev AS '01020_Portfolio_VEV_Reference'
  ,NULL AS '01030_IS_Flexible'
  ,NULL AS '01040_Flex_VEV_Historical'
  ,NULL AS '01050_Flex_VEV_Ref_Asset_Allocation'
  ,'N' AS '01060_IS_Risk_Limit_Relevant'
  ,NULL AS '01070_Flex_VEV_Risk_Limit'
  ,'N' AS '01080_Existing_Credit_Risk'
  ,TB_SRI.sri AS '01090_SRI'
  ,'N' AS '01095_IS_SRI_Adjusted'
  ,TB_SRI.sri AS '01100_MRM'
  ,TB_SRI.CRM AS '01110_CRM'
  ,TB_SRI.RHP AS'01120_Recommended_Holding_Period'
  ,CASE WHEN RF.Date_Maturite_Fonds IS NULL THEN 'N' ELSE 'Y' END AS '01125_Has_A_Contractual_Maturity_Date'
  ,RF.Date_Maturite_Fonds AS '01130_Maturity_Date'
  ,'L' AS '01140_Liquidity_Risk'
  ,TB_SRI.ReturnValue_UnFav_1 AS '02010_Portfolio_Return_Unfavourable_Scenario_1_Year'
  ,TB_SRI.ReturnValue_UnFav_Hrhp AS '02020_Portfolio_Return_Unfavourable_Scenario_Half_RHP'
  ,TB_SRI.ReturnValue_UnFav_Rhp AS '02030_Portfolio_Return_Unfavourable_Scenario_RHP_Or_First_Call_Date'
  ,'N' AS '02032_Autocall_Applied_Unfavourable_Scenario'
  ,NULL AS '02035_Autocall_Date_Unfavourable_Scenario'
  ,TB_SRI.ReturnValue_Mod_1 AS '02040_Portfolio_Return_Moderate_Scenario_1_Year'
  ,TB_SRI.ReturnValue_Mod_Hrhp AS '02050_Portfolio_Return_Moderate_Scenario_Half_RHP'
  ,TB_SRI.ReturnValue_Mod_Rhp AS '02060_Portfolio_Return_Moderate_Scenario_RHP_Or_First_Call_Date'
  ,'N' AS '02062_Autocall_Applied_Moderate_Scenario'
  ,NULL AS '02065_Autocall_Date_Moderate_Scenario'
  ,TB_SRI.ReturnValue_Fav_1 AS '02070_Portfolio_Return_Favourable_Scenario_1_Year'
  ,TB_SRI.ReturnValue_Fav_Hrhp AS '02080_Portfolio_Return_Favourable_Scenario_Half_RHP'
  ,TB_SRI.ReturnValue_Fav_Rhp AS '02090_Portfolio_Return_Favourable_Scenario_RHP_Or_First_Call_Date'
  ,'N' AS '02092_Autocall_Applied_Favourable_Scenario'
  ,NULL AS '02095_Autocall_Date_Favourable_Scenario'
  ,TB_SRI.ReturnValue_Stress_1 AS '02100_Portfolio_return_stress_scenario_1_year'
  ,TB_SRI.ReturnValue_Stress_Hrhp AS '02110_Portfolio_return_stress_scenario_half_RHP'
  ,TB_SRI.ReturnValue_Stress_Rhp AS '02120_Portfolio_Return_Stress_Scenario_RHP_Or_First_Call_Date'
  ,'N' AS '02122_Autocall_Applied_Stress_Scenario'
  ,NULL AS '02125_Autocall_Date_Stress_Scenario'
  ,TB_SRI.m0 AS '02130_Portfolio_Number_Of_Observed_Return_M0'
  ,TB_SRI.m1 AS '02140_Portfolio_Mean_Observed_Returns_M1'
  ,TB_SRI.volatility AS'02150_Portfolio_Observed_Sigma'
  ,TB_SRI.Skewness AS '02160_Portfolio_Observed_Skewness'
  ,TB_SRI.Kurtosis AS '02170_Portfolio_Observed_Excess_Kurtosis'
  ,TB_SRI.Stressed_Volatility AS '02180_Portfolio_Observed_Stressed_Volatility'
  ,'N' AS '02185_Portfolio_Past_Performance_Disclosure_Required'
  ,NULL AS '02190_Past_Performance_Link'
  ,NULL AS '02200_Previous_Performance_Scenarios_Calculation_Link'
  ,NULL AS '02210_Past_Performance_Number_Of_Years'
  ,10000 AS '02220_Reference_Invested_Amount'
  ,RFP.Tx_Frais_Entree_Max AS '03010_One_off_cost_Portfolio_entry_cost'
  ,0 AS '03015_One_off_cost_Portfolio_entry_cost_Acquired'
  ,RFP.Tx_Frais_Sortie_Max AS '03020_One_off_costs_Portfolio_exit_cost_at_RHP'
  ,RFP.Tx_Frais_Sortie_Max AS '03030_One_off_costs_Portfolio_exit_cost_at_1_year'
  ,RFP.Tx_Frais_Sortie_Max AS '03040_One_off_costs_Portfolio_exit_cost_at_half_RHP'
  ,'N' AS '03050_One_off_costs_Portfolio_sliding_exit_cost_Indicator'
  ,REPT.PTF_OTHER_COSTS_UCITS AS '03060_Ongoing_Costs_Management_Fees_And_Other_Administrative_Or_Operating_Costs'
  ,REPT.PTF_TRANSACTION_COSTS AS '03080_Ongoing_costs_Portfolio_transaction_costs'
  ,CASE WHEN RFP.Perf_Fees IS NULL OR RFP.Perf_Fees = '' OR RFP.Perf_Fees = '-'THEN 'N' ELSE 'Y' END AS '03090_Existing_Incidental_Costs_Portfolio'
  ,CASE WHEN RFP.Perf_Fees IS NULL OR RFP.Perf_Fees = '' OR RFP.Perf_Fees = '-'THEN NULL ELSE REPT.PTF_PERFORMANCE_FEES_UCITS END AS '03095_Incidental_costs'
  ,'N' AS '04020_Comprehension_Alert_Portfolio'
  ,PRIIPS.[04030_Intended_target_market_retail_investor_Portfolio] AS '04030_Intended_target_market_retail_investor_Portfolio'
  ,PRIIPS.[04040_Investment_objective_Portfolio] AS '04040_Investment_objective_Portfolio'
  ,PRIIPS.[04050_Risk_narrative_Portfolio] AS '04050_Risk_narrative_Portfolio'
  ,PRIIPS.[04060_Other_materially_relevant_risk_narrative_Portfolio] AS '04060_Other_materially_relevant_risk_narrative_Portfolio'
  ,RF.[juridique_format] AS '04070_Type_of_underlying_Investment_Option'
  ,'N' AS '04080_Capital_Guarantee'
  ,NULL AS '04081_Capital_Guarantee_Level'
  ,NULL AS '04082_Capital_Guarantee_Limitations'
  ,NULL AS '04083_Capital_Guarantee_Early_Exit_Conditions'
  ,NULL AS '04084_Capital_guarantee_Portfolio'
  ,NULL AS '04085_Possible_maximum_loss_Portfolio'
  ,CONCAT(CONVERT(VARCHAR,TB_SRI.unfavourable_scenario_startdate, 23),'/',CONVERT(VARCHAR,TB_SRI.unfavourable_scenario_enddate, 23)) AS '04086_Description_Past_Interval_Unfavourable_Scenario'
  ,CONCAT(CONVERT(VARCHAR,TB_SRI.moderate_scenario_startdate, 23),'/', CONVERT(VARCHAR,TB_SRI.moderate_scenario_enddate, 23)) AS '04087_Description_Past_Interval_Moderate_Scenario'
  ,CONCAT(CONVERT(VARCHAR,TB_SRI.favourable_scenario_startdate, 23),'/', CONVERT(VARCHAR,TB_SRI.favourable_scenario_enddate, 23)) AS '04088_Description_Past_Interval_Favourable_Scenario'
  ,CASE WHEN RFPB.id_bench IS NULL THEN 'N' ELSE 'Y' END AS '04089_Was_Benchmark_Used_Performance_Calculation'
  ,PRIIPS.[04090_Portfolio_Performance_Fees_Narrative] AS '04090_Portfolio_Performance_Fees_Carried_Interest_Narrative'
  ,NULL AS '04120_One_Off_Cost_Portfolio_Entry_Cost_Description'
  ,PRIIPS.exit_cost_narrative AS '04130_One_Off_Cost_Portfolio_Exit_Cost_Description'
  ,CONCAT(REPT.PTF_OTHER_COSTS_UCITS, PRIIPS.mgmt_cost_description) AS '04140_Ongoing_Costs_Portfolio_Management_Costs_Description'
  ,'N' AS '04150_Do_Costs_Depend_On_Invested_Amount'
  ,NULL AS '04160_Cost_Dependence_Explanation'
  ,'{Last_Month}' AS '06005_German_MOPs_Reference_Date'
  ,0 AS '06010_Bonds_Weight'
  ,TB_SRI.annualized_return_volatility AS '06020_Annualized_Return_Volatility'
  ,0 AS '06030_Duration_Bonds'
  ,'N' AS '06040_Existing_Capital_Preservation'
  ,NULL AS '06050_Capital_Preservation_Level'
  ,NULL AS '06060_Time_Interval_Maximum_Loss'
  ,'N' AS '06070_Uses_PI'
  ,NULL AS '06080_Multiplier_PI'
  ,NULL AS '07005_First_Possible_Call_Date'
  ,NULL AS '07010_Total_Cost_1_Year_Or_First_Call'
  ,NULL AS '07020_RIY_1_Year_Or_First_Call'
  ,NULL AS '07030_Total_Cost_Half_RHP'
  ,NULL AS '07040_RIY_Half_RHP'
  ,NULL AS '07050_Total_Cost_RHP'
  ,NULL AS '07060_RIY_RHP'
  ,NULL AS '07070_One_Off_Costs_Portfolio_Entry_Cost'
  ,NULL AS '07080_One_Off_Costs_Portfolio_Exit_Cost'
  ,NULL AS '07090_Ongoing_Costs_Portfolio_Transaction_Costs'
  ,NULL AS '07100_Ongoing_Costs_Management_Fees_And_Other_Administrative_Or_Operating_Costs'
  ,NULL AS '07110_Incidental_Costs_Portfolio_Performance_Fees_Carried _Interest'
  ,NULL AS '08010_UK_PRIIP_Or_UCITS_Or_Both_data_delivery'
  ,NULL AS '08020_UK_Ongoing_Costs_Portfolio_Transaction_Costs'
  ,NULL AS '08030_UK_Transactions_costs_methodology'
  ,NULL AS '08040_UK_Anti_Dilution_Benefit_Derived'
  ,NULL AS '08045_UK_PRIIPs_Data_Reference_Date'
  ,NULL AS '08050_UK_PRIIPs_KID_Publication_Date'
  ,NULL AS '08060_UK_PRIIPs_KID_Web_Address'
  ,NULL AS '08070_Investment_Objective_Portfolio'
  ,NULL AS '08080_UK_Other_Materially_Relevant_Risk_Narrative_Portfolio'
  ,NULL AS '08090_UK_Performance_Information_Main_Factors'
  ,NULL AS '08100_UK_Performance_Information_Comparator'
  ,NULL AS '08110_UK_Performance_Information_Higher_Returns'
  ,NULL AS '08120_UK_Performance_Information_Lower_Returns_Or_Loss'
  ,NULL AS '08130_UK_Performance_Information_Adverse_Conditions'
  ,NULL AS '08140_UK_Assumed_Portfolio_Return'
  ,NULL AS '08150_UCITS_KIID_Publication_Date'
  ,NULL AS '08160_UCITS_KIID_Web_Address'
  ,NULL AS '08170_UCITS_SRRI'
  ,NULL AS '08180_UCITS_Ongoing_Charges'
  ,NULL AS '08190_UCITS_Existing_Performance_Fees'
  ,NULL AS '08200_UCITS_Performance_Fees'
  FROM Ref_Funds AS RF 
  LEFT JOIN Ref_Funds_Parts AS RFP ON RFP.ref_fund_id = RF.Key_Fund
  LEFT JOIN PART_BENCH_DISTINCT RFPB ON RFP.Key_Fund_Part = RFPB.id_fund_part
  LEFT JOIN (SELECT DISTINCT * FROM tb_mo_priips_narratives WHERE language = 'DEU') AS PRIIPS ON RF.Key_Fund = PRIIPS.Key_Funds
  FULL OUTER JOIN #FILTER_EPT AS REPT ON RFP.Mnemo_Fund_Part = REPT.Mnemo_Fund_Part
  LEFT JOIN (
			  SELECT *
			  FROM [MandarineGestion_Datawarehouse].[dbo].[Tb_rm_CALCULS_JASE_PRIIPS]
			  LEFT JOIN Ref_Funds_Parts AS RFP ON Tb_rm_CALCULS_JASE_PRIIPS.fundid = RFP.ISIN_Fund
			  WHERE MONTH(cobdate)={mois} AND YEAR(cobdate)={annee}
			) AS TB_SRI ON RFP.Key_Fund_Part = TB_SRI.Key_Fund_Part
  WHERE 
    RF.PTF_Reel = 1 
    AND RF.Date_Cloture IS NULL 
    AND RF.Mnemo_Fund NOT IN ('PE-A','PE-O','PE-D') 
    AND RFP.Statut_Part = 'Active' 
    AND RFP.Mnemo_Fund_Part IN {List_Mnemo_Filter} 
    AND RFP.Code_Part <> 'MG'
    AND RFP.ISIN_Fund NOT IN ('ISINXXXXXXXX','LUXXXXXXXXXX','I','ISINXXXXXXXO',
                            'ISINXXXXXXXS','FRXXXXXXXXXX','ISINXXXKSQRF','ISINXXXXXDDL',
                            'ISINXXXXXGGI','ISINXXXXXGGR')
  ORDER BY Key_Fund
"""
    print(Req_SQL)
    cursor = conn.cursor()
    cursor.execute(Req_SQL)
    results = cursor.fetchall()
    results = [list(row) for row in results]
    columns = [column[0] for column in cursor.description]
    cursor.close()
    conn.close()
    df = pd.DataFrame(results, columns=columns)

    for mnemo_fund in pd.unique(List_Mnemo['Mnemo_Fund_Group']):
        print(mnemo_fund)

if LANG == 'DEU':
    Nom_Du_Fichier = f"EPT_V21_{dernier_jour_mois_passe.strftime('%Y%m%d')}_DEU"
elif LANG == 'ENG':
    Nom_Du_Fichier = f"EPT_V21_{dernier_jour_mois_passe.strftime('%Y%m%d')}_ENG"
else:
    Nom_Du_Fichier = f"EPT_V21_{dernier_jour_mois_passe.strftime('%Y%m%d')}"

df.to_excel(f'{chemin_dossier}\\{Nom_Du_Fichier}.xlsx', index=False)
df.to_csv(f'{chemin_dossier}\\{Nom_Du_Fichier}.csv', index=False)

########################################################
#   Prepare Data to Insert In Database
########################################################
isin_list = list(df['00030_Portfolio_Identifying_Data'])
isin_str = "IN ('" + "','".join(isin_list) + "')"

Server = '10.130.1.20'
database = 'MandarineGestion_Datawarehouse'
conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                      f'SERVER={Server};'
                      f'DATABASE={database};'
                      f'Trusted_Connection=yes')

Req_SQL = f"SELECT ISIN_Fund, Mnemo_Fund_Part FROM Ref_Funds_Parts WHERE ISIN_Fund {isin_str}"

cursor = conn.cursor()
cursor.execute(Req_SQL)
results = cursor.fetchall()
results = [list(row) for row in results]
columns = [column[0] for column in cursor.description]
cursor.close()
conn.close()
mnemo_isin = pd.DataFrame(results, columns=columns)

prepared_df = pd.merge(df, mnemo_isin, left_on='00030_Portfolio_Identifying_Data', right_on='ISIN_Fund', how='left')
prepared_df = prepared_df.drop(columns=['ISIN_Fund'])
prepared_df['Tech_Reporting_Date'] = Last_Month

prepared_df['Tech_ID'] = prepared_df['00001_EPT_Version'] + "_" + prepared_df['Mnemo_Fund_Part'] + "_" + prepared_df[
    'Tech_Reporting_Date'] + "_" + prepared_df['00120_Reference_Language']

print(
    '===========================================================================================================================================================')
print(
    '=    End                                                                                                                                                  =')
print(
    '===========================================================================================================================================================')

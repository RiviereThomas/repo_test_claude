from Utils import *
from Input import *

pd.set_option('display.max_rows', None)

# Create And Check Folder
mois = Date_Last_Day_Previous_Month.strftime('%m')
annee = Date_Last_Day_Previous_Month.strftime('%Y')
nom_dossier = f"{annee}-{mois}"
chemin_dossier = os.path.join('\\\\10.130.1.100\\mandarine\\PUBLIC\\MANDARINE SYSTEME DEVELOPPEMENT\\Dev\\5_Reporting\\1_Regulatory_Reports\\3_EMT\\1_Archives\\', nom_dossier)
print('===========================================================================================================================================================')
print('=                                                                                                                                                         =')
print("= Chemin du dossier:                                                                                                                                      =")
print(f"= {chemin_dossier}                           =")
print('=                                                                                                                                                         =')
print('===========================================================================================================================================================')

# Vérifier si le dossier existe déjà, sinon le créer
if not os.path.exists(chemin_dossier):
    os.makedirs(chemin_dossier)

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
'V4.2' AS '00001_EMT_Version'
,NULL AS '00002_EMT_Producer_Name'
,NULL AS '00003_EMT_Producer_LEI'
,NULL AS '00004_EMT_Producer_Email'
,FORMAT( GETDATE() , 'yyyy-MM-dd HH:mm:ss') AS '00005_File_Generation_Date_And_Time'
,'Y' AS '00006_EMT_Data_Reporting_Target_Market'
,'Y' AS '00007_EMT_Data_Reporting_Ex_Ante'
,'Y' AS '00008_EMT_Data_Reporting_Ex_Post'
,RFP.ISIN_Fund AS '00010_Financial_Instrument_Identifying_Data'
,1 AS '00020_Type_Of_Identification_Code_For_The_Financial_Instrument'
,RFP.lib_fund_part_nvarchar AS '00030_Financial_Instrument_Name'
,RFP.Devise_Part AS '00040_Financial_Instrument_Currency'
,CASE WHEN (RFP.Perf_Fees IS NULL OR RFP.Perf_Fees = '' OR RFP.Perf_Fees ='-') THEN 'N' ELSE 'Y' END AS '00045_Financial_Instrument_Performance_Fee'
,CASE WHEN RFP.income_tax = 'Distribution' THEN 'Y' ELSE 'N' END AS '00047_Financial_Instrument_Distribution_Of_Cash'
,'{Date_Last_Working_Day_Previous_Month.strftime('%Y-%m-%d')}' AS '00050_General_Reference_Date'
,'U' AS '00060_Financial_Instrument_Product_Type'
,RF.Date_Maturite_Fonds AS '00065_Maturity_Date'
,NULL AS '00067_May_Be_Terminated_Early'
,'Mandarine Gestion' AS '00070_Financial_Instrument_Manufacturer_Name'
,RF.lei_manco AS '00073_Financial_Instrument_Manufacturer_LEI'
,NULL AS '00074_Financial_Instrument_Manufacturer_Email'
,NULL AS '00075_Financial_Instrument_Manufacturer_Product_Governance_Process'
,NULL AS '00080_Financial_Instrument_Guarantor_Name'
,NULL AS '00085_Financial_Instrument_Type_Notional_Or_Item_Based'
-- ,CASE WHEN TRIM(RF.Type_Fonds) = 'Actions' THEN CONCAT(LEFT(RFP.ISIN_Fund, 2),'41') WHEN TRIM(RF.Type_Fonds) = 'Taux' THEN CONCAT(LEFT(RFP.ISIN_Fund, 2),'42') WHEN TRIM(RF.Type_Fonds) = 'Diversifiés' THEN CONCAT(LEFT(RFP.ISIN_Fund, 2),'44') ELSE CONCAT(LEFT(RFP.ISIN_Fund, 2),'49') END AS '00090_Product_Category_Or_Nature_Germany'
,CASE	WHEN RF.Typologie_fonds = 'OPCVM' OR (RF.Typologie_fonds = 'FIVG' AND RF.Juridique_Format = 'FCP' )  THEN '13' 
		WHEN (RF.Juridique_Format = 'FCP') AND (RF.Typologie_fonds = 'FIA' OR RF.Typologie_fonds = 'FPS' OR RF.Typologie_fonds = 'FPVG') THEN '27' 
		WHEN RF.Juridique_Format = 'FCPR' THEN '3'
		ELSE NULL END AS '00090_Product_Category_Or_Nature_Germany'
,NULL AS '00095_Structured_Securities_Product_Category_Or_Nature'
,NULL AS '00096_Structured_Securities_Quotation'
,'N' AS '00100_Leveraged_Financial_Instrument_Or_Contingent_Liability_Instrument'
,CASE WHEN RFP.Distribution_Fee = 'YES' THEN 'Y' ELSE 'N' END AS '00110_Fund_Share_Class_Without_Retrocession'
,NULL AS '00120_Ex_Post_Cost_Calculation_Basis_Italy'
,'{Date_Last_Working_Day_Previous_Month.strftime('%Y-%m-%d')}' AS '01000_Target_Market_Reference_Date'
,EMT.Investor_Type_Retail AS '01010_Investor_Type_Retail'
,EMT.Investor_Type_Professional AS '01020_Investor_Type_Professional'
,EMT.investor_type_eligible_counterparty AS '01030_Investor_Type_Eligible_Counterparty'
,EMT.basic_investor AS '02010_Basic_Investor'
,EMT.Informed_Investor AS '02020_Informed_Investor'
,EMT.Advanced_Investor AS '02030_Advanced_Investor'
,EMT.Expert_Investor_Germany AS '02040_Expert_Investor_Germany'
,EMT.Compatible_With_Clients_Who_Can_Not_Bear_Capital_Loss AS '03010_Compatible_With_Clients_Who_Can_Not_Bear_Capital_Loss'
,EMT.Compatible_With_Clients_Who_Can_Bear_Limited_Capital_Loss AS '03020_Compatible_With_Clients_Who_Can_Bear_Limited_Capital_Loss'
,EMT.Limited_Capital_Loss_Level AS '03030_Limited_Capital_Loss_Level'
,EMT.Compatible_With_Clients_Who_Do_Not_Need_Capital_Guarantee AS '03040_Compatible_With_Clients_Who_Do_Not_Need_Capital_Guarantee'
,EMT.Compatible_With_Clients_Who_Can_Bear_Loss_Beyond_Capital AS '03050_Compatible_With_Clients_Who_Can_Bear_Loss_Beyond_Capital'
,PRIIPS.sri AS '04010_Risk_Tolerance_PRIIPS_Methodology'
,NULL AS '04020_Risk_Tolerance_UCITS_Methodology'
,NULL AS '04030_Risk_Tolerance_Internal_Methodology_For_Non_PRIIPS_And_Non_UCITS'
,NULL AS '04040_Risk_Tolerance_For_Non_PRIIPS_And_Non_UCITS_Spain'
,NULL AS '04050_Not_For_Investors_With_The_Lowest_Risk_Tolerance_Germany'  -- To see for german funds
,EMT.Return_Profile_Client_Looking_For_Preservation AS '05010_Return_Profile_Client_Looking_For_Preservation'
,EMT.Return_Profile_Client_Looking_For_Capital_Growth AS '05020_Return_Profile_Client_Looking_For_Capital_Growth'
,CASE WHEN RFP.Income_Tax = 'Distribution' THEN 'Y' ELSE 'N' END AS '05030_Return_Profile_Client_Looking_For_Income'
,NULL AS '05040_Return_Profile_Hedging'
,EMT.Option_Or_Leveraged_Return_Profile AS '05050_Option_Or_Leveraged_Return_Profile'
,'N' AS '05070_Return_Profile_Pension_Scheme_Germany'
,PRIIPS.RHP AS '05080_Minimum_Recommended_Holding_Period'
,CASE WHEN (RF.sfdr_cat = 9 OR RF.sfdr_cat = 8) THEN 'Y' ELSE 'Neutral' END AS '05105_Does_This_Financial_Instrument_Consider_End_Client_Sustainability_Preferences'
,'N' AS '05115_Other_Specific_Investment_Need'
,EMT.Distrib_Execution_Only AS '06010_Execution_Only'
,EMT.Distrib_Execution_Appropriateness AS '06020_Execution_With_Appropriateness_Test_Or_Non_Advised_Services'    
,EMT.Distrib_Investment_Advice AS '06030_Investment_Advice'
,EMT.Distrib_Portfolio_Management AS '06040_Portfolio_Management'    
-- Cost & Charges Ex-Ante Section
,CASE WHEN RFP.Tx_Frais_Entree_Max = NULL THEN '0' ELSE RFP.Tx_Frais_Entree_Max END  AS '07020_Gross_One-off_Cost_Financial_Instrument_Maximum_Entry_Cost_Non_Acquired' --
,NULL AS '07025_Net_One-off_Cost_Structured_Products_Entry_Cost_Non_Acquired'
,'0' AS '07030_One-off_Cost_Financial_Instrument_Maximum_Entry_Cost_Fixed_Amount_Italy'
,'0' AS '07040_One-off_Cost_Financial_Instrument_Maximum_Entry_Cost_Acquired'
,CASE WHEN RFP.Tx_Frais_Sortie_Max = NULL THEN '0' ELSE RFP.Tx_Frais_Sortie_Max END AS '07050_One-off_Costs_Financial_Instrument_Maximum_Exit_Cost_Non_Acquired'
,'0' AS '07060_One-off_Costs_Financial_Instrument_Maximum_Exit_Cost_Fixed_Amount_Italy'
,'0' AS '07070_One-off_Costs_Financial_Instrument_Maximum_Exit_Cost_Acquired'
,NULL AS '07080_One-off_Costs_Financial_Instrument_Typical_Exit_Cost'
,NULL AS '07090_One-off_Cost_Financial_Instrument_Exit_Cost_Structured_Products_Prior_RHP'
,RFP.Tx_Frais_de_Gestion_Applique AS '07100_Financial_Instrument_Gross_Ongoing_Costs'
,NULL AS '07105_Financial_Instrument_Borrowing_Costs_Ex_Ante_UK'
,RFP.Tx_Frais_de_Gestion_Applique AS '07110_Financial_Instrument_Management_Fee'
,'0' AS '07120_Financial_Instrument_Distribution_Fee'
,REPT.PTF_TRANSACTION_COSTS AS '07130_Financial_Instrument_Transaction_Costs_Ex_Ante'
,REPT.PTF_PERFORMANCE_FEES_UCITS AS '07140_Financial_Instrument_Incidental_Costs_Ex_Ante'
,NULL AS '07150_Structured_Securities_Reference_Price_Ex_Ante'
,NULL AS '07155_Structured_Securities_Notional_Reference_Amount_Ex_Ante'
,'{Date_Last_Day_Previous_Year_str}' AS '07160_Ex_Ante_Costs_Reference_Date'
-- Cost & Charges Ex-Post Section
,NULL AS '08010_Gross_One-off_Cost_Structured_Securities_Entry_Cost_Ex_Post'
,NULL AS '08015_Net_One-off_Cost_Structured_Securities_Entry_Cost_Ex_Post'
,NULL AS '08020_One-off_Costs_Structured_Securities_Exit_Cost_Ex_Post'
,CASE WHEN RFP.Tx_Frais_Entree_Max_Applique IS NULL THEN '0' ELSE RFP.Tx_Frais_Entree_Max_Applique END  AS '08025_One-off_Cost_Financial_Instrument_Entry_Cost_Acquired'
,CASE WHEN ROUND(REPT.PTF_OTHER_COSTS_UCITS,5) < RFP.Tx_Frais_de_Gestion_Applique THEN RFP.Tx_Frais_de_Gestion_Applique ELSE ROUND(REPT.PTF_OTHER_COSTS_UCITS,5) END AS '08030_Financial_Instrument_Ongoing_Costs_Ex_Post'
,NULL AS '08040_Structured_Securities_Ongoing_Costs_Ex_Post_Accumulated'
,NULL AS '08045_Financial_Instrument_Borrowing_Costs_Ex_Post_UK'
,RFP.Tx_Frais_de_Gestion_Applique AS '08050_Financial_Instrument_Management_Fee_Ex_Post'
,'0' AS '08060_Financial_Instrument_Distribution_Fee_Ex_Post'
,REPT.PTF_TRANSACTION_COSTS AS '08070_Financial_Instrument_Transaction_Costs_Ex_Post'
,REPT.PTF_PERFORMANCE_FEES_UCITS AS '08080_Financial_Instrument_Incidental_Costs_Ex_Post'
,'2018-12-31' AS '08090_Beginning_Of_Reference_Period'
,'{Date_Last_Day_Previous_Year_str}' AS '08100_End_Of_Reference_Period'
,NULL AS '08110_Structured_Securities_Reference_Price_Ex_Post'
,NULL AS '08120_Structured_Securities_Notional_Reference_Amount'
-- Additional information required in UK
,NULL AS '09010_Financial_Instrument_Transaction_Costs_Ex_Ante_UK'
,NULL AS '09020_Financial_Instrument_Transaction_Costs_Ex_Post_UK'
-- Value for Money Mandatory and conditional apply only if 09030 is set to "Y"
,NULL AS '09030_EMT_Data_Reporting_VFM_UK'
,NULL AS '09040_Is_Assessment_Of_Value_Required_Under_COLL_UK'
,NULL AS '09050_Outcome_Of_COLL_Assessment_Of_Value_UK'
,NULL AS '09060_Outcome_Of_PRIN_Value_Assessment_Or_Review_UK'
,NULL AS '09070_Other_Review_Related_To_Value_And_Or_Charges_UK'
,NULL AS '09080_Further_Information_UK'
,NULL AS '09090_Review_Date_UK'
,NULL AS '09100_Review_Next_Due_UK'
-- Additional information required in UK - Optional section 2
,NULL AS '10000_Financial_Instrument_Indirect_Costs_Open_Ended_Ex_Ante_UK'
,NULL AS '10010_Financial_Instrument_Indirect_Costs_Closed_Ended_Ex_Ante_UK'
,NULL AS '10020_Financial_Instrument_Real_Assets_Costs_Ex_Ante_UK'
,NULL AS '10030_Financial_Instrument_Indirect_Costs_Open_Ended_Ex_Post_UK'
,NULL AS '10040_Financial_Instrument_Indirect_Costs_Closed_Ended_Ex_Post_UK'
,NULL AS '10050_Financial_Instrument_Real_Assets_Costs_Ex_Post_UK'
,NULL AS '10060_Does_Financial_Instrument_Produce_Client_Facing_Disclosures_UK'
FROM Ref_funds AS RF
LEFT JOIN Ref_funds_Parts AS RFP ON RF.Key_Fund = RFP.ref_fund_id
LEFT JOIN Tb_MO_DATA_EMT AS EMT ON RFP.Key_Fund_Part = EMT.Key_Parts
LEFT JOIN (SELECT * FROM Tb_rm_CALCULS_JASE_PRIIPS WHERE MONTH(cobdate)={mois} AND YEAR(cobdate)={annee}) AS PRIIPS ON PRIIPS.fundid = RFP.ISIN_Fund 
LEFT JOIN #FILTER_EPT AS REPT ON RFP.Mnemo_Fund_Part = REPT.Mnemo_Fund_Part
WHERE RF.PTF_Reel = 1 AND RF.Date_Cloture IS NULL AND RFP.ISIN_Fund NOT IN ('I','ISINXXXXXXXX','LUXXXXXXXXXX','FR0012217057','FR0013204088','XFCS00X2FYJ2','DK0061668068','DK0000211178','FR0014004GZ0','LU2052475139','FR0013518404','FR0007016811','FR0010077917','FR0014002U04','FR001400SVU5') AND Code_Part <> 'MG'
"""
print (Req_SQL)
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

df = pd.DataFrame(results, columns=columns)
Nom_Du_Fichier = f"EMT_V4_2_{Date_Last_Working_Day_Previous_Month.strftime('%Y%m%d')}"

df.to_excel(f'{chemin_dossier}\\{Nom_Du_Fichier}.xlsx', index=False)
df.to_csv(f'{chemin_dossier}\\{Nom_Du_Fichier}.csv', index=False)

print('===========================================================================================================================================================')
print('=    End                                                                                                                                                  =')
print('===========================================================================================================================================================')
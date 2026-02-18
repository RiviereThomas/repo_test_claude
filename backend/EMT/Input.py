
from datetime import datetime, timedelta
import pandas as pd


Date_Now = datetime.now()
Date_Now = datetime(2025, 4, 10, 0, 0, 0)

Date_Now_str = Date_Now.strftime('%Y-%m-%d')

Date_Last_Day_Previous_Month = Date_Now.replace(day=1) - timedelta(days=1)
Date_Last_Day_Previous_Month_str =  Date_Last_Day_Previous_Month.strftime('%Y-%m-%d')

Date_Last_Working_Day_Previous_Month = pd.date_range(end=Date_Last_Day_Previous_Month, periods=1, freq='B').date[0]
Date_Last_Working_Day_Previous_Month_str =  Date_Last_Working_Day_Previous_Month.strftime('%Y-%m-%d')

Date_Last_Day_Previous_Year = Date_Now.replace(month=1).replace(day=1) - timedelta(days=1)
Date_Last_Day_Previous_Year_str =  Date_Last_Day_Previous_Year.strftime('%Y-%m-%d')

Date_Last_Working_Day_Previous_Year = pd.date_range(end=Date_Last_Day_Previous_Year, periods=1, freq='B').date[0]
Date_Last_Working_Day_Previous_Year_str =  Date_Last_Working_Day_Previous_Year.strftime('%Y-%m-%d')


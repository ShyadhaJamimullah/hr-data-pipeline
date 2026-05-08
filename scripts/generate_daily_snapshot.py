import pandas as pd
import random
from datetime import datetime
import os
import sys

def generate_daily_snapshot(snapshot_date):

    snapshot_date = datetime.strptime(snapshot_date, "%Y-%m-%d").date()

    master_path="/opt/airflow/data/employee_master.csv"

    if not os.path.exists(master_path):
        raise FileNotFoundError("Employee master file not found")
    
    master_df=pd.read_csv(master_path)

    snapshot_data=[]

    for _, row in master_df.iterrows():

        salary=row["BaseSalary"]
        if random.random()<0.05:
            salary+=random.randint(1000,5000)

        relieved="Yes" if random.random()<0.05 else "No"

        snapshot_data.append({
            "EmployeeID":row["EmployeeID"],
            "EmployeeName":row["EmployeeName"],
            "Gender":row["Gender"],
            "DOB":row["DOB"],
            "Department":row["Department"],
            "JobRole":row["JobRole"],
            "HireDate":row["HireDate"],
            "MonthlyIncome":salary,                
            "Overtime":random.choice(["Yes","No"]),
            "JobSatisfaction":random.randint(1,4),
            "PerformanceRating":random.randint(1,5),
            "Relieved":relieved,
            "SnapshotDate":snapshot_date
        })

    snapshot_df=pd.DataFrame(snapshot_data)

    data_folder="/opt/airflow/data"

    
    file_name=f"snapshot_{snapshot_date.strftime('%Y%m%d')}.csv"


    file_path=os.path.join(data_folder,file_name)

    snapshot_df.to_csv(file_path, index=False)

    print(f"Daily snapshot created: {file_path}")



if __name__=="__main__":

    snapshot_date=sys.argv[1]

    generate_daily_snapshot(snapshot_date)

from faker import Faker
import pandas as pd
import random
import os

fake=Faker('en_IN')

def create_employee_master(num_records=500):
    employees=[]

    for emp_id in range(1000,1000+num_records):
        hire_date=fake.date_between(start_date='-10y',end_date='-1y').strftime("%Y-%m-%d")
        dob = fake.date_of_birth(minimum_age=22, maximum_age=60).strftime("%Y-%m-%d")

        employees.append({"EmployeeID":emp_id,
                     "EmployeeName":fake.name(),
                     "Gender":random.choice(["Male","Female"]),
                     "DOB":dob,
                     "Department":random.choice(["HR","IT","Finance","Sales"]),
                     "JobRole":random.choice(["Manager","Executive","Analyst"]),
                     "HireDate":hire_date,
                     "BaseSalary":random.randint(30000,100000)})
                   
    df=pd.DataFrame(employees)

    data_folder="/opt/airflow/data"

    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
        print(f"Created folder {data_folder}")

    file_path= os.path.join(data_folder,f"employee_master.csv")

    df.to_csv(file_path,index=False)

    print(f"File Generated: {file_path}")

create_employee_master()


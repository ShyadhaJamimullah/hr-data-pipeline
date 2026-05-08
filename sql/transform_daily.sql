insert ignore into dim_employee(EmployeeID,EmployeeName,Gender,DOB,HireDate,JobRole)
select distinct EmployeeID,EmployeeName,Gender,DOB,HireDate,JobRole 
from hr_transactions_staging;

insert ignore into dim_department(DepartmentName)
select distinct Department
from hr_transactions_staging;

insert ignore into dim_date(DateValue,Year,Month,Day,MonthName,Quarter)
select distinct 
    SnapshotDate,
    Year(SnapshotDate),
    Month(SnapshotDate),
    Day(SnapshotDate),
    MonthName(SnapshotDate),
    Quarter(SnapshotDate)
from hr_transactions_staging;

insert ignore into fact_hr_daily(
    EmployeeID,
    EmployeeName,
    SnapshotDate,
    DepartmentID,
    MonthlyIncome,
    IncomeBand,
    YearsInCompany,
    TenureBand,
    Overtime,
    JobSatisfaction,
    PerformanceRating,
    RelievedFlag
)
select 
    t.EmployeeID,
    t.EmployeeName,
    t.SnapshotDate,
    d.DepartmentID,
    t.MonthlyIncome,

    case
        when t.MonthlyIncome<40000 then 'Low'
        when t.MonthlyIncome<60000 then 'Medium'
        when t.MonthlyIncome<90000 then 'High'
        else 'Very High'
    end as IncomeBand,

    timestampdiff(Year,e.HireDate,t.SnapshotDate) as YearsInCompany,
    case
        when timestampdiff(Year,e.HireDate,t.SnapshotDate)<=2 then '0-2 Yrs'
        when timestampdiff(Year,e.HireDate,t.SnapshotDate)<=5 then '3-5 Yrs'
        when timestampdiff(Year,e.HireDate,t.SnapshotDate)<=10 then '6-10 Yrs'
        else '10+ Yrs'
    end as TenureBand,

    t.Overtime,
    t.JobSatisfaction,
    t.PerformanceRating,

    case
        when t.Relieved='Yes' then 1
        else 0
    end as RelievedFlag

from hr_transactions_staging t
join dim_department d on t.Department=d.DepartmentName
join dim_employee e on t.EmployeeID=e.EmployeeID;


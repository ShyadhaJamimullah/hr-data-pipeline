insert ignore into fact_hr_monthly(
    Year,
    Month,
    DepartmentID,
    TotalEmployees,
    AvgSalary,
    AttritionCount,
    AttritionRate,
    OvertimeRate,
    AvgTenure
)
select 
    dd.Year,
    dd.Month,
    f.DepartmentID,
    
    count(distinct f.EmployeeID) as TotalEmployees,

    avg(f.MonthlyIncome) as AvgSalary,


    sum(f.RelievedFlag) as AttritionCount,

    round(sum(f.RelievedFlag)/count(distinct f.EmployeeID),2) as AttritionRate,

    round(
        avg(case when f.Overtime='Yes' then 1 else 0 end),
        2
    ) as OvertimeRate,

    round(avg(f.YearsInCompany),2) as AvgTenure

from fact_hr_daily f
join dim_date dd on f.SnapshotDate=dd.DateValue

group by
    dd.Year,
    dd.Month,
    f.DepartmentID;
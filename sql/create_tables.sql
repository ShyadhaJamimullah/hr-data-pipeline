-- raw table
create table if not exists hr_transactions_raw
(
    EmployeeID int,
    EmployeeName varchar(50),
    Gender varchar(20),
    DOB date,
    Department varchar(50),
    JobRole varchar(50),
    HireDate date,
    MonthlyIncome int,
    Overtime varchar(10),
    JobSatisfaction int,
    PerformanceRating int,
    Relieved varchar(10),
    SnapshotDate date
);

-- DROP INDEX IF EXISTS idx_snapshotdate ON hr_transactions_raw;
-- CREATE INDEX idx_snapshotdate ON hr_transactions_raw(SnapshotDate);

-- staging table
create table if not exists hr_transactions_staging
(
    EmployeeID int,
    EmployeeName varchar(50),
    Gender varchar(20),
    DOB date,
    Department varchar(50),
    JobRole varchar(50),
    HireDate date,
    MonthlyIncome int,
    Overtime varchar(10),
    JobSatisfaction int,
    PerformanceRating int,
    Relieved varchar(10),
    SnapshotDate date
);

-- dimension tables
-- dimension employee
create table if not exists dim_employee
(
    EmployeeID int primary key,
    EmployeeName varchar(50),
    Gender varchar(20),
    DOB date,
    JobRole varchar(50),
    HireDate date
);

-- dimension department
create table if not exists dim_department
(
    DepartmentID int auto_increment primary key,
    DepartmentName varchar(50) unique
);

-- dimension date
create table if not exists dim_date
(
    DateValue date primary key,
    Year int,
    Month int,
    Day int,
    MonthName varchar(50),
    Quarter int  
);

-- fact tables
create table if not exists fact_hr_daily
(
    EmployeeID int,
    EmployeeName varchar(50),
    SnapshotDate date,
    DepartmentID int,
    MonthlyIncome int,
    IncomeBand varchar(10),
    YearsInCompany int,
    TenureBand varchar(10),
    Overtime varchar(10),
    JobSatisfaction int,
    PerformanceRating int,
    RelievedFlag tinyint,
    primary key (EmployeeID,SnapshotDate),
    foreign key (EmployeeID) references dim_employee(EmployeeID),
    foreign key (DepartmentID) references dim_department(DepartmentID),
    foreign key (SnapshotDate) references dim_date(DateValue)
);

create table if not exists fact_hr_monthly
(
    Year int,
    Month int,
    DepartmentID int,
    TotalEmployees int,
    AvgSalary decimal(10,2),
    AttritionCount int,
    AttritionRate decimal(10,2),
    OvertimeRate decimal(10,2),
    AvgTenure decimal(10,2),
    primary key (Year,Month,DepartmentID),
    foreign key (DepartmentID) references dim_department(DepartmentID)
);




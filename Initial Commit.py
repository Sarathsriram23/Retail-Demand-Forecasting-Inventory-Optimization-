import pandas as pd
#Read datasets
calendar = pd.read_csv('calendar.csv')
prices = pd.read_csv('sell_prices.csv')
sales = pd.read_csv('sales_train_validation.csv')
print(calendar.head())
print(prices.head())
print(sales.head())
#Explore data
print("Calendar Dataset")
print(calendar.head())
print(calendar.info())
print(calendar.isnull().sum())

print("Prices Dataset")
print(prices.head())
print(prices.info())
print(prices.isnull().sum())

print("Sales Dataset")
print(sales.head())
print(sales.info())
print(sales.isnull().sum())

#Identify Missing Values
print("Missing Values in Calendar Dataset:")
print(calendar.isnull().sum())
print("Missing Values in Prices Dataset:")
print(prices.isnull().sum())
print("Missing Values in Sales Dataset:")
print(sales.isnull().sum())

#Check the size of the datasets
print("\nDataset Shapes:")
print("Calendar:",calendar.shape)
print("Prices:",prices.shape)
print("Sales:",sales.shape)

#Display dataset information
print("\nCalendar Dataset Info:")
print(calendar.info())
print("\nPrices Dataset Info:")
print(prices.info())
print("\nSales Dataset Info:")
print(sales.info())

#Check for duplicates in the datasets
print("\nDuplicate Rows in Calendar Dataset:", calendar.duplicated().sum())
print("Duplicate Rows in Prices Dataset:", prices.duplicated().sum())   
print("Duplicate Rows in Sales Dataset:", sales.duplicated().sum())   

#Display column names of the datasets
print("\nCalendar Dataset Columns:", calendar.columns)
print("Prices Dataset Columns:", prices.columns)
print("Sales Dataset Columns:", sales.columns)

#Display data types of the datasets
print("\nCalendar Dataset Data Types:\n", calendar.dtypes)
print("\nPrices Dataset Data Types:\n", prices.dtypes)
print("\nSales Dataset Data Types:\n", sales.dtypes)    

#Summary statistics
print(prices.describe())
print(sales.describe())

#Convert date column
calendar['date'] = pd.to_datetime(calendar['date'])
print(calendar['date'].head())

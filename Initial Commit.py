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


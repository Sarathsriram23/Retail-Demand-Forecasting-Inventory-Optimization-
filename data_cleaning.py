import pandas as pd

calendar = pd.read_csv('calendar.csv')
prices = pd.read_csv('sell_prices.csv')
sales = pd.read_csv('sales_train_validation.csv')

print(calendar.head())
print(prices.head())
print(sales.head())

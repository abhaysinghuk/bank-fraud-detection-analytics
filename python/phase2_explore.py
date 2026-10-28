import pandas as pd

df = pd.read_csv('bank_transactions_data_2.csv')

print('SHAPE (rows, columns):', df.shape)
print()
print('DATA TYPES:')
print(df.dtypes)
print()
print('MISSING VALUES PER COLUMN:')
print(df.isnull().sum())
print()
print('DUPLICATE ROWS:', df.duplicated().sum())
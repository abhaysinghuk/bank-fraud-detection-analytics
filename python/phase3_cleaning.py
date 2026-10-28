import pandas as pd

df = pd.read_csv('bank_transactions_data_2.csv')

# Convert text columns into real datetime objects
df['TransactionDate'] = pd.to_datetime(df['TransactionDate'])
df['PreviousTransactionDate'] = pd.to_datetime(df['PreviousTransactionDate'])

# Extract the hour of day from each transaction
df['TransactionHour'] = df['TransactionDate'].dt.hour

# Extract day of week too
df['TransactionDayOfWeek'] = df['TransactionDate'].dt.day_name()

print('SAMPLE OF NEW COLUMNS:')
print(df[['TransactionDate', 'TransactionHour', 'TransactionDayOfWeek']].head())

# ---- NEW CODE BELOW ----

# Z-score method
mean_amt = df['TransactionAmount'].mean()
std_amt = df['TransactionAmount'].std()
df['Amount_ZScore'] = (df['TransactionAmount'] - mean_amt) / std_amt

# IQR method
Q1 = df['TransactionAmount'].quantile(0.25)
Q3 = df['TransactionAmount'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

print('Mean amount:', round(mean_amt, 2))
print('Std deviation:', round(std_amt, 2))
print('Q1:', Q1, '| Q3:', Q3, '| IQR:', IQR)
print('IQR outlier bounds: below', round(lower_bound,2), 'or above', round(upper_bound,2))

# Flag outliers using IQR
df['Is_Amount_Outlier_IQR'] = (df['TransactionAmount'] < lower_bound) | (df['TransactionAmount'] > upper_bound)
print()
print('Number of outlier transactions (IQR method):', df['Is_Amount_Outlier_IQR'].sum())
print()
print('Sample outlier transactions:')
print(df[df['Is_Amount_Outlier_IQR']][['TransactionID','TransactionAmount','TransactionHour']].head(10))


# ---- LoginAttempts outliers ----
Q1_login = df['LoginAttempts'].quantile(0.25)
Q3_login = df['LoginAttempts'].quantile(0.75)
IQR_login = Q3_login - Q1_login
lower_login = Q1_login - 1.5 * IQR_login
upper_login = Q3_login + 1.5 * IQR_login
df['Is_Login_Outlier_IQR'] = (df['LoginAttempts'] < lower_login) | (df['LoginAttempts'] > upper_login)

print('LoginAttempts outlier bounds: below', lower_login, 'or above', upper_login)
print('Number of LoginAttempts outliers:', df['Is_Login_Outlier_IQR'].sum())

# ---- TransactionDuration outliers ----
Q1_dur = df['TransactionDuration'].quantile(0.25)
Q3_dur = df['TransactionDuration'].quantile(0.75)
IQR_dur = Q3_dur - Q1_dur
lower_dur = Q1_dur - 1.5 * IQR_dur
upper_dur = Q3_dur + 1.5 * IQR_dur
df['Is_Duration_Outlier_IQR'] = (df['TransactionDuration'] < lower_dur) | (df['TransactionDuration'] > upper_dur)

print('TransactionDuration outlier bounds: below', lower_dur, 'or above', upper_dur)
print('Number of TransactionDuration outliers:', df['Is_Duration_Outlier_IQR'].sum())

# ---- Combine all signals into one Fraud Risk Score ----
# Each True/False outlier flag is treated as 1/0 and summed up.
df['Fraud_Risk_Score'] = (
    df['Is_Amount_Outlier_IQR'].astype(int) +
    df['Is_Login_Outlier_IQR'].astype(int) +
    df['Is_Duration_Outlier_IQR'].astype(int)
)

print()
print('Fraud Risk Score distribution:')
print(df['Fraud_Risk_Score'].value_counts().sort_index())

print()
print('Top 10 highest-risk transactions:')
print(df.sort_values('Fraud_Risk_Score', ascending=False)
        [['TransactionID','TransactionAmount','LoginAttempts','TransactionDuration','Fraud_Risk_Score']]
        .head(10))

# ---- Save the cleaned + scored dataset for use in later phases ----
df.to_csv('fraud_data_cleaned.csv', index=False)
print()
print('Saved cleaned dataset as fraud_data_cleaned.csv')
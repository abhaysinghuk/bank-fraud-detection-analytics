import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('fraud_data_cleaned.csv')

# Create a simple flag: is this transaction "suspicious" at all (score >= 1)?
df['Is_Suspicious'] = df['Fraud_Risk_Score'] >= 1

# ---- Question 1: Which cities have the most suspicious transactions? ----
city_risk = df.groupby('Location')['Is_Suspicious'].sum().sort_values(ascending=False)
print('Suspicious transactions by city (top 10):')
print(city_risk.head(10))

# ---- Question 2: Which hour of day has the most suspicious transactions? ----
hour_risk = df.groupby('TransactionHour')['Is_Suspicious'].sum().sort_values(ascending=False)
print()
print('Suspicious transactions by hour:')
print(hour_risk)

# ---- Question 3: Which customer occupation is most targeted? ----
occupation_risk = df.groupby('CustomerOccupation')['Is_Suspicious'].sum().sort_values(ascending=False)
print()
print('Suspicious transactions by occupation:')
print(occupation_risk)

# ---- Question 4: Which channel (ATM/Online/Branch) is riskiest? ----
channel_risk = df.groupby('Channel')['Is_Suspicious'].sum().sort_values(ascending=False)
print()
print('Suspicious transactions by channel:')
print(channel_risk)

# ---- Your first chart: suspicious transactions by hour ----
plt.figure(figsize=(10,5))
hour_risk.sort_index().plot(kind='bar', color='indianred')
plt.title('Suspicious Transactions by Hour of Day')
plt.xlabel('Hour of Day')
plt.ylabel('Number of Suspicious Transactions')
plt.tight_layout()
plt.savefig('chart_suspicious_by_hour.png')
print()
print('Chart saved as chart_suspicious_by_hour.png')


# ---- Corrected analysis: suspicious RATE, not raw count ----

hour_total = df.groupby('TransactionHour').size()
hour_suspicious = df.groupby('TransactionHour')['Is_Suspicious'].sum()
hour_rate = (hour_suspicious / hour_total * 100).round(2)

print('Total transactions per hour:')
print(hour_total)
print()
print('Suspicious RATE (%) by hour:')
print(hour_rate.sort_values(ascending=False))

city_total = df.groupby('Location').size()
city_suspicious = df.groupby('Location')['Is_Suspicious'].sum()
city_rate = (city_suspicious / city_total * 100).round(2)
print()
print('Suspicious RATE (%) by city (top 10):')
print(city_rate.sort_values(ascending=False).head(10))



plt.figure(figsize=(10,5))
city_rate.sort_values(ascending=False).head(10).plot(kind='bar', color='steelblue')
plt.title('Top 10 Cities by Suspicious Transaction Rate (%)')
plt.xlabel('City')
plt.ylabel('Suspicious Rate (%)')
plt.tight_layout()
plt.savefig('chart_suspicious_rate_by_city.png')
print('Chart saved as chart_suspicious_rate_by_city.png')
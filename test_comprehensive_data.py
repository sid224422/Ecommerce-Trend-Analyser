"""Verify comprehensive test data"""
import pandas as pd

df = pd.read_csv('test_data_comprehensive.csv')

print("="*60)
print("Comprehensive Test Data Verification")
print("="*60)
print(f"\nTotal rows: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(f"\nUnique brands: {df['brand'].nunique()}")
print(f"Brands: {sorted(df['brand'].unique())}")
print(f"\nPrice range: ${df['price'].min():.2f} - ${df['price'].max():.2f}")
print(f"Mean price: ${df['price'].mean():.2f}")
print(f"Median price: ${df['price'].median():.2f}")

# Count features
all_features = []
for features_str in df['feature'].dropna():
    if isinstance(features_str, str):
        features = features_str.replace(';', ',').replace('|', ',').split(',')
        all_features.extend([f.strip().lower() for f in features if f.strip()])

feature_counts = pd.Series(all_features).value_counts()
print(f"\nUnique features: {len(feature_counts)}")
print(f"Top 10 features:\n{feature_counts.head(10)}")

print("\n" + "="*60)
print("Data ready for comprehensive testing!")


import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Read files
df1 = pd.read_csv('CCIB_members.csv', encoding='ISO-8859-1')
df2 = pd.read_csv('contracts-2023.csv', encoding='ISO-8859-1', on_bad_lines='skip')
df3 = pd.read_csv('indigenous_business_directory.csv', encoding='ISO-8859-1')

# Step 2: Mark PSIB status
df2['PSIB_Status'] = df2.apply(
    lambda row: 'PSIB' if (
        row['indigenous_business_en'] in ['2. Mandatory Set-Aside', '3. Voluntary Set-Aside'] 
        or row['indigenous_business_excluding_psib_en'] == 'Yes'
    ) else 'NON-PSIB', 
    axis=1
)

# Step 3: PSIB vs NON-PSIB distribution (Pie chart)
# Calculate the count of contracts for PSIB and NON-PSIB
psib_counts = df2['PSIB_Status'].value_counts()

# Calculate the total contract value for PSIB and NON-PSIB
psib_contract_value = df2.groupby('PSIB_Status')['contract_value'].sum()

# Create subplots for both pie charts
fig, axs = plt.subplots(1, 2, figsize=(12, 6))  # 1 row, 2 columns

# Plot 1: Contract Count Distribution (Pie chart)
psib_counts.plot(kind='pie', autopct='%1.1f%%', startangle=90, ax=axs[0])
axs[0].set_title('PSIB vs NON-PSIB Contract Count Distribution')
axs[0].set_ylabel('')  # Remove the y-label for the pie chart

# Plot 2: Contract Value Distribution (Pie chart)
psib_contract_value.plot(kind='pie', autopct='%1.1f%%', startangle=90, ax=axs[1])
axs[1].set_title('PSIB vs NON-PSIB Contract Value Distribution')
axs[1].set_ylabel('')  # Remove the y-label for the pie chart

# Adjust layout to prevent overlap
plt.tight_layout()

# Display the plots
plt.show()

# Step 4: Mark IB Status
# Helper function to clean company names (ignore case and remove extra spaces)
def clean_name(name):
    if pd.isna(name):
        return ""
    return name.strip().lower()

# Clean company names in relevant columns
df1['clean_company_name'] = df1['Company Name'].apply(clean_name)  # CCIB_members.csv
df2['clean_vendor_name'] = df2['vendor_name'].apply(clean_name)    # contracts-2023.csv
df3['clean_legal_name'] = df3['Company Legal Name'].apply(clean_name)  # indigenous_business_directory.csv

# Create a set of all clean company names from CCIB and Indigenous directories (only using Company Name and Legal Name)
ib_company_names = set(df1['clean_company_name']).union(set(df3['clean_legal_name']))

# Mark contracts that match these names as 'IB'
df2['IB_Status'] = df2['clean_vendor_name'].apply(lambda name: 'IB' if name in ib_company_names else 'NON-IB')

# Step 5: Count the number of IB and NON-IB contracts
ib_counts = df2['IB_Status'].value_counts()

# Print the result
print("IB and NON-IB counts in the main table:")
print(ib_counts)

# Step 5: PSIB vs IB detailed distribution under PSIB
# Calculate the count of IB and NON-IB contracts under PSIB
psib_ib_counts = df2.groupby(['PSIB_Status', 'IB_Status']).size().unstack()
psib_ib = psib_ib_counts.loc['PSIB']

#  Calculate the total contract value for IB and NON-IB under PSIB
psib_ib_value = df2[df2['PSIB_Status'] == 'PSIB'].groupby('IB_Status')['contract_value'].sum()

#  Create subplots for both pie charts
fig, axs = plt.subplots(1, 2, figsize=(12, 6))  # 1 row, 2 columns

# Plot 1: Contract Count Distribution (Pie chart for IB vs NON-IB under PSIB)
psib_ib.plot(kind='pie', autopct='%1.1f%%', startangle=90, ax=axs[0])
axs[0].set_title('IB vs NON-IB Contract Count under PSIB')
axs[0].set_ylabel('')  # Remove the y-label for the pie chart

# Plot 2: Contract Value Distribution (Pie chart for IB vs NON-IB under PSIB)
psib_ib_value.plot(kind='pie', autopct='%1.1f%%', startangle=90, ax=axs[1])
axs[1].set_title('IB vs NON-IB Contract Value under PSIB')
axs[1].set_ylabel('')  # Remove the y-label for the pie chart

# Adjust layout to prevent overlap
plt.tight_layout()

# Display the plots
plt.show()


# Step 6: Filter out contracts with contract_value less than 1000
df2_cleaned = df2[df2['contract_value'] >= 1000]

# Define a keyword dictionary for contract classification
categories_keywords = {
    'Technology': ['software', 'information technology', 'hardware', 'network', 'AI', 'data analysis'],
    'Goods': ['office supplies', 'furniture', 'equipment', 'stationery', 'food'],
    'Construction': ['construction', 'building', 'road', 'bridge', 'infrastructure'],
    'Services': ['training', 'consulting', 'audit', 'repair', 'advertising', 'cleaning'],
}

# Step 7: Classify contracts based on description_eng
def classify_description(description):
    description = str(description).lower()  
    for category, keywords in categories_keywords.items():
        for keyword in keywords:
            if keyword.lower() in description:
                return category
    return 'Other'  

df2_cleaned['Category'] = df2_cleaned['description_eng'].apply(classify_description)

# View the classification result
print(df2_cleaned[['description_eng', 'Category']].head())

# Step 8: Contract category distribution (Bar chart)
category_counts = df2_cleaned['Category'].value_counts()
category_counts.plot(kind='bar')
plt.title('Contract Categories Distribution')
plt.xlabel('Category')
plt.ylabel('Number of Contracts')
plt.show()

# Step 9: Plot contract value proportion for PSIB and NON-PSIB
def plot_contract_value_proportion(psib_status):
    grouped = df2_cleaned[df2_cleaned['PSIB_Status'] == psib_status].groupby(['IB_Status', 'Category'])['contract_value'].sum().unstack()
    grouped.plot(kind='bar', stacked=True)
    plt.title(f'Contract Value Proportion for {psib_status} - IB vs NON-IB')
    plt.xlabel('IB Status')
    plt.ylabel('Total Contract Value')
    plt.show()

# Plot for PSIB contracts
plot_contract_value_proportion('PSIB')

# Plot for NON-PSIB contracts
plot_contract_value_proportion('NON-PSIB')

# Step 10: Top 20 vendors in Technology under PSIB and NON-IB
# 1: Filter out all contracts that are in PSIB, Technology, and NON-IB
filtered_contracts = df2_cleaned[ 
    (df2_cleaned['PSIB_Status'] == 'PSIB') & 
    (df2_cleaned['IB_Status'] == 'NON-IB') & 
    (df2_cleaned['Category'] == 'Technology')
]

# 2: Group by 'vendor_name' and sum the contract values for each vendor
aggregated_contracts = filtered_contracts.groupby('vendor_name')['contract_value'].sum().reset_index()

# Step 3: Find the top 20 vendors by contract value
top_technology_vendors = aggregated_contracts.nlargest(20, 'contract_value')

# Step 4: Display the top 20 vendors
print(top_technology_vendors[['vendor_name', 'contract_value']])

# Step 5: Plot the top 20 vendors and their contract values
top_technology_vendors.plot(kind='barh', x='vendor_name', y='contract_value', legend=False)
plt.title('Top 20 NON-IB Vendors in Technology under PSIB')
plt.xlabel('Contract Value')
plt.ylabel('Vendor Name')
plt.tight_layout()
plt.show()


# Step 11: Divide by contract value ranges
bins = [0, 10000, 25000, 100000, 1000000, 5000000, float('inf')]
labels = ['Less than $10,000', '$10,000 - $25,000', '$25,000 - $100,000', 
          '$100,000 - $1,000,000', '$1,000,000 - $5,000,000', 'More than $5,000,000']

df2['Contract Value Range'] = pd.cut(df2['contract_value'], bins=bins, labels=labels, right=False)

# Check the result
print(df2[['contract_value', 'Contract Value Range']].head())

# Step 12: Contract value distribution by range (Bar chart)
value_range_counts = df2['Contract Value Range'].value_counts(sort=False)
value_range_counts.plot(kind='bar', color='skyblue')
plt.title('Contract Value Distribution by Range')
plt.xlabel('Contract Value Range')
plt.ylabel('Number of Contracts')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

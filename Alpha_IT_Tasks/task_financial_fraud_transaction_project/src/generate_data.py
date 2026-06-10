# This script contains two sections - the first section is the reusable code which is the function to generate synthetic data for fraud detection and the second section is the executable code which will run when we execute this script and it will call the function to generate data and save it as a CSV file.

# 1. Reusable code
import pandas as pd
import numpy as np

# Generate data generateion function which will generate the synthetic data 
def generate_data(n_samples = 10000, fraud_ratio =0.02, seed = 42):
    """
    Generate synthetic fraud detection dataset.
    
    Args:
        n_samples: Total number of transactions to generate
        fraud_ratio: Proportion of fraudulent transactions (default 2%)
        seed: Random seed for reproducibility
    
    Returns:
        DataFrame with transaction features and fraud labels
    
    Fraud transactions have different patterns:
    - Higher amounts (mean \(245 vs \)33 for legit)
    - Late night hours (0-5, 23)
    - More likely to be online or travel merchants
    """
    np.random.seed(seed)  # this will generate same random numbers everytime 
    n_fraud = int(n_samples * fraud_ratio)  # this will give us the number of fraudulent transactions same as real word data many small transactions and few extremely large transactions
    n_legit = n_samples - n_fraud  # this will give us the number of legitimate transactions
    
    # Legitimate transactions: normal shopping patterns
    # - Amounts follow a log-normal distribution (most small, some large)
    # - Hours are uniformly distributed throughout the day
    # - Merchant categories weighted toward everyday shopping
    
    legit = {
        'amount' : np.random.lognormal(mean =3.5, sigma=1.2, size= n_legit),  # $245 average with some large outliers
        'hour' : np.random.randint(0,24,size= n_legit),  # it will generate random hours between 0 and 23 uniformly
        'day_of_week' : np.random.randint(0,7, size= n_legit), # this will generate random days of the week uniformly
        'merchant_category' : np.random.choice(['grocery', 'electronics', 'clothing', 'restaurant', 'travel'], size= n_legit,p=[0.30, 0.25, 0.25, 0.15,0.05]), # this is weighted towards everyday shopping shows percentage of transactions in each category
        'is_fraud' : 0
    }
    
    # Fraudulent transactions: suspicious patterns
    # - Higher amounts (fraudsters go big)
    # - Late night hours (less scrutiny)
    # - More online and travel (easier to exploit)
    fraud ={
        'amount' : np.random.lognormal(mean =5.5, sigma=1.5, size= n_fraud),  # $33 average with many large outliers
        'hour' : np.random.choice([0,1,2,3,4,5,23],size= n_fraud),  # it will generate random hours between 0 and 23 uniformly
        'day_of_week' : np.random.randint(0,7, size= n_fraud), # this will generate random days of the week uniformly
        'merchant_category' : np.random.choice(['grocery', 'electronics', 'clothing', 'restaurant', 'travel'], size= n_fraud,p=[0.10, 0.15, 0.15, 0.30,0.30]), # this is weighted towards high-risk categories
        'is_fraud' : 1
    }
    
    # Create dataframes
    legit_data = pd.DataFrame(legit)
    fraud_data = pd.DataFrame(fraud)
    
    # Combine and shuffle
    data = pd.concat([legit_data, fraud_data]).sample(frac =1 , random_state = seed).reset_index(drop = True) # this will combine the two dataframes and shuffle them randomly and reset the index
    
    return data


# 2. Executable code
# Now this below part is executable code and above part is reusable code which can be imported in other scripts and used to generate data whenever needed. This is a common practice in Python to separate the reusable code (functions, classes) from the executable code (the part that runs when you execute the script).
if __name__ == "__main__":  
    # Generate the dataset and save to CSV
    print('Generating fraud detection dataset...')
    df = generate_data()
    
    # Split into training and testing datasets
    train_df = df.sample(frac =0.8, random_state = 42)  # this will give us 80% of the data for training
    test_df = df.drop(train_df.index)  # this will give us the remaining 20% of the data for testing
    
    # Save these files as csv 
    train_df.to_csv('data/train_data.csv', index = False) # this will save the training data to a csv file without the index
    test_df.to_csv('data/test_data.csv', index= False)
     
        
    # Print summary statistics
    print(f"\nDataset generated successfully!")
    print(f"Training set: {len(train_df):,} transactions")
    print(f"Test set: {len(test_df):,} transactions")
    print(f"Overall fraud ratio: {df['is_fraud'].mean():.2%}")
    print(f"\nLegitimate transactions - Average amount: ${df[df['is_fraud']==0]['amount'].mean():.2f}")
    print(f"Fraudulent transactions - Average amount: ${df[df['is_fraud']==1]['amount'].mean():.2f}")
    print(f"\nMerchant category distribution (fraud):")
    print(df[df['is_fraud']==1]['merchant_category'].value_counts(normalize=True))  # this will give us the distribution of merchant categories for fraudulent transactions in percentage 
    
import requests
import pandas as pd
import os

def load_api_key(filepath='.apikey'):
    """
    Load API key from a file, with error handling
    """
    try:
        with open(filepath, 'r') as file:
            # Strip whitespace and newline characters
            return file.read().strip()
    except FileNotFoundError:
        print(f"Error: API key file '{filepath}' not found.")
        print("Please create a .apikey file with your Etherscan API key.")
        exit(1)
    except PermissionError:
        print(f"Error: No permission to read the file '{filepath}'.")
        exit(1)

def fetch_ethereum_transactions(address, api_key):
    """
    Fetch transaction list for a specific Ethereum address
    """
    base_url = "https://api.etherscan.io/api"
    
    params = {
        "module": "account",
        "action": "txlist",
        "address": '0xa83114A443dA1CecEFC50368531cACE9F37fCCcb',
        "startblock": 0,
        "endblock": 99999999,
        "sort": "asc",
        "apikey": api_key
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data['status'] == '1':
            transactions = data['result']
            return transactions
        else:
            print(f"Error: {data['message']}")
            return None
    
    except requests.RequestException as e:
        print(f"Error fetching transactions: {e}")
        return None

def preprocess_transactions(transactions):
    """
    Preprocess and clean transaction data
    """
    df = pd.DataFrame(transactions)
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timeStamp'], unit='s')
    
    # Convert value from Wei to Ether
    df['value_eth'] = df['value'].astype(float) / 10**18
    
    # Select and rename columns
    df = df[['hash', 'from', 'to', 'value_eth', 'timestamp']]
    
    return df

def main():
    # Load API key
    API_KEY = load_api_key()
    
    # Wallet address - you can make this configurable or pass as argument
    WALLET_ADDRESS = '0x123...'  # Replace with actual wallet address
    
    # Fetch transactions
    transactions = fetch_ethereum_transactions(WALLET_ADDRESS, API_KEY)
    
    if transactions:
        # Preprocess transactions
        df = preprocess_transactions(transactions)
        
        # Save to CSV
        df.to_csv('ethereum_transactions.csv', index=False)
        
        print(f"Fetched {len(df)} transactions")
        print(df.head())

if __name__ == "__main__":
    main()
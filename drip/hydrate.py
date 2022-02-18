import json
import time
import contract as c
from price import get_drip_price

drip_contract_addr = "0xFFE811714ab35360b67eE195acE7C10D93f89D8C"
wallet_public_addr = "0xeDb0951cF765b6E19881497C407C39914D78c597"

# load private key
wallet_private_key = open('key.txt', "r").readline()

# load abi
f = open('faucet_abi.json')
faucet_abi = json.load(f)

# create contract
faucet_contract = c.connect_to_contract(drip_contract_addr, faucet_abi)

def deposit_amount(addr):
    user_totals = faucet_contract.functions.userInfoTotals(addr).call()
    return user_totals[1]/1000000000000000000

def available(addr):
    return faucet_contract.functions.claimsAvailable(addr).call() / 1000000000000000000

def hydrate():
    txn = faucet_contract.functions.roll().buildTransaction(c.get_tx_options(wallet_public_addr, 500000))
    return c.send_txn(txn, wallet_private_key)

# create infinate loop that checks contract every hour to determine when to hydrate
while True:
    deposit = deposit_amount(wallet_public_addr)
    hydrate_amount = deposit * .01
    avail = available(wallet_public_addr)
    
    if avail >= hydrate_amount:
        hydrate()
        new_deposit = deposit_amount(wallet_public_addr)
        drip_price = get_drip_price()
        total_value = new_deposit * drip_price
        
        print(f"Hydrated! {avail:.3f} added to deposit. Total deposit now {new_deposit:,.2f}")
        print(f"Total value of your deposit is now ${total_value:,.2f}")
        time.sleep(60)
    else:
        print(f"Hydrate not ready {avail:.3f} Drip available. Need {(hydrate_amount - avail):.3f} more")
        for second in range(0, 60*60, 60):
                print(f"Sleep time remaining: {(60*60 - second)/60} min",end="\r")
                time.sleep(60)

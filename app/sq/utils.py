import requests

from stellar_sdk import Keypair, Server, Network, TransactionBuilder

def fund_using_friendbot(public_key):
    # First, check if the account already exists on the testnet
    check_url = f"https://horizon-testnet.stellar.org/accounts/{public_key}"
    r = requests.get(check_url)
    if r.status_code == 404:
        # Let's fund the thing with some XLM, courtesy of friendbot
        url = 'https://friendbot.stellar.org'
        response = requests.get( url, params={'addr': public_key} )
        response.raise_for_status()

def create_zero_balance_account(dest_kp):
    source_kp = Keypair.from_secret('SB2KSX3A5PFVE54UGF2MSYQ2R7DWO4VBTWMCYDCDLTXXN36YRU7MDTPN')
    server = Server('https://horizon-testnet.stellar.org')
    account = server.load_account(source_kp.public_key)
    transaction = (
        TransactionBuilder(
            source_account=account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=10000,
        )
        .append_begin_sponsoring_future_reserves_op(
            sponsored_id=dest_kp.public_key,
            source=source_kp.public_key,
        )
        .append_create_account_op(
            destination=dest_kp.public_key,
            starting_balance="0",
            source=source_kp.public_key,
        )
        .append_end_sponsoring_future_reserves_op(
            source=dest_kp.public_key,
        )
        .set_timeout(30)
        .build()
    )
    transaction.sign(source_kp)
    transaction.sign(dest_kp)
    try:
        response = server.submit_transaction(transaction)
        return True
    except:
        return False

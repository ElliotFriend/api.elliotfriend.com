from flask import jsonify, request
from app.sq import bp

import requests

from stellar_sdk import Keypair, Server, Network, TransactionEnvelope

def fund_using_friendbot(public_key):
    # First, check if the account already exists on the testnet
    check_url = f"https://horizon-testnet.stellar.org/accounts/{public_key}"
    r = requests.get(check_url)
    if r.status_code == 404:
        # Let's fund the thing with some XLM, courtesy of friendbot
        url = 'https://friendbot.stellar.org'
        response = requests.get( url, params={'addr': public_key} )
        response.raise_for_status()

@bp.route('/sq03', methods=['GET', 'POST'])
def side_quest_03():
    if request.method == 'POST':
        json = request.get_json()
        sponsor = json['sponsor']
        claimant = json['claimant']
        server = Server('https://horizon-testnet.stellar.org')
        tx_records = server.transactions().for_account(sponsor).order(desc=True).limit(200).call()['_embedded']['records']
        for rec in tx_records:
            if rec['operation_count'] >= 2 and rec['successful']:
                cb_created = False
                cb_claimed = False
                transaction = TransactionEnvelope.from_xdr(rec['envelope_xdr'], Network.TESTNET_NETWORK_PASSPHRASE).transaction
                operations = server.operations().for_transaction(rec['hash']).call()['_embedded']['records']
                for i in range(0, len(operations)):
                    if operations[i]['type'] == 'create_claimable_balance':
                        if (operations[i]['source_account'] == sponsor and
                                operations[i]['sponsor'] == sponsor and
                                operations[i]['claimants'][0]['destination'] == claimant):
                            cb_id = transaction.get_claimable_balance_id(i)
                            cb_created = True
                    elif operations[i]['type'] == 'claim_claimable_balance':
                        claimed_id = operations[i]['balance_id']
                        if (cb_id == claimed_id and
                                operations[i]['source_account'] == claimant and
                                operations[i]['claimant'] == claimant):
                            cb_claimed = True
                if cb_created and cb_claimed:
                    return jsonify({'success': True, 'message': 'Congratulations! You did it. I always knew you could. Now, head on over to Discord and let me know what you think.'})
        return jsonify({ 'success': False, 'message': 'Sorry, your sponsor account has not successfully submitted a transaction that meets the criteria. Please give it another shot.'})
    sponsor = Keypair.random()
    claimant = Keypair.random()
    for kp in [ sponsor, claimant ]:
        fund_using_friendbot(kp.public_key)
    return jsonify({
        'clue': {
            'sponsor': {
                'public': sponsor.public_key,
                'secret': sponsor.secret
            },
            'claimant': {
                'public': claimant.public_key,
                'secret': claimant.secret
            }
        }
    })

# Public Key	GC6WCTR4JVQR7BOJHFJKH76WMJT3CAHKB2XXTN7L73XF55UVDSSY6CIH
# Secret Key	SCWAVVOREIQSKVPEYGW2CNL354DD7W6ZJFGFRUNJ3DYPYLYTYDPAKXQE

# Public Key	GASSYMEJQCGEMVUSBBC74LNM4YWYHPTC6LAEZZ4PD2NZ54DFDF4NDRYA
# Secret Key	SAEZSUMZPHOFQSU4AI5Q6KAGFBO2QRWMISVZ5ZNEJXPRAZTJRS3JBY46

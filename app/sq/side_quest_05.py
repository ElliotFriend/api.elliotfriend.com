from flask import jsonify, request
from flask_cors import cross_origin
from app.sq import bp
from app.sq.db import get_db, query_db

import requests
from random import randrange
# from hashlib import sha256

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

@bp.route('/sq05', methods=['GET', 'POST'])
@cross_origin()
def side_quest_05_clue():
    if request.method == 'POST':
        pubkey = request.get_json()['public_key']
        response = { 'pubkey': pubkey, 'success': False }
        response['message'] = 'Quest Account has not yet reached the target sequence number.'
        server = Server('https://horizon-testnet.stellar.org')
        account = server.load_account(pubkey)

        db_account = query_db('select * from sq05_clues where quest_pk = ?',
                           [pubkey], one=True)
        if db_account is not None:
            if account.sequence == db_account['target_sequence']:
                response['success'] = True
                response['message'] = 'Congratulations! You figured out my pre_auth transaction. Nice work!!'
                db = get_db()
                db.execute(
                    'INSERT INTO sq05_verification (quest_pk, success)'
                    ' VALUES (?, ?)',
                    (pubkey, 1)
                )
                db.commit()
                return jsonify(response)
        else:
            response['message'] = 'Hmmm... I don\'t seem to recognize that public key...'
        db = get_db()
        db.execute(
            'INSERT INTO sq05_verification (quest_pk, success)'
            ' VALUES (?, ?)',
            (pubkey, 0)
        )
        db.commit()
        return jsonify(response)
    kp = Keypair.random()
    fund_using_friendbot(kp.public_key)
    server = Server('https://horizon-testnet.stellar.org')
    account = server.load_account(kp.public_key)
    starting_sequence = account.sequence
    target_sequence = randrange(starting_sequence + 10, 9223372036854775807)
    account.sequence += 1
    pre_auth_transaction = (
        TransactionBuilder(
            source_account=account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=10000,
        )
        .add_time_bounds(0, 0)
        .append_bump_sequence_op(
            bump_to=target_sequence,
        )
        .build()
    )

    account.sequence -= 2
    transaction = (
        TransactionBuilder(
            source_account=account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=10000,
        )
        .append_set_options_op(
            master_weight=10,
            low_threshold=1,
            med_threshold=10,
            high_threshold=10,
        )
        .append_pre_auth_tx_signer(
            pre_auth_tx_hash=pre_auth_transaction.hash_hex(),
            weight=1,
        )
        .set_timeout(30)
        .build()
    )
    transaction.sign(kp)
    server.submit_transaction(transaction)

    db = get_db()
    db.execute(
        'INSERT INTO sq05_clues (quest_pk, quest_sk, target_sequence)'
        ' VALUES (?, ?, ?)',
        (kp.public_key, kp.secret, target_sequence)
    )
    db.commit()

    response = jsonify({
        'clue': {
            'public': kp.public_key,
            'target_sequence': f'{target_sequence}'
        }
    })
    return response

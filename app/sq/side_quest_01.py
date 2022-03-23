from flask import jsonify, request
from app.sq import bp

import random, string, requests
from stellar_sdk import Keypair, Server, Network, TransactionBuilder
from hashlib import sha256

def get_data_name_string(length):
    letters = string.ascii_letters
    letters += string.digits
    # print(letters)
    dn_string = ''.join(random.choice(letters) for i in range(length - 2))
    dn_string += '=='
    return dn_string

@bp.route('/sq01', methods=['GET'])
def side_quest_01_clue():
    source_kp = Keypair.random()
    response = requests.get('https://friendbot.stellar.org', params={'addr': source_kp.public_key})
    clue_kp = Keypair.random()
    server = Server('https://horizon-testnet.stellar.org')

    source_account = server.load_account(source_kp.public_key)

    transaction = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=100,
        )
        .add_text_memo(
            memo_text="no gaps"
        )
        .append_create_account_op(
            destination=clue_kp.public_key,
            starting_balance="250",
        )
        .append_manage_data_op(
            data_name=get_data_name_string(64),
            # data_name="test1",
            data_value="42.99144200094185",
            source=clue_kp.public_key,
        )
        .append_manage_data_op(
            data_name=get_data_name_string(64),
            # data_name="test2",
            data_value="-87.88350484913607",
            source=clue_kp.public_key,
        )
        .append_hashx_signer(
        sha256_hash=sha256("welcometocleveland".encode('utf-8')).hexdigest(),
        weight=10,
        source=clue_kp.public_key,
        )
        .append_set_options_op(
            master_weight=10,
            low_threshold=20,
            med_threshold=20,
            high_threshold=20,
            source=clue_kp.public_key,
        )
        .set_timeout(30)
        .build()
    )

    transaction.sign(source_kp)
    transaction.sign(clue_kp)
    resp = server.submit_transaction(transaction)
    # print(resp)

    data = {
        'clue': clue_kp.secret
    }

    return jsonify(data)

from flask import jsonify, request
from flask_cors import cross_origin
from app.sq import bp
from app.sq.db import get_db

import requests

from stellar_sdk import Keypair, Server, Network

@bp.route('/sq04', methods=['GET', 'POST'])
@cross_origin()
def side_quest_04_clue():
    if request.method == 'POST':
        pubkey = request.get_json()['public_key']
        response = { 'pubkey': pubkey, 'success': False }
        response['message'] = 'Quest Account has not yet submitted a correct transaction.'
        server = Server('https://horizon-testnet.stellar.org')
        scorecard = {
            'created': False,
            'funder': '',
            'starting_balance': 0,
            'inflation': '',
            'signers': 0,
            'signer_types': { 'hash': 0, 'pubkey': 0 },
            'weights': { 'low': 0, 'med': 0, 'high': 0, 'master': 1 },
            'memo': '',
            'cb': False,
            'cb_dest': '',
            'cb_op_num': 0,
            'new_account': False,
            'new_account_pubkey': '',
            'new_account_funder': '',
            'new_account_balance': 1,
            'new_account_op_num': 0,
        }
        try:
            tx_records = server.transactions().for_account(pubkey).limit(200).order(desc=True).call()['_embedded']['records']
        except:
            db = get_db()
            db.execute(
                'INSERT INTO sq04_verification (quest_pk, success)'
                ' VALUES (?, ?)',
                (pubkey, 0)
            )
            db.commit()
            return response
        for rec in range(len(tx_records)):
            if tx_records[rec]['operation_count'] >= 7:
                scorecard['memo'] = tx_records[rec]['memo_type']
                operations = server.operations().for_transaction(tx_records[rec]['hash']).call()['_embedded']['records']
                for i in range(0, len(operations)):
                    op = operations[i]
                    if op['type'] == 'create_account':
                        if op['account'] == pubkey:
                            scorecard['created'] = True
                            scorecard['funder'] = op['funder']
                            scorecard['starting_balance'] = int(float(op['starting_balance']))
                        else:
                            scorecard['new_account'] = True
                            scorecard['new_account_op_num'] = i
                            scorecard['new_account_pubkey'] = op['account']
                            scorecard['new_account_funder'] = op['funder']
                            scorecard['new_account_balance'] = int(float(op['starting_balance']))
                    elif op['type'] == 'set_options':
                        scorecard['inflation'] = op['inflation_dest'] if 'inflation_dest' in op else scorecard['inflation']
                        scorecard['weights']['low'] = op['low_threshold'] if 'low_threshold' in op else scorecard['weights']['low']
                        scorecard['weights']['med'] = op['med_threshold'] if 'med_threshold' in op else scorecard['weights']['med']
                        scorecard['weights']['high'] = op['high_threshold'] if 'high_threshold' in op else scorecard['weights']['high']
                        scorecard['weights']['master'] = op['master_key_weight'] if 'master_key_weight' in op else scorecard['weights']['master']
                        if op['signer_key']:
                            scorecard['signers'] += 1
                            scorecard['signer_types']['hash'] = op['signer_weight'] if op['signer_key'].startswith('X') else scorecard['signer_types']['hash']
                            scorecard['signer_types']['pubkey'] = op['signer_weight'] if op['signer_key'].startswith('G') else scorecard['signer_types']['pubkey']
                    elif op['type'] == 'create_claimable_balance':
                        if op['sponsor'] == pubkey:
                            scorecard['cb'] = True
                            scorecard['cb_op_num'] = i
                            for clmt in op['claimants']:
                                scorecard['cb_dest'] = clmt['destination'] if clmt['destination'] != pubkey else scorecard['cb_dest']
            response['scorecard'] = scorecard
            if (
                    scorecard['created'] == True and scorecard['starting_balance'] == 500 and
                    scorecard['signers'] == 2 and scorecard['weights']['master'] == 0 and
                    scorecard['signer_types']['hash'] > 0 and scorecard['signer_types']['pubkey'] > 0 and
                    scorecard['signer_types']['hash'] >= scorecard['weights']['low'] and
                    scorecard['signer_types']['hash'] >= scorecard['weights']['med'] and
                    scorecard['signer_types']['hash'] < scorecard['weights']['high'] and
                    scorecard['signer_types']['pubkey'] >= scorecard['weights']['low'] and
                    scorecard['signer_types']['pubkey'] >= scorecard['weights']['med'] and
                    scorecard['signer_types']['pubkey'] < scorecard['weights']['high'] and
                    scorecard['signer_types']['hash'] + scorecard['signer_types']['pubkey'] >= scorecard['weights']['high'] and
                    scorecard['memo'] == 'text' and scorecard['funder'] == scorecard['inflation'] and
                    scorecard['cb'] == True and scorecard['cb_op_num'] < scorecard['new_account_op_num'] and
                    scorecard['cb_dest'] == scorecard['new_account_pubkey'] and scorecard['new_account_balance'] == 0 and
                    scorecard['new_account_funder'] == pubkey
                ):
                response['success'] = True
                response['message'] = 'Congratulations! You did it. I always knew you could. Now, head on over to Discord and let me know what you think.'
                db = get_db()
                db.execute(
                    'INSERT INTO sq04_verification (quest_pk, success)'
                    ' VALUES (?, ?)',
                    (pubkey, 1)
                )
                db.commit()
                return jsonify(response)
        db = get_db()
        db.execute(
            'INSERT INTO sq04_verification (quest_pk, success)'
            ' VALUES (?, ?)',
            (pubkey, 0)
        )
        db.commit()
        return jsonify(response)
    kp = Keypair.random()
    db = get_db()
    db.execute(
        'INSERT INTO sq04_clues (quest_pk, quest_sk)'
        ' VALUES (?, ?)',
        (kp.public_key, kp.secret)
    )
    db.commit()
    response = jsonify({
        'clue': {
            'public': kp.public_key,
            'secret': kp.secret
        }
    })
    return response

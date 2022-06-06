from flask import jsonify, request

from app.sq import bp
from app.sq.db import query_db, insert_clue, insert_verify
from app.sq.utils import create_zero_balance_account

import requests
import json

from stellar_sdk import Keypair, Server, StrKey
from random import randrange

@bp.route('/sq06', methods=['GET', 'POST'])
def side_quest_06_clue():
    if request.method == 'POST':
        req = request.get_json()
        response = {
            'success': False,
            'message': 'Muxed accounts have not yet received the required payments.'
        }
        if 'pubkey' not in req:
            response['message'] = "Sorry, I can't help you verify until you generate a clue."
            return jsonify(response)
        if not StrKey.is_valid_ed25519_public_key(req['pubkey']):
            response['message'] = 'Sorry, something is wrong with the public key you gave. Please try again.'
            return jsonify(response)
        pubkey = req['pubkey']
        db_clue = query_db('SELECT * FROM sq06_clues WHERE quest_pk = ?',
                           [pubkey], one=True)
        db_muxes = json.loads(db_clue['muxes'])

        total_paid = 0
        muxes_received = []

        server = Server('https://horizon-testnet.stellar.org')
        payments = server.payments().for_account(pubkey).limit(200).order(desc=True).call()['_embedded']['records']
        for p in payments:
            if 'to_muxed' in p:
                if int(p['to_muxed_id']) in db_muxes:
                    total_paid += int(float(p['amount']))
                    muxes_received.append(int(p['to_muxed_id']))

        muxes_received = list(set(muxes_received))
        db_muxes.sort()
        muxes_received.sort()
        if db_muxes == muxes_received and sum(db_muxes) == total_paid:
            response['success'] = True
            response['message'] = 'Hooray! You muxed that account so good! Well done. Head over to discord and let me know what you think.'
        insert_verify("06", pubkey, response['success'])
        return jsonify(response)

    kp = Keypair.random()
    muxes = []
    response = {
        'clue': {
            'public': kp.public_key
        }
    }
    if create_zero_balance_account(kp):
        for i in range(randrange(3, 8)):
            muxes.append(randrange(3,1001))

        response['clue']['muxes'] = list(set(muxes))
        insert_clue(
            '06',
            ['quest_pk', 'quest_sk', 'muxes'],
            (kp.public_key, kp.secret, json.dumps(response['clue']['muxes']))
        )
        return jsonify(response)
    else:
        return jsonify({
            'message': 'Something went wrong generating your clue. Please refresh the page and try again.',
        })

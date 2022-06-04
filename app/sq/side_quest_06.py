from flask import jsonify, request
from flask_cors import cross_origin

from app.sq import bp
from app.sq.db import get_db, query_db
from app.sq.utils import create_zero_balance_account

import requests
import json

from stellar_sdk import Keypair, Server, Network, TransactionBuilder
from random import randrange

# Public Key	GBY7IAKYI3RHZSNSHX7L3MJVZOWS6UDUPOQSUBNIXVSATEBGARE5BGVG
# Secret Key	SC4U3ZGXQE6EMKTJHYRPYWFPXIWIU54LW66ZDDK2J5FDPG6TYWEPFJFM
#
# Base Account G Address	GBY7IAKYI3RHZSNSHX7L3MJVZOWS6UDUPOQSUBNIXVSATEBGARE5BGVG
# Muxed Account ID	        123
# Muxed Account M Address	MBY7IAKYI3RHZSNSHX7L3MJVZOWS6UDUPOQSUBNIXVSATEBGARE5AAAAAAAAAAAAPPKWI
#
# Public Key	GAZY7ZU2FYUAIYNQIGJSMCBXP6F7EVK47KMLBZDACAL5NW4UTSIOF5NB
# Secret Key	SAETC2ALTATJ4BASNPZY45YNZEOJ6WVHPWVSE65APBIDQDXAFQ4XBJG3

@bp.route('/sq06', methods=['GET', 'POST'])
@cross_origin()
def side_quest_06_clue():
    kp = Keypair.from_secret('SAO5OFUG5DZ7VNYMIOWKI2JSLAD455OBXQYNWS2H5VUTDIUSM7JH37OO')
    muxes = [145, 245, 794, 30, 574]
    if request.method == 'POST':
        pubkey = request.get_json()['public_key']
        response = { 'pubkey': pubkey, 'success': False }
        response['message'] = 'Muxed accounts have not yet received the required payments.'
        server = Server('https://horizon-testnet.stellar.org')

        total_paid = 0
        muxes_received = []

        payments = server.payments().for_account(pubkey).order(desc=True).call()['_embedded']['records']
        response['payments'] = payments
        for p in payments:
            if 'to_muxed' in p:
                if int(p['to_muxed_id']) in muxes:
                    total_paid += int(float(p['amount']))
                    muxes_received.append(int(p['to_muxed_id']))

        # for payment in payments:
        #     print(payment)
        muxes_received = list(set(muxes_received))
        response['paid'] = total_paid
        response['muxes_received'] = muxes_received
        muxes.sort()
        muxes_received.sort()
        if muxes == muxes_received and sum(muxes) == total_paid:
            response['success'] = True
            response['message'] = 'Hooray! You muxed that account so good! Well done. Head over to discord and let me know what you think.'
        return jsonify(response)

    # if create_zero_balance_account(kp):
    # num_muxes = randrange(3, 8)
    # for i in range(randrange(3, 8)):
    #     muxes.append(randrange(3,1001))
    response = jsonify({
        'clue': {
            'public': kp.public_key,
            'secret': kp.secret,
            'muxes': muxes
        }
    })
    return response
    # else:
    #     return jsonify({
    #         'message': 'Something went wrong generating your clue. Please try again.',
    #         'success': False
    #     })

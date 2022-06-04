from flask import jsonify, request
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
def side_quest_06_clue():
    kp = Keypair.from_secret('SAO5OFUG5DZ7VNYMIOWKI2JSLAD455OBXQYNWS2H5VUTDIUSM7JH37OO')
    # if create_zero_balance_account(kp):
    # num_muxes = randrange(3, 7)
    muxes = [
        145,
        245,
        794,
        30,
        574
    ]
    # for i in range(randrange(3,7)):
    #     muxes.append(randrange(3,1000))
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

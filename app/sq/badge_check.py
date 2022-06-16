from flask import jsonify, request
from app.sq import bp

from stellar_sdk import Server
from stellar_sdk.sep import stellar_toml, federation
from stellar_sdk.exceptions import NotFoundError

import itertools

@bp.route('/badges', methods=['POST'])
def batch_check():
    req = request.get_json()
    if 'public_keys' not in req:
        return jsonify({
            'error': 'Missing required field: `public_keys`'
        })
    public_keys = req['public_keys']

    horizon_servers = [
        Server('https://horizon.stellar.org'),
        Server('https://horizon.publicnode.org'),
        Server('https://horizon.stellar.lobstr.co'),
    ]
    server_iter = itertools.cycle(horizon_servers)

    def get_prize_transaction(hash):
        ops = next(server_iter).operations().for_transaction(hash).limit(100).call()['_embedded']['records']
        prize_record = [op for op in ops if ('asset_type' in op and op['asset_type'] == 'native')]

        if prize_record:
            return int(float(prize_record[0]['amount']))
        else:
            return False
    
    def get_federated_address(public_key, home_domain):
        try:
            federated_record = federation.resolve_account_id(public_key, home_domain)
            return federated_record.stellar_address
        except:
            return False

    currencies = (stellar_toml.fetch_stellar_toml('quest.stellar.org')['CURRENCIES'])
    assets = []
    for c in currencies:
        assets.append({k: v for k, v in c.items() if k not in ['image', 'name', 'desc']})
    issuers = [a['issuer'] for a in assets]
    mono_issuers = [a['issuer'] for a in assets if 'tag' in a and a['tag'] == 'mono']
    codes = [a['code'] for a in assets]

    owned_badges = {}
    for pubkey in public_keys:
        operations_records = []
        owned_badges[pubkey] = {}
        owned_badges[pubkey]['badges'] = []
        
        try:
            account_details = next(server_iter).accounts().account_id(pubkey).call()
        except NotFoundError:
            owned_badges[pubkey]['meta'] = {
                'error': 'Resource Missing.'
            }
            continue

        owned_badges[pubkey]['meta'] = {
            'sequence': account_details['sequence'],
            'native_balance': "{:.7f}".format(float(next(b['balance'] for b in account_details['balances'] if b['asset_type'] == 'native')))
        }
        if 'last_modified_time' in account_details:
            owned_badges[pubkey]['meta']['last_modified'] = account_details['last_modified_time']
        if 'home_domain' in account_details:
            stellar_address = get_federated_address(pubkey, account_details['home_domain'])
            if stellar_address:
                owned_badges[pubkey]['meta']['stellar_address'] = stellar_address

        operations_call_builder = (
            next(server_iter).operations().for_account(pubkey).limit(200).order(desc=False)
        )
        operations_records += operations_call_builder.call()['_embedded']['records']
        page_count = 0
        while page_records := operations_call_builder.next()['_embedded']['records']:
            operations_records += page_records
            page_count += 1
        
        badge_records = []
        for rec in operations_records:
            if (rec['transaction_successful'] == True
                and rec['type'] == 'create_account'
                and rec['source_account'] != pubkey
                and rec['account'] == pubkey
            ):
                owned_badges[pubkey]['meta']['created_at'] = rec['created_at']
            elif (rec['transaction_successful'] == True
                and rec['type'] == 'payment'
                and rec['asset_type'] != 'native'
                and rec['to'] == pubkey
                and rec['asset_code'] in codes
                and rec['asset_issuer'] in issuers
                and rec['from'] in issuers
            ):
                badge_records.append(rec)
            elif (rec['transaction_successful'] == True
                    and rec['type'] == 'create_claimable_balance'
                    and rec['asset'].split(':')[0] in codes
                    and rec['asset'].split(':')[1] in issuers
                    and rec['source_account'] in issuers
                    and pubkey in [c['destination'] for c in rec['claimants']]
            ):
                badge_records.append(rec)
        for badge in badge_records:
            badge_code = badge['asset_code'] if 'asset_code' in badge else badge['asset'].split(':')[0]
            badge_issuer = badge['asset_issuer'] if 'asset_issuer' in badge else badge['asset'].split(':')[1]
            if 'first_badge' not in owned_badges[pubkey]['meta']:
                if badge_issuer in mono_issuers:
                    owned_badges[pubkey]['meta']['first_badge_mono'] = True
                owned_badges[pubkey]['meta']['first_badge_date'] = badge['created_at']
                owned_badges[pubkey]['meta']['first_badge'] = badge_code
            else:
                if owned_badges[pubkey]['meta']['first_badge_date'] > badge['created_at']:
                    if badge_issuer in mono_issuers:
                        owned_badges[pubkey]['meta']['first_badge_mono'] = True
                    owned_badges[pubkey]['meta']['first_badge_date'] = badge['created_at']
                    owned_badges[pubkey]['meta']['first_badge'] = badge_code
            if (
                badge['type'] == 'payment'
                or not any([True for i in [b['issuer'] for b in owned_badges[pubkey]['badges']] if i == badge_issuer])
                ):
                badge_dict = {
                    'date': badge['created_at'].split('T')[0],
                    'code': badge_code,
                    'issuer': badge_issuer,
                    'owned': True,
                    'hash': badge['transaction_hash'],
                    'operation': badge['id'],
                    'link': f'https://stellar.expert/explorer/public/tx/{badge["transaction_hash"]}',
                    'prize': get_prize_transaction(badge['transaction_hash']),
                }
                if badge_issuer in mono_issuers:
                    badge_dict['mono'] = True
                owned_badges[pubkey]['badges'].append(badge_dict)
        
        owned_badges[pubkey]['meta']['badges_count'] = len(owned_badges[pubkey]['badges'])
        
    return jsonify(owned_badges)

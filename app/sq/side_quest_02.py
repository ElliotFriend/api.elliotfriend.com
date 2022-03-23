from flask import jsonify, request
from app.sq import bp

import requests

from stellar_sdk import Keypair, Server, Network, TransactionBuilder, Asset, LiquidityPoolAsset, Price, Claimant, ClaimPredicate

@bp.route('/sq02', methods=['GET'])
def side_quest_02_clue():
    issue_kp = Keypair.from_secret('SBQHCV7S6SNJZUKTFT7VYOVPWQC2SQHL4UGDKIFLQDACAR362GRQSUM6')
    source_kp = Keypair.from_secret('SDC6QRYQWTM5QFMDYSTDLZ4AABLUCBS262LDKP4LB5A6RYO4S4BBVHFL')
    quest_kp = Keypair.random()
    sign_kp = Keypair.random()

    server = Server("https://horizon-testnet.stellar.org")

    yxlm = Asset("yXLM", issue_kp.public_key)
    lp_asset = LiquidityPoolAsset(
        asset_a=Asset.native(),
        asset_b=yxlm
    )

    source_account = server.load_account(source_kp.public_key)
    transaction = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=10000
        )
        .append_change_trust_op(
            asset=yxlm,
            source=source_kp.public_key
        )
        .append_payment_op(
            destination=source_kp.public_key,
            amount="50",
            asset=yxlm,
            source=issue_kp.public_key
        )
        .append_begin_sponsoring_future_reserves_op(
            sponsored_id=quest_kp.public_key,
            source=source_kp.public_key
        )
        .append_begin_sponsoring_future_reserves_op(
            sponsored_id=sign_kp.public_key,
            source=source_kp.public_key
        )
        .append_create_account_op(
            destination=quest_kp.public_key,
            starting_balance="50",
            source=source_kp.public_key
        )
        .append_change_trust_op(
            asset=yxlm,
            source=quest_kp.public_key
        )
        .append_change_trust_op(
            asset=lp_asset,
            source=quest_kp.public_key
        )
        .append_payment_op(
            destination=quest_kp.public_key,
            amount="50",
            asset=yxlm,
            source=source_kp.public_key
        )
        .append_create_account_op(
            destination=sign_kp.public_key,
            starting_balance="0",
            source=source_kp.public_key
        )
        .append_create_claimable_balance_op(
            asset=Asset.native(),
            amount="50",
            claimants=[
                Claimant(
                    destination=sign_kp.public_key,
                    predicate=ClaimPredicate.predicate_unconditional()
                ),
                Claimant(
                    destination=source_kp.public_key,
                    predicate=ClaimPredicate.predicate_unconditional()
                )
            ],
            source=source_kp.public_key
        )
        .append_liquidity_pool_deposit_op(
            liquidity_pool_id=lp_asset.liquidity_pool_id,
            max_amount_a="50",
            max_amount_b="50",
            min_price=Price(1, 1),
            max_price=Price(1, 1),
            source=quest_kp.public_key
        )
        .append_ed25519_public_key_signer(
            account_id=sign_kp.public_key,
            weight=10,
            source=quest_kp.public_key
        )
        .append_set_options_op(
            master_weight=0,
            low_threshold=10,
            med_threshold=10,
            high_threshold=10,
            source=quest_kp.public_key,
        )
        .append_end_sponsoring_future_reserves_op(
            source=quest_kp.public_key
        )
        .append_end_sponsoring_future_reserves_op(
            source=sign_kp.public_key
        )
        .set_timeout(200)
        .build()
    )
    transaction.sign(source_kp)
    transaction.sign(quest_kp)
    transaction.sign(issue_kp)
    transaction.sign(sign_kp)
    resp = server.submit_transaction(transaction)
    print(resp)

    data = {
        'clue': sign_kp.secret
    }
    return jsonify(data)

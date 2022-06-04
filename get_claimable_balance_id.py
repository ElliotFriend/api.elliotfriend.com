#!/usr/bin/env python3

from stellar_sdk import Keypair
from stellar_sdk import xdr as stellar_xdr
from stellar_sdk.utils import sha256

account_id = Keypair.from_public_key('GCPABJ57XGB5PP37ILTEQYPC2OPXGL6LHB43OUPFYCTZJFX2JELQLWX3').xdr_account_id()
# account_id = Keypair.from_public_key(self.source.account_id).xdr_account_id()
# <stellar_sdk.xdr.account_id.AccountID object at 0x7f25df88db50>
# AAAAAL1hTjxNYR+FyTlSo//WYmexAOoOr3m36/7uXvaVHKWP

operation_id = stellar_xdr.OperationID(
    type=stellar_xdr.EnvelopeType.ENVELOPE_TYPE_OP_ID,
    # <EnvelopeType.ENVELOPE_TYPE_OP_ID: 6>
    # AAAABg==
    id=stellar_xdr.OperationIDId(
        source_account=account_id, # see above
        seq_num=stellar_xdr.SequenceNumber(stellar_xdr.Int64(3473554800640001)),
        # seq_num=stellar_xdr.SequenceNumber(stellar_xdr.Int64(self.sequence)),
        # <stellar_sdk.xdr.sequence_number.SequenceNumber object at 0x7f25df8a02e0>
        # AAsdkgAAAAE=
        op_num=stellar_xdr.Uint32(0),
        # op_num=stellar_xdr.Uint32(operation_index),
        # <stellar_sdk.xdr.uint32.Uint32 object at 0x7f25dfd933a0>
        # AAAAAA==
    ),
    # <stellar_sdk.xdr.operation_id_id.OperationIDId object at 0x7f25df8a02e0>
    # AAAAAL1hTjxNYR+FyTlSo//WYmexAOoOr3m36/7uXvaVHKWPAAsdkgAAAAEAAAAA
)
# <stellar_sdk.xdr.operation_id.OperationID object at 0x7f25e15d9a90>
# AAAABgAAAAC9YU48TWEfhck5UqP/1mJnsQDqDq95t+v+7l72lRyljwALHZIAAAABAAAAAA==
# b'\x00\x00\x00\x06\x00\x00\x00\x00\xbdaN<Ma\x1f\x85\xc99R\xa3\xff\xd6bg\xb1\x00\xea\x0e\xafy\xb7\xeb\xfe\xee^\xf6\x95\x1c\xa5\x8f\x00\x0b\x1d\x92\x00\x00\x00\x01\x00\x00\x00\x00'

operation_id_hash = sha256(operation_id.to_xdr_bytes())
# sha256 here is coded as `hashlib.sha256(whatever_data_i_am_passing).digest()`
# <sha256 HASH object @ 0x7f25df8deed0> (this is without the call to `digest()`)
# b'\x9e\xa1\xd1\xb8$\xc9\xdfV\xfb\x12\x91j^&\xb9\xbf\xbb\x01\xaat\xd8D\x9f\xbd8S(\xa8\x92d\xc6\xd7'
# 9ea1d1b824c9df56fb12916a5e26b9bfbb01aa74d8449fbd385328a89264c6d7 (this is when I use `hexdigest()` instead)

balance_id = stellar_xdr.ClaimableBalanceID(
    type=stellar_xdr.ClaimableBalanceIDType.CLAIMABLE_BALANCE_ID_TYPE_V0,
    # <ClaimableBalanceIDType.CLAIMABLE_BALANCE_ID_TYPE_V0: 0>
    # AAAAAA==

    v0=stellar_xdr.Hash(operation_id_hash),
    # <stellar_sdk.xdr.hash.Hash object at 0x7f31e6a4ec70>
    # nqHRuCTJ31b7EpFqXia5v7sBqnTYRJ+9OFMoqJJkxtc=
)
# <stellar_sdk.xdr.claimable_balance_id.ClaimableBalanceID object at 0x7f31e6a4ebb0>
# AAAAAJ6h0bgkyd9W+xKRal4mub+7Aap02ESfvThTKKiSZMbX
# b'\x00\x00\x00\x00\x9e\xa1\xd1\xb8$\xc9\xdfV\xfb\x12\x91j^&\xb9\xbf\xbb\x01\xaat\xd8D\x9f\xbd8S(\xa8\x92d\xc6\xd7'

print(balance_id.to_xdr_bytes().hex())
# return balance_id.to_xdr_bytes().hex()
# b'\x00\x00\x00\x00\x9e\xa1\xd1\xb8$\xc9\xdfV\xfb\x12\x91j^&\xb9\xbf\xbb\x01\xaat\xd8D\x9f\xbd8S(\xa8\x92d\xc6\xd7'
# AAAAAJ6h0bgkyd9W+xKRal4mub+7Aap02ESfvThTKKiSZMbX
# 000000009ea1d1b824c9df56fb12916a5e26b9bfbb01aa74d8449fbd385328a89264c6d7
# 000000009ea1d1b824c9df56fb12916a5e26b9bfbb01aa74d8449fbd385328a89264c6d7

# 0000000071cd179151c4f92ed7430152c1b5e8d7b9879b34ee43502b7e288b76ad5ab110
# 00000000a92926716f86e2e227f2f0aa05d81ee9f8eb2ef297c71417d244b0f25eefd593
# 00000000a92926716f86e2e227f2f0aa05d81ee9f8eb2ef297c71417d244b0f25eefd593
# AAAAAgAAAAC9YU48TWEfhck5UqP/1mJnsQDqDq95t+v+7l72lRyljwAAAlgACx2SAAAABAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAAAAAAACgAAAAVIZWxsbwAAAAAAAAEAAAAFVGhlcmUAAAAAAAABAAAAAL1hTjxNYR+FyTlSo//WYmexAOoOr3m36/7uXvaVHKWPAAAACgAAAARpdCdzAAAAAQAAAARuaWNlAAAAAQAAAAC9YU48TWEfhck5UqP/1mJnsQDqDq95t+v+7l72lRyljwAAAAoAAAACdG8AAAAAAAEAAAAEbWVldAAAAAEAAAAAvWFOPE1hH4XJOVKj/9ZiZ7EA6g6vebfr/u5e9pUcpY8AAAAKAAAAA3lvdQAAAAABAAAABW1hZGFtAAAAAAAAAQAAAAC9YU48TWEfhck5UqP/1mJnsQDqDq95t+v+7l72lRyljwAAAA4AAAAAAAAAARsfP4AAAAABAAAAAAAAAAAlLDCJgIxGVpIIRf4trOYtg75i8sBM548em57wZRl40QAAAAAAAAABAAAAACUsMImAjEZWkghF/i2s5i2DvmLywEznjx6bnvBlGXjRAAAADwAAAACpKSZxb4bi4ify8KoF2B7p+Osu8pfHFBfSRLDyXu/VkwAAAAAAAAACZRl40QAAAEDCMNYJyV/wEkbYVaXykgk+wBedw2Jc2kaHCKqgZY8nuOWV010ZYTK1Fdo3E043ZePGKGnAZnn8aQXDL5LYpGUJlRyljwAAAECb+7tXeOIw87skccpOPGNTjjmes0+8wsYM5CfryKJJ7aIG04uoETO5k8V4LeLmtjBMvlYZSWsJEQTK+a8SReMP

# 000000007f19ee186ba540bf803246d92f7d410d3b86d94a9a5dab96eea1f90ce23b05ed
# 000000007f19ee186ba540bf803246d92f7d410d3b86d94a9a5dab96eea1f90ce23b05ed
# 000000002c3daf4f220673da7ea964dd97d13585e1b36c2b0557b538f79f6b7d0d5c6a1a

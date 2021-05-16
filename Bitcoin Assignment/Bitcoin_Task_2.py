from bitcoinutils.setup import setup
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, Locktime, Sequence
from bitcoinutils.keys import P2pkhAddress, P2shAddress, PrivateKey
from bitcoinutils.script import Script
from bitcoinutils.constants import TYPE_ABSOLUTE_TIMELOCK
from bitcoinutils.proxy import NodeProxy
import argparse
from bitcoinutils.constants import SATOSHIS_PER_BITCOIN
import requests


def to_satoshis(num):
    # we need to round because of how floats are stored internally:
    # e.g. 0.29 * 100000000 = 28999999.999999996
    return int(round(num * SATOSHIS_PER_BITCOIN))


def main():
    # always remember to setup the network
    setup('regtest')

    #
    # This script creates a P2SH address containing a CHECKLOCKTIMEVERIFY plus a P2PKH locking funds with a key as
    # well as for an absolute amount of blocks or an absolute amount of seconds since the transaction.
    #

    parser = argparse.ArgumentParser(
        description='Give the private key, a future time expressed either in block height or in UNIX Epoch time and '
                    'the P2SH address to send the funds')
    parser.add_argument('key', help="Add the private key.")
    parser.add_argument('-param', type=int, help="Add the number of blocks or the time expressed in seconds.")
    parser.add_argument('-to_address', type=str, help="Add the adress that will sent/spend")
    args = parser.parse_args()

    # set values
    key = args.key
    absolute_param = args.param
    send_address = args.to_address

    # set Locktime
    seq = Sequence(TYPE_ABSOLUTE_TIMELOCK, absolute_param)
    locktime = Locktime(absolute_param)

    # set proxy
    username = "alice"
    password = "DONT_USE_THIS_YOU_WILL_GET_ROBBED_8ak1gI25KFTvjovL3gAM967mies3E="
    proxy = NodeProxy(username, password).get_proxy()

    # secret key corresponding to the pubkey needed for the P2SH (P2PKH) transaction
    p2pkh_sk = PrivateKey(key)

    p2pkh_pk = p2pkh_sk.get_public_key()

    # get the address (from the public key)
    p2pkh_addr = p2pkh_pk.get_address()

    # print("Private key: " + p2pkh_sk. to_wif(compressed=True))
    # print("Public key: " + p2pkh_pk.to_hex(compressed=True))
    # print("P2PKH Address: " + p2pkh_addr.to_string())

    # create the redeem script
    redeem_script = Script(
        [seq.for_script(), 'OP_CHECKLOCKTIMEVERIFY', 'OP_DROP', 'OP_DUP', 'OP_HASH160', p2pkh_addr.to_hash160(),
         'OP_EQUALVERIFY', 'OP_CHECKSIG'])

    # accept a P2SH address to get the funds from
    addr = P2shAddress.from_script(redeem_script)
    print("The P2SH address to get the funds from is : " + addr.to_string())

    # check if the P2SH address has any UTXOs to get funds from

    proxy.importaddress(addr.to_string(), "P2SH to get the funds from")
    minconf = 0
    maxconf = 99999999
    my_list = proxy.listunspent(minconf, maxconf, [addr.to_string()])

    # Gather all funds that the P2SH address received to send to the P2PKH address provided

    txin_list = []
    btc_to_send = 0
    for i in my_list:
        txin = TxInput(i['txid'], i['vout'], sequence=seq.for_input_sequence())
        txin_list.append(txin)
        btc_to_send = btc_to_send + i['amount']

    if btc_to_send == 0:
        print("No btc found to send")
        quit()

    # accept a P2PKH address to send the funds to
    to_addr = P2pkhAddress(send_address)
    print("The P2PKH address to send the funds to is : " + to_addr.to_string())

    # calculate the appropriate fees with respect to the size of the transaction
    response = requests.get("https://mempool.space/api/v1/fees/recommended")
    fee_per_byte = response.json()['fastestFee']
    print("Fastest fee per byte is : %d " % fee_per_byte)

    # calculate transaction size as described at 
    # https://bitcoin.stackexchange.com/questions/1195/how-to-calculate-transaction-size-before-sending-legacy-non-segwit-p2pkh-p2sh 
    tx_size = len(my_list) * 180 + 34 + 10 + len(my_list)
    total_fees = tx_size * fee_per_byte / (1024 * 10 ** 8)
    print('Total fees are : ', total_fees)

    # Calculate the final amount
    amount = btc_to_send - total_fees
    # print(amount)

    # Create transaction output
    txout = TxOutput(to_satoshis(amount), to_addr.to_script_pub_key())

    # Create transaction after the inputs and the outputs
    tx = Transaction(txin_list, [txout], locktime.for_transaction())

    # For each transaction - when dealing with multiple inputs, you will need to sign all of them
    for i, txin in enumerate(my_list):
        sig = p2pkh_sk.sign_input(tx, i, redeem_script)
        # print(sig)
        # set the scriptSig (unlocking script) -- unlock the P2PKH (sig, pk) plus
        # the redeem script, since it is a P2SH
        txin.script_sig = Script([sig, p2pkh_pk.to_hex(), redeem_script.to_hex()])

    # display the raw signed transaction, ready to be broadcasted
    signed_tx = tx.serialize()
    print("\nRaw signed transaction:\n" + signed_tx)

    # display the raw unsigned transaction
    print("\nRaw unsigned transaction:\n" + tx.serialize())

    # display the transaction id
    print("\nTxId:", tx.get_txid())

    # verify that the transaction is valid and will be accepted by the Bitcoin nodes
    # if the transaction is valid, send it to the blockchain

    is_valid = proxy.testmempoolaccept([signed_tx])
    # print(is_valid)
    if is_valid[0]['allowed']:
        print("Transaction is valid!")
        print("Sending transaction to blockchain..")
        proxy.sendrawtransaction(signed_tx)
    else:
        print("Transaction not valid")
        quit()


if __name__ == "__main__":
    main()

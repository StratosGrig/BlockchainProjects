from bitcoinutils.setup import setup
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, Locktime
from bitcoinutils.keys import P2pkhAddress, P2shAddress, PrivateKey
from bitcoinutils.script import Script
from bitcoinutils.constants import TYPE_ABSOLUTE_TIMELOCK
import argparse
from decimal import Decimal
from binascii import hexlify, unhexlify
from bitcoinutils.constants import SATOSHIS_PER_BITCOIN


def to_satoshis(num):
    # we need to round because of how floats are stored insternally:
    # e.g. 0.29 * 100000000 = 28999999.999999996
    return int( round(num * SATOSHIS_PER_BITCOIN) )

def main():
    # always remember to setup the network
    setup('regtest')

    #
    # This script creates a P2SH address containing a CHECKLOCKTIMEVERIFY plus
    # a P2PKH locking funds with a key as well as for an absolute amount of blocks or an absolute amount of seconds since the transaction.
    #

    parser = argparse.ArgumentParser(description='Give the private key, a future time expressed either in block height or in UNIX Epoch time and the P2SH address will be displayed')
    parser.add_argument('key', help="Add the private key.")
    parser.add_argument('-param', type= int, help = "Add the number of blocks or the time expressed in seconds.")
    parser.add_argument('-to_address', type= str , help="Add the adress that will sent/spend")
    args = parser.parse_args()
        
    # set values
    key = args.key 
    absolute_param = args.param
    send_address = args.to_address
    txid = '76c102821b916a625bd3f0c3c6e35d5c308b7c23e78b8866b06a3a466041db0a'
    vout = 0
        
    locktime = Locktime(absolute_param)
    
    
    # create transaction input from tx id of UTXO (contained 11.1 tBTC)
    txin = TxInput(txid, vout, sequence= locktime.for_transaction())
    
    
    # secret key corresponding to the pubkey needed for the P2SH (P2PKH) transaction
    p2pkh_sk = PrivateKey(key)
    
    p2pkh_pk = p2pkh_sk.get_public_key()

    # get the address (from the public key)
    p2pkh_addr = p2pkh_pk.get_address()

    #print("Private key: " + p2pkh_sk. to_wif(compressed=True))
    #print("Public key: " + p2pkh_pk.to_hex(compressed=True))
    #print("P2PKH Address: " + p2pkh_addr.to_string())

    # create the redeem script
    redeem_script = Script([absolute_param, 'OP_CHECKLOCKTIMEVERIFY', 'OP_DROP', 'OP_DUP', 'OP_HASH160', p2pkh_addr.to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG'])

    # accept a P2SH address to get the funds from
    addr = P2shAddress.from_script(redeem_script)
    print("The P2SH address is : " + addr.to_string())
    
    
    #check if the P2SH address has any UTXOs to get funds from
    
    
    
    
    # accept a P2PKH address to send the funds to
    to_addr = P2pkhAddress(send_address)
    
    #amount = int( ( Decimal(str(btc_to_send)) - Decimal(str(fee)) ) * 100000000 )
    
    txout = TxOutput(to_satoshis(11), to_addr.to_script_pub_key())
    
    # create transaction from inputs/outputs
    tx = Transaction([txin], [txout])
    
    # display the raw unsigned transaction
    print("\nRaw unsigned transaction:\n" + tx.serialize())
    
    # use the private key corresponding to the address that contains the
    # UTXO we are trying to spend to create the signature for the txin -
    # note that the redeem script is passed to replace the scriptSig
    sig = p2pkh_sk.sign_input(tx, 0, redeem_script )
    print(sig)
    
    # set the scriptSig (unlocking script) -- unlock the P2PKH (sig, pk) plus
    # the redeem script, since it is a P2SH
    txin.script_sig = Script([sig, p2pkh_pk.to_hex(), redeem_script.to_hex()])
    signed_tx = tx.serialize()
    
    # display the raw signed transaction, ready to be broadcasted
    print("\nRaw signed transaction:\n" + signed_tx)
    
    # display the transaction id
    print("\nTxId:", tx.get_txid())
    
if __name__ == "__main__" :
    main()
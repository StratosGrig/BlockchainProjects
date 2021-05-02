from bitcoinutils.setup import setup
from bitcoinutils.transactions import Locktime
from bitcoinutils.keys import P2shAddress, PublicKey
from bitcoinutils.script import Script
from bitcoinutils.constants import TYPE_ABSOLUTE_TIMELOCK
import argparse


def main():
    # always remember to setup the network
    setup('regtest')

    #
    # This script creates a P2SH address containing a CHECKLOCKTIMEVERIFY plus
    # a P2PKH locking funds with a key as well as for an absolute amount of blocks or an absolute amount of seconds since the transaction.
    #

    parser = argparse.ArgumentParser(description='Give the public key, a future time expressed either in block height or in UNIX Epoch time and the P2SH address will be displayed')
    parser.add_argument('pubkey', help="Add the public key.")
    parser.add_argument('-param', type= int, help = "Add the number of blocks or the time expressed in seconds.")
    args = parser.parse_args()
    
    key = args.pubkey 
    absolute_param = args.param
    
    p2pkh_pk = PublicKey(key)
        
    locktime = Locktime(absolute_param)

    # get the address (from the public key)
    p2pkh_addr = p2pkh_pk.get_address()
    
    #print("Public key: " + p2pkh_pk.to_hex(compressed=True))
    #print("P2PKH Address: " + p2pkh_addr.to_string())

    # create the redeem script
    redeem_script = Script([absolute_param, 'OP_CHECKLOCKTIMEVERIFY', 'OP_DROP', 'OP_DUP', 'OP_HASH160', p2pkh_addr.to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG'])

    # create a P2SH address from a redeem script
    addr = P2shAddress.from_script(redeem_script)
    print("The P2SH address is : " + addr.to_string())
    


if __name__ == "__main__":
    main()
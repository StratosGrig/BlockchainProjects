from bitcoinutils.setup import setup
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, Sequence
from bitcoinutils.keys import P2pkhAddress, P2shAddress, PrivateKey
from bitcoinutils.script import Script
from bitcoinutils.constants import TYPE_RELATIVE_TIMELOCK
import argparse


def main():
    # always remember to setup the network
    setup('regtest')

    #
    # This script creates a P2SH address containing a CHECKSEQUENCEVERIFY plus
    # a P2PKH locking funds with a key as well as for a relative amount of blocks or a relative amount of seconds since the transaction.
    #

    parser = argparse.ArgumentParser(description='Give the public key, a future time expressed either in block height or in UNIX Epoch time and the P2SH address will be displayed')
    parser.add_argument('pubkey', help="Add the public key.")
    parser.add_argument('-param', type= int, help = "Add the number of blocks or the time expressed in seconds.")
    parser.add_argument('-whattype',default = True, type=lambda x: (str(x).lower() == 'true'), help = " True for Block, False for Time")
    args = parser.parse_args()
    
    
    public_key = args.pubkey 
    relative_blocks = args.param
    is_type_block = args.whattype
        
    #print(public_key)
    #print(relative_blocks)
    #print(is_type_block)
    
    seq = Sequence(TYPE_RELATIVE_TIMELOCK, relative_blocks, is_type_block )


    # secret key corresponding to the pubkey needed for the P2SH (P2PKH) transaction
    p2pkh_sk = PrivateKey(public_key)

    # get the address (from the public key)
    p2pkh_addr = p2pkh_sk.get_public_key().get_address()

    # create the redeem script
    redeem_script = Script([seq.for_script(), 'OP_CHECKSEQUENCEVERIFY', 'OP_DROP', 'OP_DUP', 'OP_HASH160', p2pkh_addr.to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG'])

    # create a P2SH address from a redeem script
    addr = P2shAddress.from_script(redeem_script)
    print("The P2SH address is : " + addr.to_string())

if __name__ == "__main__":
    main()
from bitcoinutils.setup import setup
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, Locktime
from bitcoinutils.keys import P2pkhAddress, P2shAddress, PrivateKey
from bitcoinutils.script import Script
from bitcoinutils.constants import TYPE_ABSOLUTE_TIMELOCK
from bitcoinutils.proxy import NodeProxy
import argparse
from decimal import Decimal
from binascii import hexlify, unhexlify
from bitcoinutils.constants import SATOSHIS_PER_BITCOIN
import requests
import json


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

    parser = argparse.ArgumentParser(description='Give the private key, a future time expressed either in block height or in UNIX Epoch time and the P2SH address to send the funds')
    parser.add_argument('key', help="Add the private key.")
    parser.add_argument('-param', type= int, help = "Add the number of blocks or the time expressed in seconds.")
    parser.add_argument('-to_address', type= str , help="Add the adress that will sent/spend")
    args = parser.parse_args()
        
    # set values
    key = args.key 
    absolute_param = args.param
    send_address = args.to_address
        
    #set Locktime    
    locktime = Locktime(absolute_param)
        
    #set proxy
    username = 
    password = 
    proxy = NodeProxy(username, password).get_proxy()

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
    print("The P2SH address to get the funds from is : " + addr.to_string())
    
    
    #check if the P2SH address has any UTXOs to get funds from
    minconf = 0 
    maxconf = 9999999
    list = proxy.listunspent(minconf,maxconf,"[\"addr\"]")
    
    #calculate the amount of bitcoins to send
    btc_to_send = sum(map(lambda x: int(x['amount']), json.loads(list)))
    
    
    # accept a P2PKH address to send the funds to
    to_addr = P2pkhAddress(send_address)
    print("The P2PKH address to send the funds to is : " + to_addr.to_string())
    
    # calculate the appropriate fees with respect to the size of the transaction
    response = requests.get("https://mempool.space/api/v1/fees/recommended")
    fee = response.json()['fastestFee']
    print("Fastest fee per byte is : %d " %fee)
      
    #send all funds that the P2SH address received to the P2PKH address provided  
    
    my_list = json.loads(list)
    txin = []
    for i in (my_list) : 
        x = TxInput(i['txid'], i['vout'], sequence= locktime.for_transaction())
        txin.append(x)    

    amount = btc_to_send - fee
    txout = TxOutput(to_satoshis(amount), to_addr.to_script_pub_key())
    
    tx = Transaction([txin], [txout])
    
    # display the raw unsigned transaction
    print("\nRaw unsigned transaction:\n" + tx.serialize())
    
    # sign the transaction
    sig = p2pkh_sk.sign_input(tx, 0, redeem_script )
    #print(sig)
    
    # set the scriptSig (unlocking script) -- unlock the P2PKH (sig, pk) plus
    # the redeem script, since it is a P2SH
    txin.script_sig = Script([sig, p2pkh_pk.to_hex(), redeem_script.to_hex()])
    signed_tx = tx.serialize()
    
    # display the raw signed transaction, ready to be broadcasted
    print("\nRaw signed transaction:\n" + signed_tx)
    
    # display the transaction id
    print("\nTxId:", tx.get_txid())
   
   # verify that the transaction is valid and will be accepted by the Bitcoin nodes
   # if the transaction is valid, send it to the blockchain
    
   current_block = proxy.getblockcount()
   current_block_hash = proxy.getblockhash(current_block)
   current_block_info = proxy.getblock(current_block_hash, 1)
   
   info = json.loads(current_block_info)
   if (info['confirmations'] > absolute_param):
        print("Sending transaction to blockchain")
        proxy.sendrawtransaction(signed_tx)   
   else: 
      print("Transaction is not valid")
   
    
if __name__ == "__main__" :
    main()
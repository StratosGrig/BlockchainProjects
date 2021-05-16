===========================

Task 1

For the first task you need to input the following arguments :

1) pubkey ( public key)
2) -param ( a future time expressed either in block height or in UNIX Epoch time)

For example you can run the first script in CMD: python Bitcoin_Task1.py 03a2fef1829e0742b89c218c51898d9e7cb9d51201ba2bf9d9e9214ebb6af32708 -param 2000

It is expected to return the P2SH address.

===========================

Task 2

For the second task you should input the following arguments :

1) privkey (private key)
2) -param  ( a future time expressed either in block height or in UNIX Epoch time)
3) -to_address ( P2PKH address to send the funds to) 

For example you can run the second script in CMD : python Bitcoin_Task2.py cRvyLwCPLU88jsyj94L7iJjQX5C2f8koG4G2gevN4BeSGcEvfKe9 -param 2000 -to_address n4bkvTyU1dVdzsrhWBqBw8fEMbHjJvtmJR

For this script to run, you need to:  
1) have a bitcoin node running and input the username, password at line 47-48.
2) have already sent some BTC to the P2SH address 




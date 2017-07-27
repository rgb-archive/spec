<pre>
BIP: ?
Layer: Applications
Title: RGB
Author: 
Discussions-To: 
Comments-Summary: 
Comments-URI: 
Status: Draft
Type: Process
Created: 2017-07-25
License: 
License-Code: 
Post-History: 
Requires: 
Replaces: 
Superseded-By: 
</pre>

### Questions List

TODO: what about the scripting language? how will the engine work? <br> 
TODO: dust limit in case of on-chain transactions? <br> OK enforce in contract
TODO: bip32 says that hardned keys can be derived from thr parent PRIVATE KEY not public. What about it? <br> public key
TODO: how can the index be derived from the k? otherwise the colored asset can be the one always after/before the `Issuer_Fees` output (this way the confidentiality is reduced). <br> nsequence byte to define the output index of color/change
TODO: how difficult is to bruteforce every k? <br> we use 2 derivation
TODO: Which proof Alice show to Bob? <br> ? 
TODO: atomic swap? how? hash time-locked contract ? <br>

PROBLEMS: Asset is in satoshi / Fee is almost recognizable due to contract / change probably most of the time bigger than asset <br> :'(
PROBLEMS: Input BTC history is different from Asset history <br> :'(
PROBLEMS: Multi asset ? shouldn't be a problem if the asset output position is derived by the K, but what about the change? nsequence 

## Abstract

## Motivation

## Specification

### Data structures
The system is based on 2 type of transactions called issuing and transfer. The first, also called genesis transaction, is used by the issuer to emit an asset to another party. The structure is the following:

<pre>
+--------------------------------------------------+
|            Tx Hash                               |
+---------------+----------------------------------+
|   Input       |  Output                          |
+---------------+----------------------------------+               
| • Color_Input | • Color_Output                   |
|               | • OP_RETURN pointing to contract |
+---------------+----------------------------------+
</pre>

* The `Color_Input` address is contained as a field in the contract followed by a digital signature. 
* The `Color_Output` address is given by the payee to the issuer. 
* The `OP_RETURN` contains an indentifier of the contract which can be issuer in different ways:
	* `hash256` pointing to a file in a IPFS distributed network
	* < link_id:hash256 > where `link_id` is the identifier of a pastebin/gist public file and `hash256` is the content hash

Instead, the second type of transactions is used to exchange a specific asset between 2 parties. The structure is the following:

<pre>
+---------------------------------+
|            Tx Hash              |
+---------------+-----------------+
|   Input       |  Output         |
+---------------+-----------------+              
| • Color_Input | • Color_Output  |
| • BTC_Input   | • Issuer_Fees   |
|               | • Change_Output |
+---------------+-----------------+
</pre>

* `Color_Input` is a valid colored input (will explain later how a user can be user of the validity of a colored input).
* `BTC_Input` contains an amount of BTC to pay asset's fee to the issuer.
* `Color_Output` contains the amount of asset exchanged between the two parties.
* `Issuer_Fees` contains the amount of BTC w.r.t the contract released by the issuer for that specific asset.
* `Change_Output` is a partially colored output which contains the sum of changes from the `Color_Input` and `BTC_Input`.

### Contract
When a issuer emit a share of an asset, he must also release a public contract of the following structure: <br>
<pre>
{
	"title": String,
	"issuer": {
		"pubkey": String,
		"signature": String,
		"master_pubkey" : String
	},
	"dust_limit": Integer,
	"divisibility": Float,
	"redeeming" : Array of possible reediming action,
	"rules": < Rule engine code describing the asset behavior >
}
</pre>

Each user will be able to check if the colored transaction he is going to pay for, obeys to the issuer's contract conditions. <br>
In order to increase the confidentiality against a possibile data mining attack, the fee given to the issuer are based on the K exchanged between the 2 user. Without knowing the K its impossible to deduct which of the 3 or more output is the one containing the fee and tagging the color of the transaction.

### Validation
Everytime before an asset exchange, the payee has to give to the payer 2 addresses: the first will contain the amount of colored asset meanwhile the second will be used to send the fee for the issuer as specified in the contract. The latter is also used as a unique tag to specify the ID/Type of asset. <br>
The second address is generated with 2 `K` keys derivation from, the first time, the public key (described in the contract) of the issuer (which can be found in the contract) the other times from the last generated pubkey.<br>
The list of `K` is passed from user to user. <br>
The  purpouse of the list is dual:

* everyone who has the list of Ks is able to recontruct the history of the asset and validate if the payer has a colored output which come from an asset emitted by the issuer.
* everyone is able to identify the amount of colored coin in the `Change_Output` which is the difference between `Color_Input` and `Color_Output`.
* a user can generate from the last pubkey the following pubkey.

In order to find which is the `Color_Output` and which is `Change_Output`, the output index of the `Color_Output` can be computed with the K relative to that transaction `mod` a number which is described in the nsequence left-most 3 byte.
Every byte contains two 4 bit number. The first par contains the number to indentify the index of the `Change_Output` meanwhile the second the `Color_Output`.

Then, in order to differenciate the total of colored asset from the BTC amount, we can just subtract from the `Change_Output` the difference between the `Color_Input` and the `Color_Output`. 

### Process
The following schema describe how the protocol works:

* Olivia (the issuer) publicly release the contract for an asset.
<pre>
GOLD - Olivia - Contract
</pre>
* Alice gives to the issuer an address which is used by the issuer to generate a issuing/genesis transaction.
<pre>
+-----------------------------------------------------+
|                     Tx Hash                         |
+-------------------------+---------------------------+
|   Input                 |  Output                   |
+-------------------------+---------------------------+
| • Olivia PubKey (Asset) | • Alice PubKey (Asset)    |
+-------------------------+---------------------------+
</pre>
Olivia PubKey is defined in the contract.
* Now Bob wants a share of that asset from Alice. Alice gives Bob the list of Ks, the genesis transaction and the contract ( the first time the list of Ks will be empty). Bob will generate 2 `K` keys derivation, with which will create an address, and a another address from his own extended public key. After sending those 2 address to Alice, she will create a transaction as the following:
<pre>
+-----------------------------------------------------------+
|                     Tx Hash                               |
+-------------------------+---------------------------------+
|   Input                 |  Output                         |
+-------------------------+---------------------------------+
| • Alice PubKey (Asset)  | • Bob PubKey (Asset)            |
| • Alice BTC (Fees)      | • Issuer Fees (Bob's k derived) |
|                         | • Change (Partial colored)      |
+-------------------------+---------------------------------+
</pre>
* Now also eve wants a share of that asset from Bob. First Bob send her the list of K's from which Eve can derive and validate the history of the asset and check if the contract's rule have been respected.If Bob's asset is valid, then she gives to Bob two new addresses,one will be used to send the fee to the issuer as per contract, the other to send to Eve the asse. Bob will construct a transaction like the following:
<pre>
+-----------------------------------------------------------+
|                      Tx Hash                              |
+-------------------------+---------------------------------+
|   Input                 |  Output                         |
+-------------------------+---------------------------------+
| • Bob PubKey (Asset)    | • Eve PubKey (Asset)            |
| • Bob BTC (Fees)        | • Issuer Fees (Eve's k derived) |
|                         | • Change (Partial colored)      |
+-------------------------+---------------------------------+
</pre>
* Now Eve, wants to redeem his asset by sending it to the issuer. She gives to the issuer the list of K's and the asset and by levegering the exchange with an atomic transaction, the issuer will first verify the validity of the asset history with respect to the Ks and the contract. He will then provide the respecting redeeming action as per contract.

### Confidentiality consideration

Confidentiality is archived by:
* Randomly generating an amount of fees based on the randomly generated K decrease the possibility of information disclosure by data mining based on the contract description.
* Amount disclosure is hidden between N outputs, with N > 3. A user can increase his privacy by:
	* Sending an asset to himself
	* Increasing the number of input and output
* The issuer can't follow the path of his asset until someone makes a redeem.
## Rationale

## Compatibility

## Reference implementation

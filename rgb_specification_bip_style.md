<pre>
	BIP: ?
	Layer: Applications
	Title: Colored Coin
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

TODO: how will the engine work? what about the scripting language? <br>
TODO: dust limit in case of on-band transactions? <br>
TODO: bip32 says that hardned keys can be derived from thr parent PRIVATE KEY not public. What about it? <br>
TODO: how can the index be derived from the k? otherwise the colored asset can be the one always after/before the `Issuer_Fees` output (this way the confidentiality is reduced). <br>
TODO: how difficult is to bruteforce every k? <br>
TODO: Which proof Alice show to Bob? <br>
TODO: atomic swap? how? <br>

--

PROBLEMS: Asset is in satoshi / Fee is almost recognizable due to contract / 

##Abstract

##Motivation

##Specification

###Data structures
The system is based on 2 type of transactions called issuing and transfer. The first one can be considered a genesis transaction used by the issuer to emit an asset to another party. The structure is the following:

<pre>
+--------------------------------+
|                 Tx Hash        |
+---------------+----------------+
|   Input       |  Output        |
+---------------+----------------+               
| • Color_Input | • Color_Output |
+---------------+----------------+
</pre>

* The `Color_Input` address is contained as a field in the contract followed by a digital signature. 
* The `Color_Output` address is given by the payee to the issuer. 

Instead, the second type of transactions is used to exchange a specific asset between 2 parties. The structure is the following:

<pre>
+---------------------------------+
|                 Tx Hash         |
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
	"divisibility": Float,
	"rules": < Rule engine code describing the asset behavior >
}
</pre>

Each user will be able to check if the colored transaction he is going to pay for, obeys to the issuer's contract conditions. <br>
In order to increase the confidentiality against a possibile data mining attack, the fee given to the issuer are based on the K exchanged between the 2 user. Without knowing the K its impossible to deduct which of the 3 or more output is the one containing the fee and tagging the color of the transaction.

### Validation
Everytime before an asset exchange, the payee has to give to the payer 2 addresses: the first will contain the amount of colored asset meanwhile the second will be used to store the fee for the issuer as specified in the contract. The latter is also used as a unique tag to specify the ID/Type of asset. <br>
Those 2 addresses are generated with a `K` key derivation from the master extended public keym, as per BIP32m of the issuer (which can be found in the contract) to pay for the asset fees. <br>
The list of `K` is passed from user to user. <br>
The  purpouse of the list is dual:

* everyone who has the list of Ks is able to recontruct the history of the asset and validate if the payer has a colored output which come from an asset emitted by the issuer.
* everyone is able to identify the amount of colored coin in the `Change_Output` which is the difference between `Color_Input` and `Color_Output`.

In order to find which is the `Color_Output` from the `Change_Output`, the position of the `Color_Output` can be identified by the output index which can be computed from the K.

### Process
The following schema describe how the protocol works:

* Olivia (the issuer) publicly release the contract for an asset.
<pre>
	GOLD - Olivia - Contract
</pre>
* Alice gives to the issuer an address which is used by the issuer to generate a issuing transaction.
<pre>
+-----------------------------------------------------+
|                         Tx Hash                     |
+-------------------------+---------------------------+
|   Input                 |  Output                   |
+-------------------------+---------------------------+
| • Olivia PubKey (Asset) | • Alice PubKey (Asset)    |
+-------------------------+---------------------------+
</pre>
Olivia PubKey is defined in the contract.
* Now Bob wants a share of that asset from Alice. 
<pre>
+-----------------------------------------------------------+
|                         Tx Hash                           |
+-------------------------+---------------------------------+
|   Input                 |  Output                         |
+-------------------------+---------------------------------+
| • Alice PubKey (Asset)  | • Bob PubKey (Asset)            |
| • Alice BTC (Fees)      | • Issuer Fees (Bob's k derived) |
|                         | • Change (Partial color)        |
+-------------------------+---------------------------------+
</pre>
* Now also eve wants a share of that asset from Bob. First Bob send her the list of K's from which Eve can derive and validate the history of the asset and check if the contract's rule have been respected.If Bob's asset is valid, then she gives to Bob a new K, which will be used from bob to derive an address with the extended master public key of the issuer, and an address. Bob will construct a transaction like the following:
* <pre>
+-----------------------------------------------------------+
|                         Tx Hash                           |
+-------------------------+---------------------------------+
|   Input                 |  Output                         |
+-------------------------+---------------------------------+
| • Bob PubKey (Asset)    | • Eve PubKey (Asset)            |
| • Bob BTC (Fees)        | • Issuer Fees (Eve's k derived) |
|                         | • Change (Partial color)        |
+-------------------------+---------------------------------+
</pre>
* Now Eve, wants to redeem his asset by sending it to the issuer. She gives to the issuer the list of K's and the asset and by levegering the exchange with an atomic transaction, the issuer will first verify the validity of the asset history with respect to the Ks and the contract. He will then provide the reediming.

##Rationale

##Compatibility

##Reference implementation
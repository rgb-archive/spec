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
| • Color_Input | • P2PKH Color_Output             |
|               | • P2PKH BTC_Change               |
|               | • OP_RETURN Contract_Hash        |
+---------------+----------------------------------+
</pre>

* The `Color_Input` address is contained as a field in the contract followed by a digital signature.
* The `Color_Output` address is given by the payee to the issuer. Contain the total issued asset which is the same number as the satoshi value of the output.
* `BTC_Change` is the bitcoin change
* The `OP_RETURN` contains an indentifier of the contract which can be issuer in different ways:
	* `sha256` of the contract which content is distributed with a yet-to-specify mechanism
	* `IPFS-hash` pointing to a file in a IPFS distributed network
	* < link_id:hash256 > where `link_id` is the identifier of a pastebin/gist public file and `hash256` is the content hash


The second type of transactions is used to exchange a specific asset between 2 or more parties. The base structure is the following:

<pre>
+---------------------------------------+
|            Tx Hash                    |
+---------------+-----------------------+
|   Input       |  Output               |
+---------------+-----------------------+              
| • Color_Input | • P2PKH Color_Output  |
| • BTC_Input   | • P2PKH Issuer_Fees   |
|               | • P2PKH Change_Output |
|               | • OP_RETURN Color_Def |
+---------------+-----------------------+
</pre>

* Inputs
	* `Color_Input` is a valid colored input (will explain later how a user can be user of the validity of a colored input). There could be another colored input
	* `BTC_Input` contains an amount of BTC to pay asset's fee to the issuer. There could be any number of btc input.
* Outputs (the order is irrelevant)
	* `Color_Output` contains the amount of asset exchanged between the two parties. (the satoshi amount is mapped 1:1 to the number of asset shares). There could other 4 colored output
	* `Issuer_Fees` contains the amount of BTC required by the contract released by the issuer for that specific asset.
	* `Change_Output` is a partially colored output which mixes bitcoin and number of asset shares
	* `Color_Def` contains 32 encrypted byte defining the transaction.

### Process

Everytime before an asset exchange, the payee has to give the payer an address where he want to get paid, an amount and a tagging value.
The tagging value is used to tag the transaction in a way only the partecipants of the trade know the details of the transaction (such the asset type of the transaction)

Supposing we have an issuance of an asset and two transaction

```
Issuance -> Transaction A to Alice with tagging value J -> Transaction B to Bob with tagging value K
```

Bob give to alice a random tagging value `K` of twelve bytes.
Alice take the tagging value `K` and split in 3 chunk of 4 bytes `K1`, `K2`, `K3`
Alice take the xpub of the issuer and derive the `Issuer_Fee` address as `xpub/J1/J2/J3/K1/K2/K3`
Alice put in the `Color_Def` his value `J` encrypted with the value `K` (for example xor-ed).
When Bob receive the transaction he decrypt the `Color_Def` (inside the OP_RETURN) with `K` and find `J`. Bob then retrieve transaction A where decrypt the `Color_Def` with `J` to find the previous tagging value, in this case the previous is the issuing transaction otherwise he repeat the step until he found the issuing transaction. Now Bob can verify his transaction and all the chain to the issuance are adherent to the protocol.

The process of retrieving transaction to verify the issuer chain become soon too expensive on light client, the best way to achieve this is probably client side filtering [reference to neutrino], while this solution is not in place an "electrum server" like solution could be implemented (which is suboptimal for privacy)

To be more specific the `Color_Def` is an OP_RETURN output of exactly 32 bytes (we choose a fixed size to avoid leaking privacy based on the field size, moreover 32 is a common size because it's the size of sha256)

position | size | description
--- | --- | ---
0-1 | 1 byte | RGB Version
1-2 | 1 byte | Position of the first colored input (from 0 to 254)
2-14 | 12 byte | Tagging value of the previous output of the first colored input
14-15 | 1 byte | Position of the second colored input, if any, otherwise 0xff
15-27 | 12 byte | the tagging value of the previous output of the second colored input , otherwise 0xffffffffffffffffffffffff
27-28 | 1 byte | define the position of the first colored ouptut (which is partially colored)
29-32 | 1 byte each | define the position of the second, third, 4th and 5th colored ouptut if any or 0xff

Tx with more than two colored input or more than 6 colored output are not allowed (one must build more than one tx to merge more than two inputs)

Since one could easily mark the colored inputs/outputs if the input amount is the sum of two outputs amount, one output is partially colored, meaning the number of asset shares is less than the number of satoshi of this output. The exact number of asset share could be computed as `color_value(BTC_Input)-Color_output` since they are exact value. This comes handy because the payer could use this to get back the bitcoin change without creating another output.

To avoid transaction tracking based on the amount of the `Issuer_Fee` this value must be randomized in the less signifcant part, for example based on `K` and `J`

### Contract

When a issuer emit a share of an asset, he must also release a public contract with the following structure: <br>
<pre>
{
	"version": Integer  # RGB version
	"title": String,
	"issuer": {
		"pubkey": String,
		"signature": String,
		"master_pubkey" : String
	},
	"dust_limit": Integer,
	"divisibility": Float,
	"redeeming" : Array of possible reediming action,
	"rules": < Rule engine code describing the asset behavior >  ## RULES TO BE DEFINED
}
</pre>

Each user will be able to check if the colored transaction he is going to pay for, obeys to the issuer's contract conditions.

In order to increase the confidentiality against a possibile data mining attack, the fee given to the issuer are based on the K exchanged between the 2 user. Without knowing the K its impossible to deduct which of the 3 or more output is the one containing the fee and tagging the color of the transaction.

Issuer is not collecting fees of an entire path until someone redeem the asset, in that moment the issuer discover all the tagging values and can collect the fees. To overcome this problem issuer could define some rules to incentivize redeeming after N transactions (this would also allow to keep path not too long).

### Known issue

The dust limit of the amount prevent sending low value of shares. One could consider to send 1000 shares as minimum but this could change in the future, a split/join mechanism which does not require reissuance of all tokens should be defined to properly handle dust limit.

## Rationale

## Compatibility

## Reference implementation

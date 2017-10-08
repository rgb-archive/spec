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

The RGB protocol aims to develop a better way to exchange generic assets by making confidentiality and interoperability with the existing Bitcoin ecosystem a priority.

### Confidentiality
While a centralized and trust-based solution for digital assets encumbers its users to privacy concerns, and the issuer to extreme regulatory burden (KYC, AML, privacy laws, asset-specific regulations and authorizations, ecc.), some of these costs could be lowered in the framework of a technical (total or partial) impossibility, for the issuer, to view, track, prevent, censor or revert asset transactions. This feature would not just be an advantage for some kind of users in terms of privacy, but also a responsibility relief for the asset issuer itself. Of course, this advantage would be of paramount importance for informal, unregulated or borderline issuers, but also for regulated legal entities the implications could be of interest, even if for them it would come at cost of possible increases of reputational and regulatory risk.

In order to archive the confidentiality levels needed we developed a unique way for tagging the colored asset such that RGB transactions are indistinguishable from normal transactions for any party running forensic analytics on Bitcoin blockchain or on its network, thus making the RGB protocol different to other existing colored coin protocols.
This protocol focuses on the asset history confidentiality. It differs from existing colored coin protocols in that it exploits the mere presence of an output address to identify a colored transaction and verify its integrity, rather than using order, padding order or any other version based on the index position of the outputs. The key to achieve the desired level of privacy is that the colored transaction can’t be decoded by anyone else except by the two parties involved in the transaction.


### Interoperability
While a centralized and proprietary solution for digital assets is difficult to push and needs to be marketed, an open source de-facto standard could be leveraged to lower friction to adoption. If a public blockchain-based system reached mainstream adoption due to its inner value proposition (native asset transfer), then also generic digital assets could be issued on the same platform, leveraging wallets, light clients, markets, libraries, block explorers, APIs, regulatory framework, secure hardware, user habits, ecc. The fewer the customizations necessary, the more frictionless the process. This advantage comes at the typical cost related with open ecosystems: difficult to lock-in users.

### Auditability
While a centralized and trust-based solution for digital assets would allow the issuer to modify the ledger in every possible way, inflating the supply, changing the distribution, blacklisting amounts and users, changing the transaction history, blockchain technology could be used (given certain condition) to provide solid proofs of correct, fair and deterministic behaviour. The amount of issued assets, the reserve, the immutability of the history of the ledger, could be proved cryptographically and independently audited leveraging blockchain technologies in a correct way. While it is still unclear if these auditability properties could represent a strong value proposition toward final users (at least in the case of a regulated business, where social, reputational and legal guarantees of fairness are usually valued more than technological ones), they could be interesting for regulators.

### Programmability
The RGB protocol will have its own scripting language giving the possibility to the asset issuers to create functions to describe the behavior against which the token transfers will have to adhere, and it will not be Turing complete, so as to avoid output unpredictability and undefined code behaviors.

In conjunction with the scripting language, there is also a validation system which checks if the asset history is valid against the rules described in the contract script. 
Finally the issuer will attach a human readable contract to each and every RGB colored coin. Such note will make it explicit what the asset bearer will be entitled with when redeeming the asset from the issuer. 
This contract will be digitally signed by the issuer, timestamped and committed to the issuing transaction and it will be passed along by every user to the next and it will be stored – together with the necessary proofs, the digital signature and the timestamp proof – by every user.

The RGB scripting language will be versioned and its first version will grant the validation rules to pass along the digital assets between users on the secondary market. The subsequent versions not only they will grant that the digital asset has always been transferred correctly by all users in each and every transaction, but also that the transaction respected a set of more complex conditions granting the ultimate redeemability of the asset. Examples of such rules could be a fee proportional to the amount of asset being transferred, or the block height, to be attached in each transaction and destined to the asset issuer in order for the asset to be finally redeemable. This conservative approach will grant safety and usability of the protocol for transferring the assets from day one, while additional features needing additional testing and validation will be easily introduced without breaking backward compatibility.

## Specification

### Data structures

The system is based on 2 types of transactions called issuing and transfer. The first – also called genesis transaction – is used by the issuer to emit an asset to another party. The structure is the following:

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

* The `Color_Input` address is contained as a field in the [contract](#contract) followed by a digital signature.
* The `Color_Output` address is given by the payee to the issuer. It contains the total issued assets which corresponds to the number of satoshis of the output.
* `BTC_Change` is the bitcoin change
* The `OP_RETURN` contains an indentifier of the [contract](#contract). This can be issued in different ways:
	* `sha256` of the contract whose content is distributed with a yet-to-specify mechanism,
	* `IPFS-hash` pointing to a file in an IPFS distributed network,
	* < link_id:hash256 > where `link_id` is the identifier of a pastebin/gist public file and `hash256` is the content hash.


The second type of transactions is the transfer trasaction. It is used to exchange a specific asset between 2 or more parties. The base structure is the following:

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
	* `Color_Input` is a valid colored input (we will explain [later](#process) how a user can verify the validity of a colored input). There could be another colored input
	* `BTC_Input` contains an amount of BTC to pay an asset-transfer fee to the issuer through the `Issuer_Fees` output. There could be any number of bitcoins in input.
* Outputs (the order is irrelevant)
	* `Color_Output` contains the amount of asset exchanged between the two parties (the satoshi amount is mapped 1:1 to the number of asset shares). There can be up to 4 additional colored outputs,
	* `Issuer_Fees` contains the amount of BTC as required within the [contract](#contract) released by the issuer for that specific asset.
	* `Change_Output` is a partially colored output which mixes bitcoin and number of asset shares
	* `Color_Def` contains 32 Bytes encrypted. These Bytes define the transaction.

### Process

Every time before an asset exchange, the payee provides the payer with an **address** where he wants to be paid, an **amount** and a **tagging value**.
The tagging value is used to tag the transaction in a way such that only the partecipants of the trade know the details of the transaction (i.e. details regarding the asset type of the transaction).

Supposing we have an issuance of an asset and two transactions

```
Issuance -> Transaction A to Alice with tagging value J -> Transaction B to Bob with tagging value K
```

1. Bob gives to Alice a random tagging value `K` of twelve Bytes,
2. Alice takes the tagging value `K` given by bob and splits it into 3 chunks of 4 Bytes `K1`, `K2`, `K3`. Then takes her own tagging value `J` and splits it into 3 chunks as well `J1`, `J2`, `J3`. 
3. Alice takes the xpub of the issuer and derives the `Issuer_Fee` address as `xpub/J1/J2/J3/K1/K2/K3` (When deriving the most significant bit of every chunk is set to `0` because the `1` it's reserved for hardened derivation)
4. Alice puts her tagging value `J` into the `Color_Def`, symmetrically encrypts the `Color_Def` with Bob's tagging value `K` and broadcasts transaction B.
5. When Bob receives the transaction B he decrypts the `Color_Def` (inside the OP_RETURN) with `K` and finds `J`. 
6. Bob then retrieves the previous transaction A where decrypts the `Color_Def` output with `J` to find the previous tagging value, in this case the previous is the issuing transaction otherwise he repeats the step until he finds the issuing transaction. 
7. Now Bob can verify his transaction and all the chain to the issuance are adherent to the protocol.

The process of retrieving transactions to verify the chain all the way up to the issuing transaction becomes very soon too expensive on light clients. The best way to achieve this is probably [client side filtering](https://github.com/lightninglabs/neutrino), but while this solution is not operational an "electrum server"-like solution could be implemented (which is suboptimal for privacy).

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

Transactions with more than two colored inputs or more than 6 colored outputs are not allowed (one must build more than one tx to merge more than two inputs)

Since one could easily mark the colored inputs/outputs if the input amount is the sum of two outputs amount, one output the `Change_Output` is partially colored, meaning that the number of asset shares is less than the number of satoshi of this output. The exact number of asset share can be computed as `color_value(BTC_Input)-Color_output` since they are exact value. This comes handy because the payer could use this to get back the bitcoin change without creating another output.

To avoid transaction tracking based on the amount of the `Issuer_Fee` this value must be randomized in the less signifcant part, for example based on `K` and `J`.

### Contract

When an issuer emits a share of an asset, he must also release a public contract with the following structure: <br>
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

Each user will be able to check if the colored transaction he is going to pay for obeys to the issuer's contract conditions.

In order to increase the confidentiality against a possibile data mining attack, the fee given to the issuer are based on the `K` exchanged between the 2 user. Without knowing the `K` its impossible to infer which of the 3 (or more) outputs is the one containing the fee and the one tagging the color of the transaction.

The issuer is not collecting fees of an entire path until someone redeems the asset, in that moment the issuer discovers all the tagging values and can collect the fees. To overcome this problem the issuer could define some rules to incentivize redeeming after *N* transactions (this would also allow to limit the path).

### Known issue

The dust limit of the amount prevents sending few shares. One could consider to send 1000 shares as minimum but this could change in the future, a split/join mechanism which does not require reissuance of all tokens should be defined to properly handle dust limit.

## Rationale

## Compatibility

## Reference implementation

## Future Developments and Improvements

### Lightning Network integration for Decentralized Atomic Swaps
Of primary concern is out of the box integration with Lightning Network.
In fact, Lightning Network offers several benefits, such as the possibility to transfer funds even when the network is congested, increased privacy by avoiding to publish the whole history of the asset and more economic and faster transaction, with fees and confirmation time near to null. 
Not only this but also Lightning Network could be heavily exploited for the development of a Decentralized Exchange, thus giving the possibility to RGB users to transfer generic assets in a safer and more confidential environment.  

By levegering the Lightning Network, we could get rid of counterparty risk – through commit-or-refund schema – and of bureaucratic procedures – such as KYC or AML, which would weaken users confidentiality. Instead everything would exploit off-chain transactions, in a peer-to-peer decentralized environment.

One of the biggest and most underrated problems of the existing exchange platforms is that fact that users need to trust their counterparty (exchange operators), giving them full control of their own goods. Counterparty risks, even when dealing with generally reliable and trusted parties, have always to be taken into consideration since casualties are always behind the door. 

Lightning Network indirectly brings others important features, improving both security, censorship resistance and privacy. In fact, Lightning transactions are based on commit-or-refund schema hence they are atomic by default, meaning that either the exchange of funds is executed or you are refunded with your money back. There is no way for a counterparty to either steal your money or even block it for an undefined amount of time.

The objective of the next RGB protocol improvement is to:
* on one hand take care of the opening and management of a lightning channel with a specific asset, while giving the user full control over the configuration of the exchange rates he is willing to offer,
* on the other hand leverage the route finding algorithm to seek the best exchange rate to perform the asset swap.

This way users owning payment channels containing different assets will be able to atomically swap portions of their channels according to the exchange rate they initially agree to.

### Secure Computing integration to extend Scripting Expressivity
Another important future improvement concerns extending the scripting expressivity of the RGB protocol through Hardware Secure Modules and Trusted Execution Environments. The HSM are hardware tamper-proof trusted computing devices able to run generic scripts such as the ones used to describe the behavior of an asset. The HSM servers will allow to enforce arbitrarily more complex smart contracts directly on Bitcoin blockchain, but they will also serve as hardware oracles, retrieving the data that triggers a smart contract from off-chain outlets. In fact, natively the RGB protocol – just like any other transfer protocol on a blockchain – can make use of data endogenous to its blockchain, therefore very elementary data such as time, fees or amounts. When an issuer wants to program a digital asset to be transferred only when some event happens in the real world, then an oracle is needed in order to trigger the smart contract. This is exactly what an HSM can serve for, thus enabling unimaginable use cases both for issuers and users.

Using such technology, an issuer or the traders exchanging the asset are forced to obey to the contracts terms and the various conditions for the asset transferability, leaving the only option to issuers or to users to partially cheat by breaking the HSM, which will not make them  able to steal anything in any case.

# RGB Protocol Specification V0.20
## Abstract
This document contains the technical specification for the proposed “RGB” protocol for the issuance, the storage and the transfer of blockchain-based digital assets. The protocol aims to provide a standard to perform the aforementioned goal in a way that overcomes the major shortcomings of previous attempts. The protocol is based on Bitcoin, and it’s aimed to provide an acceptable level of scalability, confidentiality, and standardness.
## Motivation
### Digital Assets
There is a continuous and growing interest for digital assets somehow representing a proxy for securities (shares, bonds, deposits, royalties, voting rights, IOUs for physical goods, etc.), utilities (vouchers, coupons, fidelity points, casino tokens, discount rights, presell receipts, payment alternatives, etc.) or collectibles. Traditional ways to issue and transfer assets are usually slow, expensive, inefficient, and present a lot of friction, both technological and regulatory. Nowadays an increasing number of businesses, startups, financial institutions or even individuals are willing to issue digital assets across multiple use-cases.
### Blockchain-based Assets?
While centralized and trust-based models for digital asset management are still, in many cases, the most rational option, there is a growing interest for the application to this problem of the same kind of “blockchain” technology that powers Bitcoin (a purely peer-to-peer, decentralized, trustless, permissionless protocol born to manage the homonym digital commodity). 

Much of this interest is driven by marketing reasons in the context of the current hype cycle, as blockchain-based strategies often result useless (in many digital asset schemes there is already unavoidable need for a central counterparty) and even harmful (a blockchain-based design is usually more expensive, slow, inefficient, and privacy-lacking if compared to centralized existent alternatives, its implementation is usually more complex, challenged by new and not well understood security issues and it requires skills not common in the market, while providing “features” that are often undesirable for business and/or regulatory reasons, like pseudo-anonymity, censorship-resistance, complete openness, etc.). There could be, anyway, some legit reasons to use such a design.
#### Full Decentralization
A first class of reasons could be related to future development of decentralized mechanisms enabling autonomous, trustless, and censorship-resistant enforcement of rights/benefits connected to the assets, in order to extend some the features of Bitcoin to more generic types of digital ownership. Even if this kind of application is still far from actual commercial use, trust-less, automatic, and unstoppable contracts with low to zero counterparty risk are potentially natural candidates for blockchain-based asset schemes. While these ideas are still far from complete, general-purpose, and practical implementations, there are many niche theoretical fields (“smart-property”, “DAOs”, etc.) where they seem promising, and some of these features are achievable by present-day state-of-the-art technologies in some degree.
#### Blindness/Federation
While a full-fledged decentralized, trustless, and permissionless setting is still difficult to imagine for systems beyond Bitcoin itself, some of its interesting features are somehow approximated by settings where the central issuer/enforcer of the digital assets is made, to a certain degree, “blind” to the exact content of its action (“zero knowledge” setups), or when its role is fulfilled by a federation of independent and likely non-colluding entities. That said, both blindness and federation features are achievable with renown, well-established, tested, pre-blockchain technologies (Chaum servers, etc.), which are usually intrinsically easier to bootstrap, upgrade, manage, scale up and use in a privacy-aware context.
#### Auditability
Even in the case of a trusted, non-blind, and centralized counterparty, some advantages could come in the form of enhanced auditability around the actions of the issuer/enforcer. While a traditional architecture would technically allow him to modify the state of the system in every possible way (by inflating the asset supply, changing the distribution, blacklisting amounts and users, editing the transaction history, denying legit redeem claims or forging false ones) without leaving traces, blockchain-related methods could be used to provide solid proofs of correct behaviour. While it is still unclear if these auditability properties could represent a strong value proposition toward final users (at least in the case of a regulated business, where social, reputational, and legal guarantees are usually better received than technological ones), they could be interesting for regulatory compliance. Such properties don’t typically require a “blockchain” architecture per se: traditional systems can just be adapted to leverage the Bitcoin blockchain as an anchor (proof of existence, trustless timestamping, proof of publication, etc.).
#### Standardness
While centralized, closed, proprietary, non-blockchain solutions could already provide sound solutions for many of the problems above (sometimes with less technological friction than blockchain-based alternatives), they are usually difficult to adopt in a wide, consistent, and durable fashion. Open source de-facto standards could be leveraged to lower friction to adoption and to overcome many coordination problems. This is especially true in the case of blockchain-based protocols, where the need for a single, global, consistent, and immutable “source of truth” could reduce degrees of freedom and boost coordination even more. If Bitcoin or similar technologies reached mainstream adoption for their inner value proposition, then also other, more general types of digital assets could easily leverage some of the same infrastructure (standards, libraries, APIs, wallets, marketplaces, block explorers, regulatory frameworks, secure hardware, user habits, best practices, etc.). The fewer the customizations necessary, the more frictionless the process would be. This advantage comes at the typical business costs related to open ecosystems: it’s more difficult to profit in order to grant investment returns, to lock-in and retain users, to monetize research and development. But many examples seem to suggest a strong market case for such systems. Right now, the most used platform for the management of digital tokens is the Ethereum-based ERC20 protocol. Notwithstanding the several and very serious shortcomings of this asset protocol and especially of the underlying system (which we cannot cover here but are well documented and severely affect sustainability, security, censorship-resistance, confidentiality, and scalability) this has so far become is the de-facto standard for many token schemes and “Initial Coin Offerings”, a controversial but relevant use-case. Another controversial but relevant use-case for a blockchain-based asset scheme is related to digital IOUs representing fiat money (i.e., US dollars): this kind of technique is often used, on Bitcoin-based protocols like Omni, to circumvent regulatory barrier to fiat-money deposit and withdrawal to and from cryptocurrency exchanges, and could prove useful in the future for the development of decentralized exchanges, where the “fiat representation” function can be legally separated from the actual trading/exchanging system. While not sustainable in their current form, these examples prove the wide range of opportunities for a well designed, open, reasonably secure, auditable, censorship-resistant, private and scalable digital asset protocol. The fact itself that many market niches are now adopting broken models as de-facto standards for digital asset management, could represent a compelling argument for better alternatives.
### Existent Alternatives
If Ethereum-ERC20 model for blockchain-based assets raises several serious concerns, existent alternatives still fail to address many of them. Asset-specific independent blockchains are not sustainable, while proper asset-enabled side-chains are still just a promising field of research (relying on very strong assumptions as for bootstrap and adoption). Most “meta-protocols” developed on top of Bitcoin (digital asset protocols that rely on independent validation rules, leveraging Bitcoin’s blockchain just as “proof of publication”, in order to prevent double-spending and audit issuances and reserves), while providing a potential interesting solution, completely miss the standardness/interoperability point, while showing important scalability shortcomings. The “colored coin” idea (a particular subset of Bitcoin “meta-protocol”, where most of the features of the underlying platform, such as addresses, scripts and amounts, are leveraged to maximize interoperability) has been considered promising, but existing implementations show important limitations. In particular, they inherit and further exacerbate the confidentiality/fungibility shortcomings as well as the scalability shortcomings of the “on-chain” Bitcoin layer, making them both strictly worse. As for confidentiality/fungibility, existent “colored coin” schemes heavily rely on the present serious lack of there features on Bitcoin “layer 1”: specific bitcoin amounts (often already not fungible enough in the current Bitcoin setting) are made even less fungible, “coloring” them in ways that greatly facilitate forensic analysis and “tainting” techniques, often invalidating external confidentiality/fungibility enhancing practices (i.e., coinjoin or other techniques where “order-based coloring” and “value-based coloring” would break) and relegating them to (pseudo)anonymity sets that will necessarily be small-to-irrelevant for all but major asset-types. As for scalability, they inherit the typical limitations of “on-chain” Bitcoin transaction, making them worse because of the risk of perverse incentives for blockchain bloating, because of dust limit problems and because of the lack of a trivial support for light-nodes in the form of “SPV”-like solutions (whose effectiveness is anyway seriously questioned for Bitcoin itself). Also, many of the existing implementations require a huge number of “ad hoc” modification to the current Bitcoin infrastructure, making their adoption difficult and full of friction and reducing the potential standardness/interoperability/leverage points of strength of the model. It is also possible that many of these first implementations had the timing wrong (the market was not showing the current strong demand for a digital asset management standard, back when they have been conceived and implemented), and that a new, reviewed proposals could now gather more interest and momentum.
## General Design
### General Goals
A new, better proposal for a blockchain-based asset management standard should satisfy as much as possible all the rational market requirement (standardness, auditability, native predisposition for blind/federated and fully decentralized settings), as well as overcome many of the shortcomings of existing alternatives. The “RGB” protocol is mostly aimed to “layer 2” scalability/fungibility strategies, but it relies for its bootstrap on a “layer 1” core, which borrows extensively from existent “colored coin” concepts, maximizing standardness properties, leveraging as much as possible the current Bitcoin infrastructure and interoperating seamlessly with it with minor, modular add-ons. This part will introduce some new modifications in respect with traditional “colored coin” implementations, aimed to reach “on-chain” levels of confidentiality/fungibility (“Dark Color”) and scalability (“Light Color”) which could be considered at least close to the ones of Bitcoin itself: a trustless support for light-nodes, a set of responsible best practices to limit and disincentivize blockchain-bloating, a smooth management of problems related to the dust limit, a broad (pseudo-)anonymity set for asset users, a complete independence from output ordering. Other modifications of the “layer 1” are introduced as a mean to make this protocol fully compatible with the main “layer 2”/”off-chain” standards, with a particular focus on Lightning Network, in order to seamlessly inherit all their game-changing scalability and confidentiality/fungibility features. Furthermore, the protocol proposal will contain an additional, specific and native “layer 2” solution based on “Single Use Seals” and “Proofs of Publication Ledger”.
### Initial Definitions
* We call **“asset”** a generic family of units of digital property, whose scarcity, divisibility and conditional transferability features, as well as associated “rights” (legally or technically enforced), are defined by the relative contract before the issuance.
* We call **“token”** a single conventional unit of a specific asset type (without further assumptions about its divisibility).
* We call **“colored”** a transaction output which represents the ownership of tokens of one or more assets.
* We call **“contract”** the set of conditions that the issuer commit to when issuing an asset, including rules that will be enforced on any transfer of that asset.
* We call **“issuance”** the action, performed by an issuer, of creating and publishing an asset contract, generating and distributing a certain number of tokens to a list of recipient. The issuance can be done only once for any given token (no more tokens can be "printed" after the first issuance).
* We call **“transfer”** the action, performed by one or more senders, of transferring tokens it/they owned to one or more receivers.
* We call **“redemption”** the action, performed by one or more senders, of transferring tokens to their initial issuer in order to redeem (leveraging autonomous mechanisms or legal claims) the rights associated with the correspondent asset contract.
* We call **“re-issuance”** the action, performed by one or more senders, of transferring tokens to the initial issuer in order to have them issued again on a new public contract, possibly linked with the previous one.

### Main features
#### Contract Engine
In order to be able to compose and verify asset transactions related to a specific contract, RGB-compliant wallets must include a software module capable to run transactions against the meta-script contained in any public contract, testing deterministically the compliance with the contract. The meta-script should allow an easy versioning to build and manage expansions, dialect, upgrades.
#### Publisher Servers
The scheme requires additional agreed-upon third parties which store the chain of encrypted proofs and accept related queries, possibly in a "Bloom filter" way to increase privacy (false positive can be added randomly in order to maintain even more privacy). In the context of an issued asset, these **"publisher"** servers could be mantained by the issuer itself. More generally, they can be mantained individually by the receivers, or by one or many independent third parties selected from a set defined by the receivers. The storage and the trasmission of the proofs could be achieved via a decentralized sistem (BitTorrent, IPFS, Siacoin, ecc.), but the censorship-resistance gains do not compensate for the increased complexity. Moreover, the Proofmarshal Integration (see below) requires a centralized third party anyway, which could be effectevely leveraged for the Lightning Network Integragion (see below) as well.
#### Extended URI
Since any assumption of additional protocols for off-band communication weakens the standardness of the proposal, we leverage the only type of off-band communication already assumed as existing in most Bitcoin on-chain transactions: the address passing. When a payee generates an address to give to the payer, he also transmit the IP address (or set of IP addresses) of the selected Publisher Server (or collection of Publisher Servers), and he finally generates a number, hereby called **“dark-tag”**, passing it to the payee along with the address and the Publishing information. This feature can be developed extending the standard Bitcoin URI.

#### Proofmarshal Integration
The protocol will also include another L2 strategy for scalability/fungibility, an asset-specific implementation of the “Proofmarshal” concept, based on “Single-Use-Seals” and “Proof-of-Publication-Ledgers”. In this integration, a Publisher Server *might* also act as **“sealer”**, with the ability to censor transactions but not to manipulate/forge/falsify them by committing multiple proofs from different anonymous users to a single UTXO. This could decouple the anti-double-spending function of the Bitcoin blockchain from the specific asset transations, making possible to "seal" a huge number of them spending a single Bitcoin UTXO.

#### Lightning Network Integration
Being the protocol UTXO-based, it will be possible to link one or more assets owned to a Lightning Network channel which becomes *colored*, exchanging state updates which are compliant to the asset scheme, with strong guarantees that asset distribution will be preserved also in case of non-consensual closures. In this way, it will be possible to leverage the scalability and privacy features of the Lightning Network, as well as LN-enabled atomis swaps for decentralized asset exchange.

### Structure

##### Address-Based vs UTXO-Based

RGB allows the sender of a colored transaction to transfer the ownership of any asset in two slightly different ways:

* **Address-Based** if the receiver prefers to receive the colored UTXO itself;
* **UTXO-Based** if the receiver already owns one ore more UTXO(s) and would like to "bind" its new tokens he is about to receive to this/those UTXO(s). This allows the sender to spend the nominal Bitcoin value of the UTXO which was previously bound to the tokens however he wants (send them back to himself, make an on-chain payment, open a Lightning channel or more). The UTXO is serialized as `SHA256(TX_HASH:OUTPUT_INDEX)` in order to increase the privacy of the receiver.

##### Proofs

Every RGB on-chain transaction will have a corresponding **"proof"**, where the sender encrypts, using the payee’s dark-tag, the following information in a structured way:

* the entire chain of proofs received up to the issuance contract;
* a list of triplets made with:
	* color of the token being transacted
	* amount being transacted
	* either the hash of an UTXO in the form (TX_hash, index) to send an *UTXO-Based* transaction or an index which will bind those tokens to the corresponding output of the transaction *spending* the colored UTXO. 
* a free field to pass over transaction meta-data that could be conditionally used by the asset contract to manipulate the transaction meaning (“meta-script");
* The parameters used to create the signature, in order to allow the payee and the following receivers of these tokens to verify the commitment **[expand]**

In order to help a safe and easy management of the additional data required by this feature, the dark-tag can be derived from the BIP32 derivation key that the payee is using to generate the receiving address. 

**[note on safety of mixing Bitcoin and RGB addresses]**

This feature should enhance the anonymity set of asset users, making chain analysis techniques almost as difficult as ones on “plain bitcoin” transactions. The leakage of a specific transaction dark-tag gives away the path from the issuing to the transaction itself, and of the “sibling” transactions, but it preserves uncertainty about other branches.

#### Color Addition
[expand]
## Exemplified Process Description
The following Process Description assumes:

* the use of Version 1.0 of RGB Meta-scrip;
* one-2-one transfers after the issuance (many-to-many transfers are possible);
* single-asset issuance and transfers (multi-asset issuance and transfers are possible);
### Basic Asset Issuance

1. The issuer prepares the public contract for the asset issuing, with the following structure:

```json
{
	"version":{
		// RGB Meta-script version - https://semver.org
		"major": <Integer>, // version when you make incompatible API changes
		"minor": <Integer>, // version when you add functionality in a backwards-compatible manner
		"patch": <Integer>  // version when you make backwards-compatible bug fixes
	},
	"title": <String>, // Title of the asset contract
	"description": <String>, // Description of possible reediming actions and non-script conditions
	"issuance_date": <Date>, // Date of issuance
	"issuance_utxo": <String>, // The UTXO which will be spent with a commitment to this contract
	"owner_utxo": <String>, // The UTXO which will receive all the issued token
	"contract_url": <String>, // Unique url for the publication of the contract and the light-anchors
	"re-issuance_url": <String>, // Url for the contract of which this contract is the reissuance (optional)
	"re-issuance_utxo": <String>, // The UTXO which will need to be spent in order to make a re-issuance (optional)
	"next_re-issuance_enabled": <Boolean>, // Flag to represent the possibility of reissuance
	"total_supply": <Integer>, // Total supply in satoshi (1e-8)
	"max_hops": <Integer>, // Maximum amount of onchain transfers that can be performed on the asset before reissuance
	"min_amount": <Integer>, // Minimum amount of colored satoshis that can be transfered together
}
```

2. The issuer spends the `issuance_utxo` with a commitment to this contract and publishes the contract, followed by the proofs, on the selected public channel.

### On-chain Asset Transfer
1. The payee can either chose one of its UTXO or generates in his wallet a receiving address as per BIP32 standard, together with 30 bytes of entropy, which will serve as dark-tag for this transfer.
2. The payee transmits the UTXO or the address, the dark-tag and a list of storage servers he wishes to use to the payer.
3. The payer composes (eventually performing a coin-selection process from several unspent colored outputs), signs and broadcasts with his wallet a transaction with the following structure (the order of inputs and output is irrelevant):
  * Inputs
     * Colored Input 1: valid colored (entirely or partially) UTXO to spend
     * Colored Input 2: (optional)
  * Outputs
     * Colored Output 1: address of the Nth receiver (if performing an *Address-Based* transaction)
     * Colored Output 2: (optional) another address of the payer for the colored (up to capacity) and non-colored change

The payer also produces a new proof containing:

* RGB Meta-script version
* A list of triplets made with:
	* color of the token being transacted
	* amount being transacted
	* either the hash of an UTXO in the form (TX_hash, index) to send an *UTXO-Based* 
* Meta-script-related transaction meta-data
* The parameters used to create the signature, in order to allow the payee and the following receivers of these tokens to verify the commitment **[expand]**

This proof is simmetrically encrypted using AES 256 together with the entire chain of proofs up to the issuance of the token and uploaded to the storage server(s) selected by the payee.

Every signature performed in the transaction **must** include a commitment to the proof produced.

In the case of a multisig address spending funds **all** the signatures must include the same commitment.

### Lightning Asset Transfer
[expand]
### Proofmarshal Asset Transfer
[expand]
### Basic Asset Redeeming
[expand]
### Basic Asset Re-issuance
[expand]
## Reference Implementation
[expand]
## Requirements Check
### Standardness
[expand]
### Auditability
[expand]
### Blindness/Federation
[expand]
### Full Decentralization
[expand]
## Future Evolutions
### Advanced Scripts
#### Multiple Asset Management
[expand]
#### Simplified Issuance
[expand]
#### Issuer Fees
[expand]
### DBTEE Contracts
[expand]
### BOLT-based Exchange
[expand]
### Asset-enabled Side-chains
[expand]
## Explanatory Notes
[expand]
## Open Points
* General weaknesses of blockchain-asset capabilities
* General game-theory dangers
* Other off-chain compatibilities still to test
* Dust Limit (look at Todd’s python library)
* Payment protocol for dark-tags
## Copyright
[expand: DPL/MIT]

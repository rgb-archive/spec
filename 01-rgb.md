# RGB Protocol Specification #01: Contracts and Proofs

* [Versioning](#versioning)
* [Commitment Scheme](#commitment-scheme)
  * [OP_RETURN](#op_return)
  * [Pay-to-contract](#pay-to-contract)
* [Contracts](#contracts)
  * [Re-issuance](#re-issuance)
  * [Proof-of-burn](#proof-of-burn)
  * [Entity Structure](#entity-structure)
    * [Header](#header)
  * [Blueprints and their versioning](#blueprints-and-versioning)
    * [Simple issuance: `0x01`](#simple-issuance-0x01)
    * [Crowdsale: `0x02`](#crowdsale-0x02)
    * [Re-issuance: `0x03`](#re-issuance-0x03)
* [Proofs](#proofs)
  * [Transfer proofs](#transfer-proofs)
  * [Special proofs](#special-proofs)
* [Structure](#structure)
  * [Address-Based vs UTXO-Based](#address-based-vs-utxo-based)
  * [RgbOutPoint](#rgboutpoint)
  * [Multi-signature Asset Ownership](#multi-signature-asset-ownership)
* [Exemplified Process Description](#exemplified-process-description)
  * [Basic Asset Issuance](#basic-asset-issuance)
  * [On-chain Asset Transfer](#on-chain-asset-transfer)
  * [Color Addition](#color-addition)

## Versioning

The protocol can be updated in the future, affecting the structure of the entities which are used by it (contracts, proofs). In order to preserve the space used by those entities, we use strict serialization format which does not allow adding/removing fields or changing types of existing fields. Thus, each entity has its own version as its first field, which defines how the entity has to be parsed. 

The current specification defines the structure for the first version of RGB contracts, transfer proofs and contract blueprints. By default, proofs MAY utilize versions that are different from the version of the issuing contract or other proofs – unless it is prohibited by the corresponding version specification explicitly.

## Commitment Scheme

In order to ensure immutability and prevent double spend, it's necessary to strongly bind RGB contracts and asset transfer proofs to Bitcoin transaction outputs in a way that makes impossible to modify RGB entities at a later time without invalidating them. This is done with cryptographic commitments, that commit the hash of the contract or proof into the mined bitcoin transaction output – pretty much like it is done in the [OpenTimeStamps](https://opentimestamps.org/).

In this specification we describe two commitment schemes available in the RGB protocol: Pay-to-contract and OP_RETURN.
Pay-to-contract scheme SHOULD BE the default recommended scheme, while OP_RETURN SHOULD BE be reserved only for the cases of (a) public asset issuing contract commitments and (b) for asset transfers that have to be compatible with HSM/hardware wallets. The reason of pay-to-contract being the default scheme is the reduction of Bitcoin blockchain pollution with asset transfer data and better privacy: pay-to-contract has higher protection from on-chain analysis tools.

Contracts and proofs bind RGB assets to transaction output – or, in case of proofs, to multiple outputs of a single or multiple transactions (see `issuance_utxo` field in [contract header](#header) and [Proof structure](#address-based-vs-utxo-based) for the details). These transaction(s) MAY differ from a transaction the contract or the proof is committed to. In order to prevent a double spend, each time when a UTXO containing an RGB asset is spent, the spending transaction MUST contain new commitment to the proof of the asset spending. Proofs that are not committed to a transaction which spends **all** of the UTXOs corresponding to RGB assets given in the proof inputs – or committed to some other transaction – MUST BE considered invalid.

The proofs MAY follow different commitment scheme than the contract; moreover different proofs MAY use different commitment schemes.

Which commitment scheme is used by a contract or a proof is defined by the presence of the `original_pk` field in their header.

### OP_RETURN

A transaction committing to a proof or contract using the `OP_RETURN` scheme is considered valid if:

1. There's at least one `OP_RETURN` output
2. The first `OP_RETURN` output contains a 32-bytes push which is SHA256 of the entity which the transaction is committing to (i.e. `contract_id` and `proof_id`, which reperesent SHA256 of serialized contract/proof data), prefixed with `rgb:contract` (for contracts) and `rgb:proof` (for proofs) UTF-8 strings: `OP_RETURN <SHA256('rgb:<contract|proof>' || SHA256(serialized_bytecode))`

![OP_RETURN Commitment](assets/rgb_op_return_commitment.png)

The main rationale behind adding OP_RETURN scheme additionally to Pay-to-contract is that getting pay-to-contract to work with hardware wallets is non-trivial. Getting pay-to-contract to work with with most off-the-shelf HSMs (that are typically used by exchanges etc for custody) is impossible. Restricting RGB to pay-to-contract/sign-to-contract only may limit the applicability and use cases.

### Pay-to-contract

The commitment to a proof made using pay-to-contract SHOULD BE considered valid only, and only if:

* Given `n = fee_satoshi mod num_outputs`

1. The `n`th output pays an arbitrary amount of Bitcoin to `P2PKH`, `P2WPKH` or `P2SH`-wrapped `P2WPKH`.
2. The public key of this output is tweaked using the method described below
3. There are no `OP_RETURN` outputs in the same transaction

Otherwise, the proof MUST BE considered as an invalid and MUST NOT BE accepted; the assets associated with the proof inputs MUST BE considered as lost. NB: since in the future (with the introduction of the future SegWit versions, like Taproot, MAST etc) the list of supported output types MAY change, assets allocated to invalid outputs MUST NOT BE considered as deterministically burned; in order to create a proper proof of burn user MUST follow the procedure described in the [Proof-of-burn section](#proof-of-burn)

Rationale for not supporting other types of transaction outputs for the proof commitments:
* `P2PK`: considered insecure and SHOULD NOT be used;
* `P2WSH`: the present version of RGB specification does not provides a way to deterministically define which of the public keys are present inside the script and which are used for the commitment – however, this behaviour may change in the future (see the note above);
* `P2SH`, except `P2SH`-wrapped `P2WPKH`, but not `P2SH`-wrapped `P2WSH`: the same reason as for `P2WSH`;
* `OP_RETURN` outputs can't be tweaked, since they do not contain a public key and serve pre-defined purposes only. If it is necessary to commit to OP_RETURN output one should instead use [OP_RETURN commitment scheme](#op_return)
* Non-standard outputs: tweak procedure can't be standardized.

![Pay-to-contract Commitment](assets/rgb_p2c_commitment.png)

#### Public key tweaking

The tweaking procedure has been previously described in many publications, such as [Eternity Wall's "sign-to-contract" article](https://blog.eternitywall.com/2018/04/13/sign-to-contract/). However, since the tweaking is already widely used practice ([OpenTimeStamps](https://petertodd.org/2016/opentimestamps-announcement), [merchant payments](https://arxiv.org/abs/1212.3257)) and will be even more adopted with the intruduction of [Taproot](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2018-January/015614.html), [Graphroot](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2018-February/015700.html), [MAST](https://github.com/bitcoin/bips/blob/master/bip-0114.mediawiki) and many other proposals, the hash, used for public key tweaking under one standard (like this one) can be provided to some uninformed third-party as a commitment under the other standard (like Taproot), and there is non-zero chance of a collision, when serialized RGB contract or proof will present at least a partially-valid Bitcoin script or other code that can be interpreted as a custom non-RGB script and used to attack that third-party. In order to reduce the risk, we follow the practice introduced in the [Taproot BIP proposal](https://github.com/sipa/bips/blob/bip-schnorr/bip-taproot.mediawiki#tagged-hashes) of prefixing the serialized RGB contract/proof with **two** hashes of RGB-specific tags, namely "rgb:contract" for contracts and "rgb:proof" for proofs. Two hashes are required to further reduce risk of undesirable collisions, since nowhere in the Bitcoin protocol the input of SHA256 starts with two (non-double) SHA256 hashes.

The whole algorithm thus looks in the following way
1. Serialize contract/proof with standard bitcoin transaction serialization rules `s = consensus_serialize(<contract> -or- <proof>)` and compute its hash, i.e. obtain `contract_id`/`proof_id` value: `id = SHA256(s)`
1. Prefix it twice with a hash of a proper tag and compute double hash with `hash<sub>tag</sub>(m)` function introduced in the [Taproot BIP](https://github.com/sipa/bips/blob/bip-schnorr/bip-taproot.mediawiki#tagged-hashes) `h = hash<sub>rgb:contract/rgb:proof</sub>(original_pubkey || id)`, where `hash<sub>tag</sub>(message) := SHA256(SHA256(tag) || SHA256(tag) || message)`
2. Compute `new_pub_key = original_pubkey + h * G`
3. Compute the address as a standard Bitcoin `P2(W)PKH` using `new_pub_key` as public key

In order to be able to spend the output later, the same procedure should be applied to the private key.

## Contracts

Contracts are entities that, once "deployed" on the Bitcoin blockchain, determine the creation of a new, unique asset with a specific set of characteristics (like total supply, divisibility, dust limit, etc.) and possibly provably linked to some kind of commitment by the Issuer.

Contract is uniquely identified by its `contract_id`, which is computed as a single SHA245-hash of the serialized commitment fields from both contract header and body.

Every asset is identified by the `asset_id`, which is computed in the following way:  
`asset_id = RIPMD160(SHA256(contract_id || committment_txid || asset_no))`,  
where `committment_txid` is a serialized txid (in standard bitcoin serialization format) of the transaction in which this contract is committed with either pay-to-contract or OP_RETURN commitment scheme. Use of RIPMD160 hash gives smaller size for the asset_id, which is important for saving storage space in proofs, and makes asset_id indistinguishable from Bitcoin addresses.

The rational for this asset_id design is the following: RGB-enabled LN nodes would have to announce the list of assets (i.e. asset ids) they can buy/sell – with corresponding bid and ask prices. Since we'd like to increase the privacy, we need these asset ids to be "obscured", i.e. not easily tracked down to the specific asset/contract – unless for those who has the source of the asset issuing contract. This means that we could not just rely on `SHA256(contract_id || index)`, since contract_id is public, and it will be quite easy to construct "rainbow tables" with contract_ids joined by different indexes and track the asset ids down to the issuing contracts. At the same time, `committment_txid` is a private information known only to the owners of the contract (with the exception of public contracts, but we do not need to hide asset_id for public assets anyway).

Many different *kinds* (or *blueprints*) of contracts exist, allowing the user to choose the rules that will define how the asset is issued and, later, transferred. **Every contract kind has a specific 1-byte-long unique identifier**, which is serialized and committed to during the deployment phase, to make sure that its behaviour cannot be changed at a later time. Every blueprint also has an independent versioning system, in order to make the entire project even more "modular" (See [issue #23 on GitHub](https://github.com/rgb-org/spec/issues/23)).

### Re-issuance

Since the total supply of an asset is hard-coded into the contract itself, there's no way to change it at a later time. The only way to issue more token, thus inflating the supply, is by doing what's called a **"re-issuance"**, which basically means issuing another contract of type `0x03` (reissuance) linked to the previous one by committing it to `reissuance_utxo`. This feature can be disable by setting `reissuance_enabled` to `0`. 

### Proof-of-burn

Token owners have the ability to *burn* tokens in order to claim or redeem any of the rights associated with their tokens.

To do this, token owner have to issue a special form of the proof ("proof of burn"), having zero outputs, and commit it with either Pay-to-contract or OR_RETURN scheme. The proof SHOULD then be published by the asset issuer itself to *prove* that the supply has been deflated.

### Entity Structure

Contracts are made of two parts:

* Header - the area that contains all the fields common among every contract kind
* Body - the area that contains blueprint-specific fields

Both header and body contain fields to which the contract is cryptographically committed ("commitment fields") – and fields that do not participate in the generation of the cryptographic commitment. The latter can be either permanent or prunable; the permanent fields are required for the contract verification process and need to be transferred to other peers. Prunable fields are computable fields, they serve utilitary function, optimising the speed of data retrieval from Bitcoin Core node. Prunnable fields are optional, they MAY be transfered upon request from one peer to other (alike witness data in bitcoin blocks), however peers are MAY NOT keep these data and can decline the requests for providing them from other peers.

#### Header

The header contains the following fields:

* Commitment fields:
    * `version`: Version of the contract headers, 16-bit integer.
    * `blueprint_type`: 16-bit number representing version of the blueprint used
    * `title`: Title of the asset contract
    * `description`: (optional) Description of the asset contract
    * `contract_url`: (optional) Unique url for the publication of the contract and the light-anchors
    * `network`: The Bitcoin network in use (mainnet, testnet)
    * `issuance_utxo`: The UTXO which will be held the issued assets
    * `committment_txid`: (optional) The transaction id containing a commitment to this contract. If the field is absent, the contract is committed to the same transaction containing `issuance_utxo`
    * `total_supply`: Total supply, using the smallest undividable available unit, 64-bit unsigned integer
    * `min_amount`: Minimum amount of tokens that can be transferred together, like a *dust limit*, 64-bit unsigned integer
    * `max_hops`: Maximum number of "hops" before the reissuance (can be set to `0xFFFFFFFF` to disable this feature, which should be the default option)
    * `reissuance_utxo`: (optional) UTXO which have to be spent to reissue tokens. Absence of this field means that reissuance is disabled,
* Non-prunable non-commitment fields:
    * `original_pubkey`: (optional) If present, signifies P2C commitment scheme and provides the original public key before the tweak procedure which is needed to verify the contract commitment. Original pubkey is not a part of the commitment fields since it was explicitly included into the commitment during pay-to-contract public key tweaking procedure.

NB: Since with bitcoin network protocol-style serialization, used by RGB, we can't have optionals, the optional header fields should be serialized as a zero-length strings, which upon deserialization must be converted into `nil/NULL`

### Blueprints and versioning

There are two types of versioning for RGB contracts: header version (`version` field) and blueprint type (`blueprint_type` field). The difference is that header version defines a set of fields used by the contract, which might change in the future with addition of the new fields – or some fields becoming optional or changing data type. Blueprint version defines the exact type of the contract with specific fields and structure for the contract body.

#### Simple issuance: `0x01`

This blueprint allows to mint `total_supply` tokens and immediately send them to `owner_utxo`.

The additional fields in the body are:

* `owner_utxo`: the UTXO which will receive all the tokens

#### Crowdsale: `0x02`

This blueprint allows to set-up a crowdsale, to sell tokens at a specified price up to the `total_supply`. This contract actually creates two different assets with different `assets_id`s. Together with the "normal" token, a new "change" token is issued, to "refund" users who either send some Bitcoins too early or too late and will miss out on the crowdsale. Change tokens have a fixed 1-to-1-satoshi rate in the issuing phase, and are intended to maintain the same rate in the redeeming phase.

The additional fields in the body are:

* `deposit_address`: the address to send Bitcoins to in order to buy tokens
* `price_sat`: the price in satoshi for a single token
* `from_block`: when the crowdsale starts
* `to_block`: when the crowdsale ends

These fields are commitment fields.

#### Re-issuance: `0x03`

This blueprint allows an asset issuer to re-issue tokens by inflating the supply. This is allowed only if the original contract had `reissuance_enabled` != `0`. 

This contract MUST be issued using the `reissuance_utxo` and its version MUST match the original contract's one. 

The following fields in its header MUST be set to `0` in order to disable them:

* `title`
* `description`
* `network`
* `min_amount`
* `max_hops`
* `commitment_scheme`

The following fields MUST be filled with "real" values:

* `contract_url`: Unique url for the publication of the contract and the light-anchors
* `issuance_utxo`: The UTXO which will be spent in a transaction containing a  commitment to this contract to "deploy" it (must match the original contract's `reissuance_utxo`)
* `total_supply`: Additional supply in satoshi (1e-8)
* `reissuance_enabled`: Whether the re-issuance feature is enabled or not
* `reissuance_utxo`: (optional) UTXO which have to be spent to reissue tokens
* `blueprint_type`: 16-bit number representing version of the blueprint used (i.e. `0x03`)

There are no additional fields in its body.

## Proofs

Proofs, as the name implies, are entities that *prove* that some requirements are met. Proofs allow transfer of assets by proving the ownership of them and "connect" to contracts, by fulfilling all the conditions set in the contract itself.

Like contracts, proofs have an header and a body, where the common and "special" fields are stored respectively.

Both header and body contain fields to which the contract is cryptographically committed ("commitment fields") – and fields that do not participate in the generation of the cryptographic commitment. The latter can be either permanent or prunable; the permanent fields are required for the contract verification process and need to be transferred to other peers. Prunable fields are computable fields, they serve utilitary function, optimising the speed of data retrieval from Bitcoin Core node. Prunnable fields are optional, they MAY be transfered upon request from one peer to other (alike witness data in bitcoin blocks), however peers are MAY NOT keep these data and can decline the requests for providing them from other peers.

Contract is uniquely identified by its `proof_id`, which is computed as a single SHA245-hash of the serialized commitment fields from both contract header and body.

### Transfer proofs

Every RGB on-chain transaction will have a corresponding **"proof"**, where the payer stores the following information in a structured way:

* Commitment fields:
    * `version`: Version of the contract headers, 16-bit integer.
    * `assets`: list of `asset_id`s, transferred by this proof; each `asset_id` MUST have corresponding proofs and issuing contracts in input DAG;
    * `inputs`: the entire DAG of proofs received up to the issuance contracts for each of the assets transferred by the proof;
    * `outputs`: an array containing list of transfers for each or the `asset_id` listed in `assets` field, such as an index within `outputs` field corresponds to an `asset_id` under the same index in `assets` field. Each array member is presented by a list of transfers, consisting of tuples:
        * amount being transacted
        * either the hash of an UTXO in the form (TX_hash, index) to send an *UTXO-Based* transaction or an index which will bind those tokens to the corresponding output of the transaction *spending* the colored UTXO.
    * `metadata`: an optional free field to pass over transaction meta-data that could be conditionally used by the asset contract to manipulate the transaction meaning (generally for the "meta-script" contract blueprint);
* Non-commitment non-prunable fields:
    * `original_pubkey`: (optional) If present, signifies P2C commitment scheme and provides the original public key before the tweak procedure which is needed to verify the proof commitment. Original pubkey is not a part of the commitment fields since it was explicitly included into the commitment during pay-to-contract public key tweaking procedure.

Notes on output structure:
* Zero length for the list of outputs is used to indicate [proof of burn](#proof-of-burn)
* The amount field in the last tansfer tuple for each asset type MUST BE omitted and MUST BE automatically deduced as `sum(inputs) - sum(outputs)` for the given asset type. This allows do avoid situations where `sum(inputs) > sum(outputs)` and  saves storage space.

The proof MUST be considered invalid as a whole if `sum(inputs) < sum(outputs)` for any of the assets transfered by the proof.

### Special proofs

Every contract blueprint needs a special "adaptor" proofs, that *proves* that the payer can fulfill the requirements specified by the contract itself.

## Structure

### Address-Based vs UTXO-Based

RGB allows the sender of a colored transaction to transfer the ownership of any asset in two slightly different ways:

* **UTXO-Based** if the receiver already owns one ore more UTXO(s) and would like to "bind" its new tokens he is about to receive to this/those UTXO(s). This allows the sender to spend the nominal Bitcoin value of the UTXO which was previously bound to the tokens however he wants (send them back to himself, make an on-chain payment, open a Lightning channel or more). The UTXO is serialized as `SHA256D(TX_HASH || OUTPUT_INDEX_AS_U32)` in order to increase the privacy of the receiver.
* **Address-Based** if the receiver prefers to receive the colored UTXO itself;

### RgbOutPoint

`RgbOutPoint` is an entity that encodes the receiver of some tokens. It can either be a `Sha256d` entity when used in an UTXO-based transaction, to represent the double SHA256 of the pair (TX_HASH, OUTPUT_INDEX), or a 16-bit unsigned integer when used in an address-based transaction.

When serialized, one more byte is added to encode which of the two branches is being encoded. Its value must be `0x01` for UTXO-based transactions and `0x02` for address-based ones.

For example, the byte sequence:

```
01 49CAFDBC 3E9133A7 5B411A3A 6D705DCA 2E9565B6 60123B65 35BABB75 67C28F02
```

is decoded as:

* `0x01` = UTXO-based transaction
* `...` = SHA256D(TX_HASH || OUTPUT_INDEX_AS_U32)

### Multi-signature asset ownership

Multi-signature asset ownership is working in the same way it works for bitcoin: transfer proofs MAY assign RGB assets to a `P2SH` or `P2WSH` address containing multi-signature locking script, while being committed with either Pay-to-contract or OP_RETURN commitment scheme to some other output within the same or other transaction.

Such assets can be spent with a new transfer proof only under the same circumstances as satoshis under this output: if the unlocking script will satisfy the signing conditions of the locking script.

## Exemplified Process Description

The following Process Description assumes:

* one-2-one transfers after the issuance (many-to-many transfers are possible);
* single-asset issuance and transfers (multi-asset issuance and transfers are possible);

### Basic Asset Issuance

1. The issuer prepares the public contract for the asset issuing, with the following structure:

```c
{
	"kind": 0x01 // The kind of contract we are creating, in this case a generic issuance
	"version": 0x0008 // Version of this contract kind to use,
	"title": <String>, // Title of the asset contract
	"description": <String>, // Description of possible redeeming actions and non-script conditions
	"issuance_utxo": <String>, // The UTXO which will be spent with a commitment to this contract,
	"contract_url": <String>, // Unique url for the publication of the contract and the light-anchors
	"total_supply": <Integer>, // Total supply in satoshi (1e-8)
	"max_hops": <Integer>, // Maximum amount of onchain transfers that can be performed on the asset before reissuance
	"min_amount": <Integer>, // Minimum amount of colored satoshis that can be transferred together,
	"network": "BITCOIN", // The network in use
	"reissuance_enabled": 0, // Disable reissuance
	"commitment_scheme": "OP_RETURN", // The commitment scheme used by this asset
	

	"owner_utxo": <String>, // The UTXO which will receive all the issued token. This is a contract-specific field.
}
```

2. The issuer spends the `issuance_utxo` with a commitment to this contract (using an `OP_RETURN`) and publishes the contract. *`total_supply`* tokens will be created and sent to `owner_utxo`.

### On-chain Asset Transfer
1. The payee can either chose one of its UTXO or generates in his wallet a receiving address as per BIP32 standard.
2. The payee transmits the UTXO or the address and a list of storage servers he wishes to use to the payer.
3. The payer composes (eventually performing a coin-selection process from several unspent colored outputs), signs and broadcasts with his wallet a transaction with the following structure (the order of inputs and output is irrelevant):
  * Inputs
     * Colored Input 1: valid colored (entirely or partially) UTXO to spend
     * Colored Input 2: (optional)
  * Outputs
     * Colored Output 1: address of the Nth receiver (if performing an *Address-Based* transaction)
     * Colored Output 2: (optional) another address of the payer for the colored (up to capacity) and non-colored change

The payer also produces a new transfer proof containing:

* A list of triplets made with:
	* color of the token being transacted;
	* amount being transacted;
	* either the hash of an UTXO in the form `SHA256D(TX_HASH || OUTPUT_INDEX_AS_U32)` to send an *UTXO-Based* tx or the index of the output sent to the receiver to send an *Address-Based* tx;
* Optional meta-script-related meta-data;

The proof is hashed and a commitment to the hash is included in the transaction, in this case using an `OP_RETURN`.

### Color Addition
[expand]

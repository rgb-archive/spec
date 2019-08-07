# RGB Protocol Specification #01: Contracts and Proofs

* [Overview](#overview)
  * [Versioning](#versioning)
  * [Multi-signature Asset Ownership](#multi-signature-asset-ownership)
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
  * [Asset assignments](#asset-assignments)

## Overview

The protocol allows issuance, re-issuance and transfer of digital assets (tokenised securities, collectionables etc) on top of LNP/BP technology stack. The assets are issued and re-issued using different types (called **blueprints**) of **RGB contracts** and are transferred using **RGB proofs**.

In order to prevent double-spends, the protocol utilizes single-use-seals mechanism, originally proposed by Peter Todd. Briefly, contracts and proofs **[assign](#asset-assignments)** some defined amounts of assets to bitcoin transaction outputs, named **assigned assets** and **outputs with assigned assets** correspondingly. Each time an output with assigned assets is spent it implies the fact of the asset transfer, and a corresponding new proof for the asset transfer has to be created. To reach immutability, both contracts and proofs cryptographically commit their data into Bitcoin transaction outputs, named **commitment transactions** and **commitment outputs** (see [Commitment Scheme](#commitment-scheme) section). For asset issuance, contracts commit to a transaction spending some predefined bitcoin transaction outpoint; for asset re-issuance — to the transaction spending committed output of the most recent re-issuance/issuance contract (see [Contract](#contracts) section for details). For asset transfer proofs, commitment outputs MUST BE placed into the transactions spending outputs with assigned assets, but the transferred assets can be assigned to some other external transactions, if required. Alongside asset assignments, each proof references hashes (unique identifiers) of its **upstream** proofs and contracts, indicating the sources of the transferred assets (see [Proofs](#proofs) section for details).

![RGB Protocol Overview](assets/rgb_overview.png)

### Versioning

The protocol can be updated in the future, affecting the structure of the entities which are used by it (contracts, proofs). In order to preserve the space used by those entities, we use strict serialization format which does not allow adding/removing fields or changing types of existing fields. Thus, each entity has its own version as its first field, which defines how the entity has to be parsed. 

The version is a 16-bit integer, constructed of two main parts: major and minor version bits. The minor version is the lower (in little-endian Bitcoin encoding format) six bits (0-63); the major version is the upper ten bits. Minor version represents backward-compatible protocol changes ("soft-forks"), while major version increase represents incompatible changes ("hard-forks"). 

Proofs MAY have different minor version than the issuing contract, however they can't differ in a major version from it. This is required in order to prevent potential double-spending: the changes in a commitment schemes are "hard-forks" without backward compatibility, and they will require increase of the major version. Since the proofs can't have a different major version than the issuing contract, it will be impossible to produce two proofs under the different commitment schemes utilizing incompatible versions.

If the issuer would like to upgrade the contract major version, he needs to deploy a new [Proof-of-burn](#proof-of-burn) contract with the updated major version, so asset owners will be able to upgrade and migrate to a new version through it. 

Contract major and minor version jointly defines the set of available contract blueprints and their structure.

The current specification defines the structure for the 0.5 version of RGB contracts, their blueprints and transfer proofs. 

### Multi-signature asset ownership

Multi-signature asset ownership is working in the same way it works for bitcoin: transfer proofs MAY assign RGB assets to a `P2SH` or `P2WSH` address containing multi-signature locking script, while being committed with either Pay-to-contract or OP_RETURN commitment scheme to some other output within the same or other transaction.

Such assets can be spent with a new transfer proof only under the same circumstances as satoshis under this output: if the unlocking script will satisfy the signing conditions of the locking script.

## Commitment Scheme

In order to ensure immutability and prevent double spend, it's necessary to strongly bind RGB contracts and asset transfer proofs to Bitcoin transaction outputs in a way that makes impossible to modify RGB entities at a later time without invalidating them. This is done with cryptographic commitments, that commit the hash of the contract or proof into the mined bitcoin transaction output – pretty much like it is done in the [OpenTimeStamps](https://opentimestamps.org/).

In this specification we describe two commitment schemes available in the RGB protocol: Pay-to-contract and OP_RETURN. Pay-to-contract scheme SHOULD BE the default recommended scheme, while OP_RETURN SHOULD BE be reserved only for asset transfer proofs that have to be compatible with hardware wallets, thus proofs under the same contract can use different commitment schemes. Contracts always MUST BE deployed only with pay to contract scheme. Proofs 

The reason of pay-to-contract being the default scheme is the reduction of Bitcoin blockchain pollution with asset transfer data and better privacy: pay-to-contract has higher protection from on-chain analysis tools.

Contracts and proofs assign RGB assets to transaction(s) output(s) (see `issuance_txout` field in [contract header](#header) and `assignments` field in the [proof structure](#proofs) for the details). These transaction(s) MAY differ from a transaction the contract or the proof is committed to. In order to prevent a double spend, each time when a UTXO containing an RGB asset is spent, the spending transaction MUST contain new commitment to the proof of the asset spending. Proofs that are not committed to a transaction which spends **all** of the UTXOs corresponding to RGB assets given in the proof upstreams – or committed to some other transaction – MUST BE considered invalid.

Which commitment scheme is used by a contract or a proof is defined by the presence of the `original_pk` field in their header.

### OP_RETURN

A transaction committing to a proof or contract using the `OP_RETURN` scheme is considered valid if:

1. There's at least one `OP_RETURN` output
2. The first `OP_RETURN` output contains a 32-bytes push which is SHA256 of the entity which the transaction is committing to (i.e. `contract_id` and `proof_id`, which reperesent SHA256 of serialized contract/proof data), prefixed with `rgb:contract` (for contracts) and `rgb:proof` (for proofs) UTF-8 strings: `OP_RETURN <SHA256('rgb:<contract|proof>' || SHA256(serialized_bytecode))`

![OP_RETURN Commitment](assets/rgb_op_return_commitment.png)

The main rationale behind adding OP_RETURN scheme additionally to Pay-to-contract is that getting pay-to-contract to work with hardware wallets is non-trivial. Getting pay-to-contract to work with with most off-the-shelf HSMs (that are typically used by exchanges etc for custody) is impossible. Restricting RGB to pay-to-contract/sign-to-contract only may limit the applicability and use cases.

### Pay-to-contract

The commitment to a proof made using pay-to-contract SHOULD BE considered valid if, and only if:

* Given `n = fee_satoshi mod num_outputs`

1. The `n`th output pays an arbitrary amount of Bitcoin to `P2PKH`, `P2WPKH` or `P2SH`-wrapped `P2WPKH`.
2. The public key of this output is tweaked using the method described below
3. There are no `OP_RETURN` outputs in the same transaction (this rune is [forced at the level of Bitcoin Core](https://github.com/bitcoin/bitcoin/blob/d0f81a96d9c158a9226dc946bdd61d48c4d42959/src/policy/policy.cpp#L131))

Otherwise, the proof MUST BE considered as an invalid and MUST NOT BE accepted; the assets associated with the upstream proofs MUST BE considered as lost. NB: since in the future (with the introduction of the future SegWit versions, like Taproot, MAST etc) the list of supported output types MAY change, assets allocated to invalid outputs MUST NOT BE considered as deterministically burned; in order to create a proper proof of burn user MUST follow the procedure described in the [Proof-of-burn section](#proof-of-burn)

Rationale for not supporting other types of transaction outputs for the proof commitments:
* `P2PK`: considered legacy and MUST NOT be used;
* `P2WSH`: the present version of RGB specification does not provides a way to deterministically define which of the public keys are present inside the script and which are used for the commitment – however, this behaviour may change in the future (see the note above);
* `P2SH`, except `P2SH`-wrapped `P2WPKH`, but not `P2SH`-wrapped `P2WSH`: the same reason as for `P2WSH`;
* `OP_RETURN` outputs can't be tweaked, since they do not contain a public key and serve pre-defined purposes only. If it is necessary to commit to OP_RETURN output one should instead use [OP_RETURN commitment scheme](#op_return)
* Non-standard outputs: tweak procedure can't be standardized.

![Pay-to-contract Commitment](assets/rgb_p2c_commitment.png)

#### Public key tweaking

The tweaking procedure has been previously described in many publications, such as [Eternity Wall's "sign-to-contract" article](https://blog.eternitywall.com/2018/04/13/sign-to-contract/). However, since the tweaking is already widely used practice ([OpenTimeStamps](https://petertodd.org/2016/opentimestamps-announcement), [merchant payments](https://arxiv.org/abs/1212.3257)) and will be even more adopted with the intruduction of [Taproot](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2018-January/015614.html), [Graphroot](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2018-February/015700.html), [MAST](https://github.com/bitcoin/bips/blob/master/bip-0114.mediawiki) and many other proposals, the hash, used for public key tweaking under one standard (like this one) can be provided to some uninformed third-party as a commitment under the other standard (like Taproot), and there is non-zero chance of a collision, when serialized RGB contract or proof will present at least a partially-valid Bitcoin script or other code that can be interpreted as a custom non-RGB script and used to attack that third-party. In order to reduce the risk, we follow the practice introduced in the [Taproot BIP proposal](https://github.com/sipa/bips/blob/bip-schnorr/bip-taproot.mediawiki#tagged-hashes) of prefixing the serialized RGB contract/proof with **two** hashes of RGB-specific tags, namely "rgb:contract" for contracts and "rgb:proof" for proofs. Two hashes are required to further reduce risk of undesirable collisions, since nowhere in the Bitcoin protocol the input of SHA256 starts with two (non-double) SHA256 hashes.

The whole algorithm thus looks in the following way
1. Serialize contract/proof with standard bitcoin transaction serialization rules `s = consensus_serialize(<contract> -or- <proof>)` and compute its hash, i.e. obtain `contract_id`/`proof_id` value: `id = SHA256(s)`
1. Prefix it twice with a hash of a proper tag and compute double hash with `hash`<sub>tag</sub>`(m)` function introduced in the [Taproot BIP](https://github.com/sipa/bips/blob/bip-schnorr/bip-taproot.mediawiki#tagged-hashes) `h = hash`<sub>rgb:contract/rgb:proof</sub>`(original_pubkey || id)`, where `hash`<sub>tag</sub>`(message) := SHA256(SHA256(tag) || SHA256(tag) || message)`
2. Compute `new_pubkey = original_pubkey + h * G`
3. Compute the address as a standard Bitcoin `P2(W)PKH` using `new_pubkey` as public key

In order to be able to spend the output later, the same procedure should be applied to the private key.

## Contracts

Contracts are entities that, once "deployed" on the Bitcoin blockchain, determine the creation of a new, unique asset with a specific set of characteristics (like total supply, divisibility, dust limit, etc.) and possibly provably linked to some kind of commitment by the Issuer.

Contract is uniquely identified by its `contract_id`, which is computed as a single SHA245-hash of the serialized commitment fields from both contract header and body.

Every asset is identified by the `asset_id`, which is computed in the following way:  
`asset_id = RIPMD160(SHA256(contract_id || committment_txid || asset_no))`,  
where `committment_txid` is a serialized txid (in standard bitcoin serialization format) of the transaction in which this contract is committed to and `asset_no` is a serial asset number inside the contract (for the contracts issuing only a single asset it should be `0`). Use of RIPMD160 hash gives smaller size for the asset_id, which is important for saving storage space in proofs, and makes asset_id indistinguishable from Bitcoin addresses.

The rational for this asset_id design is the following: RGB-enabled LN nodes would have to announce the list of assets (i.e. asset ids) they can buy/sell – with corresponding bid and ask prices. Since we'd like to increase the privacy, we need these asset ids to be "obscured", i.e. not easily tracked down to the specific asset/contract – unless for those who has the source of the asset issuing contract. This means that we could not just rely on `SHA256(contract_id || index)`, since contract_id is public, and it will be quite easy to construct "rainbow tables" with contract_ids joined by different indexes and track the asset ids down to the issuing contracts. At the same time, `committment_txid` is a private information known only to the owners of the contract (with the exception of public contracts, but we do not need to hide asset_id for public assets anyway).

Many different *kinds* (or **blueprints**) of contracts exist, allowing the user to choose the rules that will define how the asset is issued and, later, transferred. Every contract kind has a specific 1-byte-long unique identifier for the used blueprint type (`blueprint_type` field), which is serialized and committed to during the deployment phase, to make sure that its behaviour cannot be changed at a later time.

### Re-issuance

Since the total supply of an asset is hard-coded into the contract itself, there's no way to change it at a later time. The only way to issue more token, thus inflating the supply, is by doing what's called a **"re-issuance"**, which basically means issuing another contract of type `0x03` (re-issuance) linked to the previous one by committing it to `reissuance_utxo`. This feature can be disable by setting `reissuance_enabled` to `0`. 

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
    * `version`: [version](#versioning) of the contract, 16-bit integer.
    * `blueprint_type`: 16-bit number representing version of the blueprint used
    * `title`: title of the asset contract
    * `description`: (optional) description of the asset contract
    * `contract_url`: (optional) unique url for the publication of the contract and the light-anchors
    * `network`: Bitcoin network in use (mainnet, testnet)
    * `deployment_txout`: UTXO which will be spent in the transaction which will have a contract commitment
    * `issuance_txout`: [RgbOutPoint](#asset-assignments) which will held the issued assets
    * `issued_supply`: total issued supply, using the smallest undividable available unit, 64-bit unsigned integer
    * `min_amount`: minimum amount of assets that can be transferred together, like a *dust limit*, 64-bit unsigned integer
    * `max_hops`: maximum number of "hops" before the reissuance (can be set to `0xFFFFFFFF` to disable this feature, which should be the default option)
    * `reissuance_enabled`: whether the re-issuance feature is enabled or not
    * `signature`: (optional) signature of the committed part of the contract (without the signature field itself).
* Non-prunnable non-commitment fields:
    * `original_pubkey`: provides the original public key before the tweak procedure which is needed to verify the contract commitment. Original public key is not a part of the commitment fields since it was explicitly included into the commitment during pay-to-contract public key tweaking procedure.

NB: Since with bitcoin network protocol-style serialization, used by RGB, we can't have optionals, the optional header fields should be serialized as a zero-length strings, which upon deserialization must be converted into `nil/NULL`

The contract issuer MAY sign the contract (by filling the appropriate `signature` field). It is the right of the issuer to choose which key should be used for contract signing: it can be the same key which is used for an associated commitment output, a key associated with the DNS certificate of the issuer domain, or any other.

### Blueprint types

#### Simple issuance: type `0x01`

This blueprint allows to mint `issued_supply` tokens and immediately send them to `issuance_txout`.

There are no additional fields in its body.

#### Crowdsale: type `0x02`

This blueprint allows to set-up a crowdsale, to sell tokens at a specified price up to the `issued_supply`. This contract actually creates two different assets with different `assets_id`s. Together with the "normal" token, a new "change" token is issued, to "refund" users who either send some Bitcoins too early or too late and will miss out on the crowdsale. Change tokens have a fixed 1-to-1-satoshi rate in the issuing phase, and are intended to maintain the same rate in the redeeming phase.

The additional fields in the body are:

* `deposit_address`: the address to send Bitcoins to in order to buy tokens
* `price_sat`: the price (in satoshis) for a single token
* `from_block`: when the crowdsale starts
* `to_block`: when the crowdsale ends

These fields are commitment fields.

#### Re-issuance: type `0x03`

This blueprint allows an asset issuer to re-issue tokens by inflating the supply. This is allowed only if the original contract had `reissuance_enabled` != `0`. 

This contract MUST be deployed by spending the commitment output of the original issuing contract. The major version of the re-issuance contract MUST match the original contract's one. 

The following fields in its header MUST be set to `0` or zero-length string in order to disable them:

* `title`
* `description`
* `network`
* `min_amount`
* `max_hops`
* `deployment_txout`

The following fields MUST be filled:

* `contract_url`: Unique url for the publication of the contract and the light-anchors
* `issued_supply`: Additional supply in satoshi (1e-8)
* `reissuance_enabled`: Whether the re-issuance feature is enabled or not
* `blueprint_type`: 16-bit number representing version of the blueprint used (i.e. `0x03`)

There are no additional fields in its body.

## Proofs

Proofs, as the name implies, are entities that *prove* that some requirements are met. Proofs allow transfer of assets by proving the ownership of them and "connect" to contracts, by fulfilling all the conditions set in the contract itself.

Like contracts, proofs have an header and a body, where the common and "special" fields are stored respectively.

Both header and body contain fields to which the contract is cryptographically committed ("commitment fields") – and fields that do not participate in the generation of the cryptographic commitment. The latter can be either permanent or prunnable; the permanent fields are required for the contract verification process and need to be transferred to other peers. Prunnable fields are computable fields, they serve utilitary function, optimising the speed of data retrieval from Bitcoin Core node. Prunnable fields are optional, they MAY be transferred upon request from one peer to other (alike witness data in bitcoin blocks), however peers are MAY NOT keep these data and can decline the requests for providing them from other peers.

Proof is uniquely identified by its `proof_id`, which is computed as a single SHA245-hash of the serialized commitment fields.

### Transfer proofs

Every RGB on-chain transaction will have a corresponding **proof**, where the payer stores the following information in a structured way:

* Commitment fields:
    * `version`: [version](#versioning) of the proof, 16-bit integer.
    * `upstreams`: a list containing upstream `proof_id`s (and/or `contract_id`s when the proof spends issuing output of some contract);
    * `assignments`: an array, where elements are subarrays containing list of transfers for each of the assets. Assets are ordered according to their order in the upstream proofs and contracts. For instance, if the first upstream proof transacts assets C and then B, the second A and B, then the order of asset subarrays will be "C, B, A". Each subarray for a given asset contains:
        * amount being transacted
        * [RgbOutPoint](#asset-assignments) for the asset: a UTXO for *UTXO-Based* transfers – or an index which will assign the asset to the corresponding output of the transaction *spending* the input UTXO.
    * `metadata`: an optional free field to pass over transaction meta-data that could be conditionally used by the asset contract to manipulate the transaction meaning (generally for the "meta-script" contract blueprint);
* Non-commitment non-prunable fields:
    * `original_pubkey`: (optional) If present, signifies P2C commitment scheme and provides the original public key before the tweak procedure which is needed to verify the proof commitment. Original pubkey is not a part of the commitment fields since it was explicitly included into the commitment during pay-to-contract public key tweaking procedure.
* Prunnable fields:
    * `commitment_txid`: transaction this proof is committed to. This is required field for the proofs assigning assets to a yet-unspent outputs (i.e. proofs with no downstream proofs). For historical proofs this is a redundant information, since asset spending transaction is the transaction containing the proof commitment. However, this information can be still kept in order to increase the speed of requests to Bitcoin Core.

Notes on output structure:
* Zero length for the list of outputs is used to indicate [proof of burn](#proof-of-burn)
* The amount field in the last transfer tuple for each asset type MUST BE omitted and MUST BE automatically deduced as `sum(upstreams) - sum(assignments)` for the given asset type. This allows do avoid situations where `sum(upstreams) > sum(assignments)` and  saves storage space.

The proof MUST be considered invalid as a whole if `sum(upstreams) < sum(assignments)` for any of the assets transfered by the proof.

### Asset assignments

RGB allows the sender of a commitment transaction to transfer the ownership of any asset in two slightly different ways:

* **UTXO-Based** if the receiver already owns one ore more UTXO(s) and would like to assign the asset he is about to receive to this/those UTXO(s). This allows the sender to spend the nominal Bitcoin value of the UTXO which was previously bound to the tokens however he wants (send them back to himself, make an on-chain payment, open a Lightning channel or more). The UTXO is serialized as `SHA256D(TX_HASH || OUTPUT_INDEX_AS_U32)` in order to increase the privacy of the receiver.
* **Address-Based** if the receiver prefers to receive the colored UTXO itself;

`RgbOutPoint` is an entity that encodes the receiver of some assets. It can either be bitcoin `OutPoint` entity when used in an UTXO-based transaction, to represent the pair (TX_HASH, OUTPUT_INDEX), or a 16-bit unsigned integer when used in an address-based transaction.

When serialized, one more byte is added to encode which of the two branches is being encoded. Its value must be `0x01` for UTXO-based transactions and `0x02` for address-based ones.

### Special proofs

Every contract blueprint needs a special "adaptor" proofs, that *proves* that the payer can fulfill the requirements specified by the contract itself.


## Verification Process

For some specific proof `P_n` the verification process MUST BE the following:

1. Verify internal proof consistency
2. Verify that both commitment and assignment transactions are valid Bitcoin transactions and are included into the Bitcoin blockchain at a safe depth from the chain head (this parameter can be an option for the wallet software).
3. Validate commitment: 
   * If there is at least a single `OP_RETURN` output, check that it contains appropriate commitment to the current proof
   * Otherwise, take an output defined by `fee mod count(outputs)` in the proof commitment transaction `Tc_n` and ensure that it is a P2(W)PKH or P2SH-wrapped P2WPKH output containing a key from the proof's `original_pubkey` field tweaked with the hash of serialized commitment fields of the proof.
4. Validate upstreams: request a corresponding proof for each of the `upstream` list members and
   * Recursively run the whole described validation procedure for each of them
   * Check that at least one of the outputs containing assigned assets by an upstream proof or a contract are spent as inputs of the current commitment transaction
   * The sum of assets assigned to each of such spent outputs is greater or equal than the sum of the corresponding assets in the proof `assignments` field
5. Check that the transactions referenced in the `assignments` field are existing as a valid transactions in the Bitcoin blockchain or (optionally) mempool and the referenced outputs are valid outputs for binding RGB assets.

# RGB Protocol Specification #01: Contracts and Proofs

* [Commitment Scheme](#commitment-scheme)
  * [OP_RETURN](#op_return)
  * [Pay-to-contract](#pay-to-contract)
* [Contracts](#contracts)
  * [Re-issuance](#re-issuance)
  * [Proof-of-burn](#proof-of-burn)
  * [Entity Structure](#entity-structure)
    * [Header](#header)
  * [Blueprints and versioning](#blueprints-and-versioning)
    * [Simple issuance: `0x01`](#simple-issuance-0x01)
    * [Crowdsale: `0x02`](#crowdsale-0x02)
    * [Re-issuance: `0x03`](#re-issuance-0x03)
* [Proofs](#proofs)
  * [Transfer proofs](#transfer-proofs)
  * [Special proofs](#special-proofs)
* [Structure](#structure)
  * [Address-Based vs UTXO-Based](#address-based-vs-utxo-based)
  * [RgbOutPoint](#rgboutpoint)
* [Exemplified Process Description](#exemplified-process-description)
  * [Basic Asset Issuance](#basic-asset-issuance)
  * [On-chain Asset Transfer](#on-chain-asset-transfer)
  * [Color Addition](#color-addition)

## Commitment Scheme

In order to ensure immutability and prevent double spend, it's necessary to strongly bind Bitcoin transactions to contracts and proofs, in a way that makes it impossible to modify RGB entities at a later time without invalidating the underlying transaction.

In this specification we describe two commitment schemes available in the RGB protocol, both with some useful features and drawbacks. It's up to the issuer to choose which commitment scheme suits its needs the best, by setting the `commitment_scheme` flag in the contract.

Contract MAY be deployed using different scheme than `commitment_scheme` specified in the contract header (see below).

Every later proof MUST follow the scheme chosen in the contract header.

### OP_RETURN

A transaction committing to a proof or contract using the `OP_RETURN` scheme is considered valid if:

1. There's at least one `OP_RETURN` output
2. The first `OP_RETURN` output contains a 32-bytes push which is the double SHA256 of the entity which the transaction is committing to, prefixed with `rgb:contract` (for contracts) and `rgb:proof` (for proofs) UTF-8 strings: `OP_RETURN <SHA256(SHA256('rgb:<contract|proof>' || serialized_bytecode))`

![OP_RETURN Commitment](assets/rgb_op_return_commitment.png)

The main rationale behind adding OP_RETURN scheme additionally to Pay-to-contract is that getting pay-to-contract to work with hardware wallets is non-trivial. Getting pay-to-contract to work with with most off-the-shelf HSMs (that are typically used by exchanges etc for custody) is impossible. Restricting RGB to pay-to-contract/sign-to-contract only may limit the applicability and use cases.

### Pay-to-contract

The commitment to a proof made using pay-to-contract is considered valid if:

* Given `n = fee_satoshi mod num_outputs`

1. The `n`th output pays an arbitrary amount of Bitcoin to a `P2WPKH` or a `P2PKH` (`P2PK` is considered insecure and not supported)
2. The public key of this output is tweaked using the method described below

![Pay-to-contract Commitment](assets/rgb_p2c_commitment.png)

#### Public key tweaking

The tweaking procedure has been previously described in many publications, such as [Eternity Wall's "sign-to-contract" article](https://blog.eternitywall.com/2018/04/13/sign-to-contract/). However, since the tweaking is already widely used practice ([OpenTimeStamps](https://petertodd.org/2016/opentimestamps-announcement), [merchant payments](https://arxiv.org/abs/1212.3257)) and will be even more adopted with the intruduction of [Taproot](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2018-January/015614.html), [Graphroot](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2018-February/015700.html), [MAST](https://github.com/bitcoin/bips/blob/master/bip-0114.mediawiki) and many other proposals, the hash, used for public key tweaking under one standard (like this one) can be provided to some uninformed third-party as a commitment under the other standard (like Taproot), and there is non-zero chance of a collision, when serialized RGB contract or proof will present at least a partially-valid Bitcoin script or other code that can be interpreted as a custom non-RGB script and used to attack that third-party. In order to reduce the risk, we follow the practice introduced in the [Taproot BIP proposal](https://github.com/sipa/bips/blob/bip-schnorr/bip-taproot.mediawiki#tagged-hashes) of prefixing the serialized RGB contract/proof with **two** hashes of RGB-specific tags, namely "rgb:contract" for contracts and "rgb:proof" for proofs. Two hashes are required to further reduce risk of undesirable collisions, since nowhere in the Bitcoin protocol the input of SHA256 starts with two (non-double) SHA256 hashes.

The whole algorithm thus looks in the following way
1. Serialize contract/proof with standard bitcoin transaction serialization rules: `s = consensus_serialize(<contract> -or- <proof>)`
1. Prefix it twice with a hash of a proper tag and compute double hash with ''hash<sub>tag</sub>(m)'' function indroduced in the [Taproot BIP] (https://github.com/sipa/bips/blob/bip-schnorr/bip-taproot.mediawiki#tagged-hashes) `h = hash<sub>rgb:contract/rgb:proof</sub>(s)`, where `hash<sub>tag</sub>(message) := SHA256(SHA256(tag) || SHA256(tag) || message)`
2. Compute `new_pub_key = original_pubkey + h * G`
3. Compute the address as a standard Bitcoin `P2(W)PKH` using `new_pub_key` as public key

In order to be able to spend the output later, the same procedure should be applied to the private key.

## Contracts

Contracts are entities that, once "deployed" on the Bitcoin blockchain, determine the creation of a new, unique asset with a specific set of characteristics (like total supply, divisibility, dust limit, etc.) and possibly provably linked to some kind of commitment by the Issuer.

Every asset is identified by the `asset_id`, which is the hash of some fields of the contracts.

Many different *kinds* (or *blueprints*) of contracts exist, allowing the user to choose the rules that will define how the asset is issued and, later, transferred. **Every contract kind has a specific 1-byte-long unique identifier**, which is serialized and committed to during the deployment phase, to make sure that its behaviour cannot be changed at a later time. Every blueprint also has an independent versioning system, in order to make the entire project even more "modular" (See [issue #23 on GitHub](https://github.com/rgb-org/spec/issues/23)).

### Re-issuance

Since the total supply of an asset is hard-coded into the contract itself, there's no way to change it at a later time. The only way to issue more token, thus inflating the supply, is by doing what's called a **"re-issuance"**, which basically means issuing another contract of type `0x03` (reissuance) linked to the previous one by committing it to `reissuance_utxo`. This feature can be disable by setting `reissuance_enabled` to `0`. 

### Proof-of-burn

Token owners have the ability to *burn* tokens in order to claim or redeem any of the rights associated with their tokens.

To do this, token owner have to send them to the `burn_address`, specified in the contract. The proof showing the transfer should then be published by the asset issuer itself [**extend**] to *prove* that the supply has been deflated.

### Entity Structure

Contracts are ideally made by two parts:

* Header - the area that contains all the fields common among every contract kind
* Body - the area that contains blueprint-specific fields

#### Header

The header contains the following fields:

* `version`: Version of the contract headers, 16-bit integer.
* `title`: Title of the asset contract
* `description`: (optional) Description of the asset contract
* `contract_url`: (optional) Unique url for the publication of the contract and the light-anchors
* `issuance_utxo`: The UTXO which will be spent in a transaction containing a  commitment to this contract to "deploy" it
* `network`: The Bitcoin network in use (mainnet, testnet)
* `total_supply`: Total supply, using the smallest undividable available unit, 64-bit unsigned integer
* `min_amount`: Minimum amount of tokens that can be transferred together, like a *dust limit*, 64-bit unsigned integer
* `max_hops`: Maximum number of "hops" before the reissuance (can be set to `0xFFFFFFFF` to disable this feature, which should be the default option)
* `reissuance_enabled`: Whether the re-issuance feature is enabled or not
* `reissuance_utxo`: (optional) UTXO which have to be spent to reissue tokens
* `burn_address`: The address to send tokens to in order to burn them
* `commitment_scheme`: The commitment scheme used by this contract, 0x01 for OP_RETURN, 0x02 for pay to contract scheme
* `blueprint_type`: 16-bit number representing version of the blueprint used

NB: Since with bitcoin network protocol-style serialization, used by RGB, we can't have optionals, the optional header fields should be serialized as a zero-length strings, which upon deserialization must be converted into `nil/NULL`

### Blueprints and versioning

There are two types of versioning for RGB contracts: header version (`version` field) and blueprint type (`blueprint_type` field). The difference is that header version defines a set of fields used by the contract, which might change in the future with addition of the new fields – or some fields becoming optional or changing data type. Blueprint version defines the exact type of the contract with specific fields and structure for the contract body.

#### Simple issuance: `0x01`

**Blueprint type `0x0008`**

This blueprint allows to mint `total_supply` tokens and immediately send them to `owner_utxo`.

The additional fields in the body are:

* `owner_utxo`: the UTXO which will receive all the tokens

#### Crowdsale: `0x02`

**Blueprint type `0x0008`**

This blueprint allows to set-up a crowdsale, to sell tokens at a specified price up to the `total_supply`. This contract actually creates two different assets with different `assets_id`s. Together with the "normal" token, a new "change" token is issued, to "refund" users who either send some Bitcoins too early or too late and will miss out on the crowdsale. Change tokens have a fixed 1-to-1-satoshi rate in the issuing phase, and are intended to maintain the same rate in the redeeming phase.

The additional fields in the body are:

* `deposit_address`: the address to send Bitcoins to in order to buy tokens
* `price_sat`: the price in satoshi for a single token
* `from_block`: when the crowdsale starts
* `to_block`: when the crowdsale ends

#### Re-issuance: `0x03`

**Blueprint type `0x0008`**

This blueprint allows an asset issuer to re-issue tokens by inflating the supply. This is allowed only if the original contract had `reissuance_enabled` != `0`. 

This contract MUST be issued using the `reissuance_utxo` and its version MUST match the original contract's one. 

The following fields in its header MUST be set to `0` in order to disable them:

* `title`
* `description`
* `network`
* `min_amount`
* `max_hops`
* `burn_address`
* `commitment_scheme`

The following fields MUST be filled with "real" values:

* `contract_url`: Unique url for the publication of the contract and the light-anchors
* `issuance_utxo`: The UTXO which will be spent in a transaction containing a  commitment to this contract to "deploy" it (must match the original contract's `reissuance_utxo`)
* `total_supply`: Additional supply in satoshi (1e-8)
* `reissuance_enabled`: Whether the re-issuance feature is enabled or not
* `reissuance_utxo`: (optional) UTXO which have to be spent to reissue tokens
* `version`: 16-bit number representing version of the blueprint used

There are no additional fields in its body.

## Proofs

Proofs, as the name implies, are entities that *prove* that some requirements are met. Proofs allow transfer of assets by proving the ownership of them and "connect" to contracts, by fulfilling all the conditions set in the contract itself.

Like contracts, proofs have an header and a body, where the common and "special" fields are stored respectively.

### Transfer proofs

Every RGB on-chain transaction will have a corresponding **"proof"**, where the payer stores the following information in a structured way:

* the entire chain of proofs received up to the issuance contract;
* a list of triplets made with:
	* color of the token being transacted
	* amount being transacted
	* either the hash of an UTXO in the form (TX_hash, index) to send an *UTXO-Based* transaction or an index which will bind those tokens to the corresponding output of the transaction *spending* the colored UTXO.
* an optional free field to pass over transaction meta-data that could be conditionally used by the asset contract to manipulate the transaction meaning (generally for the "meta-script" contract blueprint);

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
	"burn_address": <Address>, // The address used to burn tokens
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

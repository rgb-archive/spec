# RGB Protocol Specification #01: Contracts and Proofs

* [Contracts](#contracts)
  * [Entity Structure](#entity-structure)
    * [Header](#header)
  * [Blueprints and versioning](#blueprints-and-versioning)
    * [Simple issuance: `0x01`](#simple-issuance-0x01)
    * [Crowdsale: `0x02`](#crowdsale-0x02)
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

## Contracts

Contracts are entities that, once "deployed" on the Bitcoin blockchain, determine the creation of a new, unique asset with a specific set of charateristics (like total supply, divisibility, dust limit, etc.) and possibly provably linked to some kind of commitment by the Issuer.

Every asset is identified by the `asset_id`, which is the hash of some fields of the contracts.

Many different *kinds* (or *blueprints*) of contracts exist, allowing the user to choose the rules that will define how the asset is issued and, later, transferred. **Every contract kind has a specific 1-byte-long unique identifier**, which is serialized and committed to during the deployment phase, to make sure that its behaviour cannot be changed at a later time. Every blueprint also has an independent versioning system, in order to make the entire project even more "modular" (See [issue #23 on GitHub](https://github.com/rgb-org/spec/issues/23)).

### Entity Structure

Contracts are ideally made by two parts:

* Header - the area that contains all the fields common among every contract kind
* Body - the area that contains blueprint-specific fields

#### Header

The header contains the following fields:

* `title`: Title of the asset contract
* `description`: Description of the asset contract
* `contract_url`: Unique url for the publication of the contract and the light-anchors
* `issuance_utxo`: The UTXO which will be spent in a transaction containing a  commitment to this contract to "deploy" it
* `network`: The Bitcoin network in use (mainnet, testnet)
* `total_supply`: Total supply in satoshi (1e-8)
* `min_amount`: Minimum amount of tokens that can be transferred together, like a *dust limit*
* `max_hops`: Maximum number of "hops" before the reissuance (can be set to `0xFFFFFFFF` to disable this feature)
* `version`: 16-bit number representing version of the blueprint used

### Blueprints and versioning

#### Simple issuance: `0x01`

**Version `0x0008`**

This blueprint allows to mint `total_supply` tokens and immediately send them to `owner_utxo`.

The additional fields in the body are:

* `owner_utxo`: the UTXO which will receive all the tokens

#### Crowdsale: `0x02`

**Version `0x0008`**

This blueprint allows to set-up a crowdsale, to sell tokens at a specified price up to the `total_supply`. This contract actually creates two different assets with different `assets_id`s. Together with the "normal" token, a new "change" token is issued, to "refund" users who either send some Bitcoins too early or too late and will miss out on the crowdsale. Change tokens have a fixed 1-to-1-satoshi rate in the issuing phase, and are intended to maintain the same rate in the redeeming phase.

The additional fields in the body are:

* `deposit_address`: the address to send Bitcoins to in order to buy tokens
* `price_sat`: the price in satoshi for a single token
* `from_block`: when the crowdsale starts
* `to_block`: when the crowdsale ends

## Proofs

Proofs, as the name implies, are entities that *prove* that some requirements are met. Proofs allow transfer of assets by proving the ownership of them and "connect" to contracts, by fulfilling all the conditions set in the contract itself.

Like contracts, proofs have an header and a body, where the common and "special" fields are stored respectively.

### Transfer proofs

Every RGB on-chain transaction will have a corresponding **"proof"**, where the payer encrypts, using the payee’s dark-tag, the following information in a structured way:

* the entire chain of proofs received up to the issuance contract;
* a list of triplets made with:
	* color of the token being transacted
	* amount being transacted
	* either the hash of an UTXO in the form (TX_hash, index) to send an *UTXO-Based* transaction or an index which will bind those tokens to the corresponding output of the transaction *spending* the colored UTXO.
* an optional free field to pass over transaction meta-data that could be conditionally used by the asset contract to manipulate the transaction meaning (generally for the "meta-script" contract blueprint);

In order to help a safe and easy management of the additional data required by this feature, the dark-tag can be derived from the BIP32 derivation key that the payee is using to generate the receiving address.

**[note on safety of mixing Bitcoin and RGB addresses]**

This feature should enhance the anonymity set of asset users, making chain analysis techniques almost as difficult as ones on “plain bitcoin” transactions. The leakage of a specific transaction dark-tag gives away the path from the issuing to the transaction itself, and of the “sibling” transactions, but it preserves uncertainty about other branches.

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
	"version":{
		// Version of this contract kind to use - https://semver.org
		"major": <Integer>, // version when you make incompatible API changes
		"minor": <Integer>, // version when you add functionality in a backwards-compatible manner
		"patch": <Integer>  // version when you make backwards-compatible bug fixes
	},
	"title": <String>, // Title of the asset contract
	"description": <String>, // Description of possible reediming actions and non-script conditions
	"issuance_utxo": <String>, // The UTXO which will be spent with a commitment to this contract,
	"contract_url": <String>, // Unique url for the publication of the contract and the light-anchors
	"total_supply": <Integer>, // Total supply in satoshi (1e-8)
	"max_hops": <Integer>, // Maximum amount of onchain transfers that can be performed on the asset before reissuance
	"min_amount": <Integer>, // Minimum amount of colored satoshis that can be transfered together

	"owner_utxo": <String>, // The UTXO which will receive all the issued token. This is a contract-specific field.
}
```

2. The issuer spends the `issuance_utxo` with a commitment to this contract and publishes the contract. *`total_supply`* tokens will be created and sent to `owner_utxo`.

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

The payer also produces a new transfer proof containing:

* A list of triplets made with:
	* color of the token being transacted;
	* amount being transacted;
	* either the hash of an UTXO in the form `SHA256D(TX_HASH || OUTPUT_INDEX_AS_U32)` to send an *UTXO-Based* tx or the index of the output sent to the receiver to send an *Address-Based* tx;
* Optional meta-script-related meta-data;

The proof is hashed and included in **the first** OP_RETURN output created in the transaction.

This proof is also simmetrically encrypted with the dark-tag using AES 256 together with the entire chain of proofs up to the issuance of the token and uploaded to the storage server(s) selected by the payee.

### Color Addition
[expand]

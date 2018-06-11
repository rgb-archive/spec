# RGB Protocol Specification #01: Contracts and Proofs
* [Exemplified Process Description](#exemplified-process-description)
	* [Basic Asset Issuance](#basic-asset-issuance)
	* [On-chain Asset Transfer](#on-chain-asset-transfer)
* [Structure](#structure)
	* [Address-Based vs UTXO-Based](#address-based-vs-utxo-based)
	* [Proofs](#proofs)
	* [Color Addition](#color-addition)

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
	* either the hash of an UTXO in the form `SHA256(TX_HASH:OUTPUT_INDEX)` to send an *UTXO-Based* tx or the index of the output sent to the receiver to send an *Address-Based* tx;
* Signature(s) of the proof using the same pubkeys specified in the Bitcoin `scriptPubKey`;
* The parameter(s) used to create the signature, in order to allow the payee and the following receivers of these tokens to verify the commitment **[expand]**;
* Optional meta-script-related meta-data;

This proof is simmetrically encrypted with the dark-tag using AES 256 together with the entire chain of proofs up to the issuance of the token and uploaded to the storage server(s) selected by the payee.

Every signature performed in the transaction **should** include a commitment to the proof produced.

In the case of a multisig address spending funds at least one of the signatures **must** include a commitment to the proof.

## Structure

### Address-Based vs UTXO-Based

RGB allows the sender of a colored transaction to transfer the ownership of any asset in two slightly different ways:

* **Address-Based** if the receiver prefers to receive the colored UTXO itself;
* **UTXO-Based** if the receiver already owns one ore more UTXO(s) and would like to "bind" its new tokens he is about to receive to this/those UTXO(s). This allows the sender to spend the nominal Bitcoin value of the UTXO which was previously bound to the tokens however he wants (send them back to himself, make an on-chain payment, open a Lightning channel or more). The UTXO is serialized as `SHA256(TX_HASH:OUTPUT_INDEX)` in order to increase the privacy of the receiver.

### Proofs

Every RGB on-chain transaction will have a corresponding **"proof"**, where the payer encrypts, using the payee’s dark-tag, the following information in a structured way:

* the entire chain of proofs received up to the issuance contract;
* a list of triplets made with:
	* color of the token being transacted
	* amount being transacted
	* either the hash of an UTXO in the form (TX_hash, index) to send an *UTXO-Based* transaction or an index which will bind those tokens to the corresponding output of the transaction *spending* the colored UTXO.
* an optional free field to pass over transaction meta-data that could be conditionally used by the asset contract to manipulate the transaction meaning (generally for the "meta-script" contract blueprint);
* The parameters used to create the signature, in order to allow the payee and the following receivers of these tokens to verify the commitment **[expand]**

In order to help a safe and easy management of the additional data required by this feature, the dark-tag can be derived from the BIP32 derivation key that the payee is using to generate the receiving address.

**[note on safety of mixing Bitcoin and RGB addresses]**

This feature should enhance the anonymity set of asset users, making chain analysis techniques almost as difficult as ones on “plain bitcoin” transactions. The leakage of a specific transaction dark-tag gives away the path from the issuing to the transaction itself, and of the “sibling” transactions, but it preserves uncertainty about other branches.

### Color Addition
[expand]
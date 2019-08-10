# Quicksilver Framework

* [Overview](#overview)
  * [Definitions](#definitions)
  * [Core concepts and features](#core-concepts-and-features)
  * [Previous work](#previous-work)
* [Protocol details](#protocol-details)
  * [Single use seals](#single-use-seals)
  * [Cryptographic commitments](#cryptographic-commitments)
    * [Pay-to-contract commitments](#pay-to-contract)
    * [OP_RETURN-based commitments](#op_return-based)
  * [Schema](#schemata)
  * [Proofs](#proofs)
  * [State](#state)
    * [Multi-signature state ownership](#multi-signature-state-ownership)
    * [Proof of state destruction](#proof-of-state-destruction)
* [Data structures](#data-structures)
  * [Proof](#proof-data-structure)
  * [Seal](#seal)
  * [FlagVarInt](#flagvarint)

## Overview

Quicksilver framework allows creation of "dark" (private) state-managing systems and networks, where the **state** is, 
for instance, information on distribution and ownership of some asset; unspent balances or cross-linked immutable data 
structures. The state is shared between selected peers in a trustless manner, maintained in a form of DAG on top of 
Bitcoin blockchain. The framework can also operate on top of different Layer 2 technologies, like Lightning Network, 
Eltoo, etc.

### Definitions

Quicksilver is a framework for a distributed state, where consensus on the state is achieved using combined mechanics of 
**client-side validation** for off-chain data and verification of cryptographic commitments embedded into LNP/BP 
transaction outputs (**single-use seals**). The state is maintained in a form of size-efficient cross-linked **proofs** 
organized as a **directed acyclic graph** (DAG), stored and validated by peers without a need to trust each other.

### Core concepts and features

In order to ensure immutability and achieve consensus, it's necessary to strongly bind state changes to Bitcoin 
transaction outputs in a way that makes impossible to modify the state in any other way without invalidating it. 
This is achieved by using cryptographic commitments, i.e. by embedding commitment to the hash of the state change 
(named hereinafter a **proof**) into a Bitcoin transaction output – pretty much like it is done in the 
[OpenTimeStamps](https://opentimestamps.org/). This mechanism is called **single-use seals** and was originally proposed 
by Peter Todd.

The main distinguishing features of the framework are the following:

* Absence of a shared global state, allowing much higher scalability and better privacy. You can think of the framework
  as of a DAG or a sharding concept done properly, at the Level 2/3 above LNP/BP, without own blockchain, global state,
  economics distortions cased by token introduction etc.
* Privacy, censorship resistance and permissionlessness: data embedding points into Bitcoin blockchain are completely 
  obscure, allowing censorship resistance in terms of Bitcoin transaction mining and absence of economic incentive 
  distortion for the miners in Bitcoin network, as well as impossibility of data analysis with on-chain analysis.
* Client-side validation and data storage
* Near-zero Bitcoin blockchain pollution
* Security model fully based on the security of Bitcoin network
* Scripting model inheriting Bitcoin scripts
* Support for forthcoming Bitcoin features: Schnorr's signatures, MAST, Taproot etc
* Native support for different Layer 2 technologies

### Previous work

The initial idea for the technology comes from Peter's Todd and Giacomo Zucco concepts and ideas of proof-of-publication
timestamping (OpenTimeStamps), single-use-seals and client-side validation, as was proposed in the original concept for
Bitcoin-based asset protocol (RGB).


## Protocol details

### Single-use seals

The general principle of single-use seals is the following: the state is defined in a **proof**, which is stored offchain. 
The proof commits to its data immutability by hashing them and embedding the hash into a transaction output of a newly
created and published transaction (either by using **key-tweaking procedure** for some existing output or by creating 
a special `OP_RETURN` output). This transaction output containing the commitment is named **committed output**. 
The proof defines a set of transaction outputs (from zero up to 2^10) which are used as **seals**, meaning that 
the state defined by the associated **sealed data** (also stored the in proof) is valid only, and only until the sealed 
transaction output is not spent; i.e. by this way proof **binds** state to the UTXO set in bitcoin blockchain, and 
cryptographically commit the immutability of the binding by publishing the bitcoin transaction containing the 
commitment.

In order to modify the state bound to some of the seals in UTXOs one needs to (a) spend those UTXOs with a single 
transaction (i.e. this can only be done by the parties controlling this UTXOs, which provides a security model for
managing state changes based on Bitcoin model), (b) create a proof defining the new state and bindinb it to a new
UTXOs, (c) cryptographically commit to the proof within the same transaction that spends previous sealed UTXOs, 
(d) sign and publish the transaction and wait until it will be mined (mining may be omitted when the technology is
used on Layer 2).

UTXOs to which a state is bound (using proofs) are called **sealed UTXOs**. When the state is modified and the UTXOs
are spent, they become **unsealed txouts** and the proof unsealing them becomes **heading** proof in the DAG composed 
of all historical proofs. Historical proofs (**unsealed proofs**) are linked together through a blockchain-based history 
of unsealed and committed transaction outputs. This history can't be reconstructed without having access to a complete 
history of proofs changing same particular part of the state. Since the proofs are kept by the parties having access to 
the state, the system makes impossible to censor or analyse state chaning transactions, their history or reconstruct the 
set of state controlling parties (owners).

### Cryptographic commitments

Quicksilver uses two types of on-chain cryptographic commitment to bind the proofs immutability to immutability
properties of bitcoin transactions:
* Pay-to-contract (P2C)
* OP_RETURN-based (ORB) 

P2C commitments SHOULD BE the default type, while ORB SHOULD BE be reserved only for situations where party
producing new proof need to create the transaction with the committed output using hardware wallet without ability
to tweak the public keys with some factor (as described in [Pay-to-contract](#pay-to-contract) section).

The reason of pay-to-contract being the default type is the reduction of Bitcoin blockchain pollution with hash data 
**and** better privacy: pay-to-contract commitments are "transparent" and can't be detected using on-chain analysis.

#### Pay-to-contract

Proof commitment made with pay-to-contract (P2C) type SHOULD BE considered valid if, and only if:

* Given `f = fee_satoshi mod #(outputs)`

1. The `f`th output pays an arbitrary amount of satoshis to `P2PKH`, `P2WPKH` or `P2SH`-wrapped `P2WPKH`.
2. The public key of this output is tweaked using the method described below
3. There are no `OP_RETURN` outputs in the same transaction (this rule is 
[forced at the level of Bitcoin Core](https://github.com/bitcoin/bitcoin/blob/d0f81a96d9c158a9226dc946bdd61d48c4d42959/src/policy/policy.cpp#L131))

Otherwise, the proof MUST BE considered as an invalid and MUST NOT BE accepted; the state associated with the unsealed 
proofs MUST BE considered as lost (destroyed). 

Rationale for not supporting other types of transaction outputs for the proof commitments:
* `P2PK`: considered legacy and MUST NOT be used;
* `P2WSH`: the present version of RGB specification does not provides a way to deterministically define which of the 
   public keys are present inside the script and which are used for the commitment – however, this behaviour may change 
   in the future (see the note above);
* `P2SH`, except `P2SH`-wrapped `P2WPKH`, but not `P2SH`-wrapped `P2WSH`: the same reason as for `P2WSH`;
* `OP_RETURN` outputs can't be tweaked, since they do not contain a public key and serve pre-defined purposes only. 
   If it is necessary to commit to OP_RETURN output one should instead use [OP_RETURN commitments](#op_return-based)
*  Non-standard outputs: tweak procedure can't be standardized.

NB: since in the future (with the introduction of the future SegWit versions, like Taproot, MAST etc) the list of 
supported output types MAY change, state bound to an invalid output types MUST NOT BE considered as deterministically 
**destroyed**, but rather as **undefined**. In order to create a proper proof of state destruction a user MUST follow 
the procedure described in the [Proof of state destruction](#proof-of-state-destruction) section.

The tweaking procedure has been previously described in many publications, such as 
[Eternity Wall's "sign-to-contract" article](https://blog.eternitywall.com/2018/04/13/sign-to-contract/).
However, since the tweaking is already widely used practice 
([OpenTimeStamps](https://petertodd.org/2016/opentimestamps-announcement), 
[merchant payments](https://arxiv.org/abs/1212.3257)) and will be even more adopted with the introduction of 
[Taproot](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2018-January/015614.html), 
[Graphroot](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2018-February/015700.html), 
[MAST](https://github.com/bitcoin/bips/blob/master/bip-0114.mediawiki) and many other proposals, the hash, used for 
public key tweaking under one standard (like this one) can be provided to some uninformed third-party as a commitment 
under the other standard (like Taproot), and there is non-zero chance of a collision, when serialized proof will present 
at least a partially-valid Bitcoin script or other code that can be interpreted as a custom non-Quicksilver data 
and used to attack that third-party. In order to reduce the risk, we follow the practice introduced in the 
[Taproot BIP proposal](https://github.com/sipa/bips/blob/bip-schnorr/bip-taproot.mediawiki#tagged-hashes) of prefixing 
the proof hash with *two* hashes of Quicksilver-specific tags, namely "quicksilver". Two hashes are required to 
further reduce risk of undesirable collisions, since nowhere in the Bitcoin protocol the input of SHA256 starts with 
two (non-double) SHA256 hashes <https://github.com/sipa/bips/blob/bip-schnorr/bip-taproot.mediawiki#tagged-hashes>.

The whole algorithm thus looks in the following way:
1. Serialize proof with a procedure described in the [Proof](#proof-data-structure) section
2. Compute SHA256 hash of the serialized data, which is also will serve as a unique identifier for the proof: 
   `id = SHA256(serialized_proof)`
1. Get result of `hash(message, tag) := SHA256(SHA256(tag) || SHA256(tag) || message)` function
   (see [Taproot BIP](https://github.com/sipa/bips/blob/bip-schnorr/bip-taproot.mediawiki#tagged-hashes) for the details),
   where `message` MUST contain concatenated original public key `original_pubkey` and proof's `id`:
   `h = hash(original_pubkey || id, 'quicksilver')`
2. Compute `new_pubkey = original_pubkey + h * G`
3. Compute the address as a standard Bitcoin `P2(W)PKH` using `new_pubkey` as public key

In order to be able to spend the output later, the same procedure should be applied to the private key.

#### OP_RETURN-based

This type MUST BE used only to commit the proofs created with a special hardware (digital wallets) which is unable to
support modification of output public keys.

A transaction committed to a proof using ORB type is considered valid if:

1. There is exactly one `OP_RETURN` output (rule forced by Bitcoin Core)
2. This output contains a 32-bytes push which is SHA256 of the entity which the transaction is committing to 
   (i.e. SHA256 of serialized proof data, like in P2C commitments), prefixed with 'quicksilver' tag: 
   `OP_RETURN <SHA256('quicksilver' || SHA256(serialized_proof))>`


### Schemata

The schema in quicksilver defines the exact structure of a seal-bound state, including:
* relation between the seals pointing to transaction outputs and parts of the state
* structure for the state data and metadata 
* serialization and deserealization rules for state data and metadata (see [Proof](#proof-data-structure) section)
* rules to validate the state and state changes on top of the validation runes used by the Quicksilver

The schema can be defined in formal or an informal name. One of Quicksilver schema samples is an [RGB protocol], 
defining RGB schema for digital asset (digitalized securities, collectibles etc) issuing and transfer.

Schemata are identified by a cryptographic RIPMD160-hash of the schema name (for informally-defined schemas) or 
RIPMD160-hash of serialized formal schema definition data (see [Schema definition section]). Quicksilver-enabled user 
agents MAY use the hash to locate and download schema formal definition file (QSD) and use it in order to parse the 
sealed state and validate parts of it in relation to schema-defined state validation rules.


### Proofs

Proof consists of data that are cryptographically committed, i.e. must be preserved as immutable; and additional data,
which always may be deterministically re-computed basing on the data from the Bitcoin blockchain transactions and other
proofs. Thus, they represent the prunable part of the proof and may be discarded. The reason why it may be reasonable
to keep and transfer them is the performance: some data will require significant verification orverload in order to be
recomputed, and it will be much easier to check their correctness having the data itself than to re-compute them from
the scratch.

There are two main types of the proofs: **root proof** and normal proofs. The root proof is the source for the state, 
i.e. it represents DAG root node. Root proof MUST start with a root flag (the highest bit in the first byte = 1) and
MUST contain special additional fields absent in the rest of proofs: 
* `ver`, specifying the Quicksilver framework version used for proof serialization, interpretation and verification. 
  This field MUST BE masked with the highest bit set to `1` (to signal the root proof). The current document defines 
  version 1 for the Quicksilver framework.
* `root`, pointing to transaction output which MUST be spent and become one of the inputs for the transaction containing
  an output committed to the root proof. This mechanism is necessary to prevent possible double-publication of the root
  proof and ambiguity in the state.
* `schema`: a cryptographic RIPMD160-hash of the schema name (for informally-defined schemas) or RIPMD160-hash of 
  serialized formal schema definition data

A special form of the proof, [Proof of state destruction](#proof-of-state-destruction) can be constructed just by
creating a normal proof with zero seals.


### State

Publication of the transaction containing committed output to a root proof creates a root for the decentralized state,
changes to which will be maintained in a form of a DAG consisting of other proofs spending the sealed transaction 
outputs from the root proof.

The distributed state initialized by the root proof can be uniquely identified with the root proof id, i.e. its hash
used for the commitment procedure. This hash includes the hash of the transaction output which is spent during the
proof publication, so there is no way to publish the same proof twice and have the same id for some distributed state.

#### Multi-signature state ownership

Multi-signature state ownership is working in the same way it works for bitcoin: proofs MAY assign parts of the state 
to a `P2SH` or `P2WSH` address containing multi-signature locking script, while being committed with either P2C or ORB 
commitment to some other output within the same or other transaction.

Such state can be changed with a new proof only under the same circumstances as satoshis under this output: if the 
unlocking script will satisfy the signing conditions of the locking script.

#### Proof of state destruction

Token owners have the ability to provably and deterministically destroy parts of the state. To do this, proof owner 
having control on some parts of the state has to create a special form of the proof (**proof of state destruction**),
which is a normal proof with zero seals, and commit it with either P2C or ORB commitment. The proof MAY then be 
published in order to prove that the part of the state was really destroyed.


## Data structures

### Proof data structure

Field        | Serialized       | Committed | Optionality  | Description
------------ | ---------------- | --------- | ------------ | -----------
`ver`        | `byte`           | yes       | only in root | Version of the quicksilver protocol having the highest bit set to `1` (to signal the root proof)
`root`       | `OutPoint`       | yes       | only in root | TxOut which is to be spent as a proof of publication for the root entity. Present only if `flag == 1`
`schema`     | `RIPMD160`       | yes       | only in root | Schema ID applied to parse the `data` and `meta` fields. Present only in the root proof, i.e. if `flag == 1`
`pubkey`     | `PubKey`         | yes*      | for P2C only | Original public key before the key tweaking procedure applied
`seals`      | [`FlagVarInt`](#flagvarint)`[Seal]` | yes | obligatory | References to sealed txouts or vouts. Must always start with a highest bit = `0` in order to distinguish normal proofs from root proofs (which have the highest byte in the first bet = `1`)
`state`      | `VarInt[bytes]`  | yes       | obligatory   | Sealed state: some data structures linked to the sealed transaction outputs
`metadata`   | `VarInt[bytes]`  | yes       | obligatory   | Metadata representing additional information other then the sealed data
`parents`    | `VarInt[SHA256]` | no        | prunable     | List of parent proofs some of which seals are unsealed by the current proof (the field MAY BE added for performance reasons)
`txid`       | `TxId`           | no        | prunable     | Transaction ID that contains an output with the commitment to the proof (the field MAY BE added for performance reasons)

* — `pubkey` is committed not into a hash of the proof, but as a part of tagged [P2C commitment](#pay-to-contract).

The structure of a smallest normal P2C-committed proof will be around 38 bytes.

### Seal

Field        | Serialized   | Length (bytes)      
------------ | ------------ | ------------------
`typeflag`   | bit flag     | 1 bit
`vout`       | [`FlagVarInt`](#flagvarint) | 1..5
`txid`       | `TxId`       | 0 or 36

### FlagVarInt

FlagVarInt uses Bitcoin VarInt-like serialization format, but it reserves the highest bit from the first byte for a flag
and supports values only up to 32-bit integers. In general, it helps to save a byte on signaling some information inside
the proofs and seals and provides generally smaller size footprint for the real-world use cases addressing transaction
outputs: for transactions with 256-2^16 outputs `FlagVarInt` will result in 3-byte encoding, while `VarInt` will give a 
5-byte encoding.

```
<124 -> _ * * *   * * * * : 
=124 -> _ 1 1 1   1 1 0 0 : * * * *   * * * *
=125 -> _ 1 1 1   1 1 0 1 : * * * *   * * * * : * * * *   * * * *
=126 -> _ 1 1 1   1 1 1 0 : * * * *   * * * * : * * * *   * * * * : * * * *   * * * *
=127 -> _ 1 1 1   1 1 1 1 : * * * *   * * * * : * * * *   * * * * : * * * *   * * * * : * * * *   * * * * 
```

(* is a wildcard for bytes that can have any value, i.e. used to encode the actual integer).

Sample deserealization code:

```rust
fn parse_flagvarint() -> u32 {
    let flag_firstbyte : u8 = read_byte();
    let flag = flag_firstbyte.clone() & 0x80;
    let firstbyte = flag_firstbyte - flag;
    match firstbyte ^ 0x7F {
      0x00 => return read_byte(), // ... read and shift next bytes
      0x01 => return (read_byte() as u32)
                   + ((read_byte() as u32) << 8), // ... read and shift next 2 bytes
      0x02 => return (read_byte() as u32)
                   + ((read_byte() as u32) << 8) 
                   + ((read_byte() as u32) << 16), // ... read and shift next 3 bytes
      0x03 => return (read_byte() as u32)
                   + ((read_byte() as u32) << 8) 
                   + ((read_byte() as u32) << 16) 
                   + ((read_byte() as u32) << 24), // ... read and shift next 4 bytes
      _ => return firstbyte,
    }
}
```


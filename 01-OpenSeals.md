# OpenSeals Framework

* [Overview](#overview)
  * [Definitions](#definitions)
  * [Core concepts and features](#core-concepts-and-features)
  * [Previous work](#previous-work)
* [Protocol details](#protocol-details)
  * [Single use seals](#single-use-seals)
  * [Cryptographic commitments](#cryptographic-commitments)
    * [Deterministic definition of committed output](#deterministic-definition-of-committed-output)
    * [Pay-to-contract commitments](#pay-to-contract)
    * [OP_RETURN-based commitments](#op_return-based)
    * [Commitment versioning](#commitment-versioning)
  * [Schema](#schemata)
  * [Proofs](#proofs)
  * [State](#state)
    * [Multi-signature state ownership](#multi-signature-state-ownership)
    * [Proof of state destruction](#proof-of-state-destruction)
* [Data structures](#data-structures)
  * [Schema](#schema)
    * [MetaField](#metafield)
    * [StateType](#statetype)
    * [SealType](#sealtype)
    * [ProofType](#prooftype)
  * [Proof](#proof)
    * [Seal](#seal)
    * [FlagVarInt](#flagvarint)

## Overview

OpenSeals framework allows creation of "dark" (private) state-managing systems and networks, where the **state** is, 
for instance, information on distribution and ownership of some asset; unspent balances or cross-linked immutable data 
structures. The state is shared between selected peers in a trustless manner, maintained in a form of DAG on top of 
Bitcoin blockchain. The framework can also operate on top of different Layer 2 technologies, like Lightning Network, 
Eltoo, etc.

### Definitions

OpenSeals is a framework for a distributed state, where consensus on the state is achieved using combined mechanics of 
**client-side validation** for off-chain data and verification of cryptographic commitments embedded into LNP/BP 
transaction outputs (**single-use seals**). The state is maintained in a form of size-efficient cross-linked **proofs** 
organized as a **directed acyclic graph** (DAG), stored and validated by peers without a need to trust each other.

Proofs are dually-bounded to the Bitcoin blockchain with seals and commitments. Each proof **seals** some **state** to
particular transaction output(s) and **commits** to some transaction that spends one of the outputs sealed by 
**parent** proof(s); this process of state change is named **unsealing**. All the history of the state preceding the 
state sealed by some proof `A` is called **ancestor proofs** for `A` and forms a part of global DAG named 
**ancestry DAG** of `A`. Ancestry DAG represents subgraph of the overall DAG always starting at the same root point, 
named **root proof**, that defines initial **root state**.

Each time a transaction output sealed by some proof is spent (*unsealed*), the proof becomes **historical proof** and
a new proof defining new state must be created and committed to the transaction spending outputs of these 
*parent proofs*. From the point of view of the `X` *historical proof* the proofs that directly unseals its state is
called **child proofs**, and the whole DAG subgraph composed of all proofs unsealing at least some of the states of
the *child proofs* is named **descending graph**. **Root proof** is an origination point for a **state DAG**, which 
includes all descending proofs of the root proof.


### Core concepts and features

In order to ensure immutability and achieve consensus, it's necessary to strongly bind state changes to Bitcoin 
transaction outputs in a way that makes impossible to modify the state in any other way without invalidating it. 
This is achieved by using cryptographic commitments, i.e. by embedding commitment to the hash of the state change 
(named hereinafter a **proof**) into a Bitcoin transaction output – pretty much like it is done in the 
[OpenTimeStamps](https://opentimestamps.org/). This mechanism is called **single-use seals** and was 
[originally proposed](https://petertodd.org/2016/commitments-and-single-use-seals) by Peter Todd. This proposal extends
original concept into a more generic case.

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

The initial idea for the technology comes from Peter's Todd and Giacomo Zucco concepts and ideas of 
[proof-of-publication](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2014-December/006982.html)
timestamping ([OpenTimeStamps](https://petertodd.org/2016/opentimestamps-announcement)),
[single-use-seals](https://building-on-bitcoin.com/docs/slides/Peter_Todd_BoB_2018.pdf) 
and client-side validation, as was proposed in the original concept for
[Bitcoin-based assets](https://petertodd.org/2017/scalable-single-use-seal-asset-transfer) and 
[RGB protocol](https://github.com/rgb-org/spec/tree/74e9e196129adeae345c7b76c02a89c6814ace2f).


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
the state, the system makes impossible to censor or analyse state changing transactions, their history or reconstruct
the set of state controlling parties (owners).

### Cryptographic commitments

OpenSeals uses two types of on-chain cryptographic commitment to bind the proofs immutability to immutability
properties of bitcoin transactions:
* Pay-to-contract (P2C)
* OP_RETURN-based (ORB) 

P2C commitments SHOULD BE the default type, while ORB SHOULD BE be reserved only for situations where party
producing new proof need to create the transaction with the committed output using hardware wallet without ability
to tweak the public keys with some factor (as described in [Pay-to-contract](#pay-to-contract) section).

The reason of pay-to-contract being the default type is the reduction of Bitcoin blockchain pollution with hash data 
**and** better privacy: pay-to-contract commitments are "transparent" and can't be detected using on-chain analysis.

#### Deterministic definition of committed output

Each state seal must be unsealed only once, when the transaction output binding the state is spent. There also MUST BE 
a single deterministic way of detecting the proof assigned to the sealed state change, so it would not be possible to
create several different versions of the state change proof for the given unsealed output. In order to achieve this,
OpenSeals defines a single way to find which specific transaction output (for the transaction spending sealed outputs)
MUST contain cryptographic commitment with either P2C or ORB commitment schemes. 

The algorithm is designed in a way that helps to keep information of the output containing commitment private from any 
party which may assume that the transaction must contain such commitment. The function combines two parameters: 
* **fee amount** (`fee`): a public factor, which may be changed by the party changing the state (i.e. unsealing an   
  output with a previous state),
* **entropy from previous proof** (`entropy`): a private factor, known only to those who has an access to the history 
  of the proofs. This implies that such factor can't be changed by the party changing the state, since it's predefined 
  at the moment of sealing the parent state.

The committed output number `n` is determined by the following formula:  
`n = (fee * entropy) mod count(outputs)`

The current version of the specification uses RIPMD160 hash of the serialized proof as a source of `entropy`. 
For P2C proofs the proof is serialized _including_ the original public key field (`pubkey`). This different 
serialization and different hash type comparing to SHA256 hash used to create the commitment itself further reduces
probability for some third-party to guess the number of the actual committed output. The root proof, which has no
parent proofs, should take as an entropy value the RIPMD160 hash of the serialized schema type source to which it
commits to.

#### Pay-to-contract

Proof commitment made with pay-to-contract (P2C) type SHOULD BE considered valid if, and only if:

1. The `n`th output defined by the [deterministic committed output](#deterministic-definition-of-committed-output) 
   pays an arbitrary amount of satoshis to `P2PKH`, `P2WPKH` or `P2SH`-wrapped `P2WPKH`.
2. The public key of this output is tweaked using the method described below

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
at least a partially-valid Bitcoin script or other code that can be interpreted as a custom non-OpenSeals data 
and used to attack that third-party. In order to reduce the risk, we follow the practice introduced in the 
[Taproot BIP proposal](https://github.com/sipa/bips/blob/bip-schnorr/bip-taproot.mediawiki#tagged-hashes) of prefixing 
the proof hash with *two* hashes of OpenSeals-specific tags, namely "openseal". Two hashes are required to 
further reduce risk of undesirable collisions, since nowhere in the Bitcoin protocol the input of SHA256 starts with 
two (non-double) SHA256 hashes <https://github.com/sipa/bips/blob/bip-schnorr/bip-taproot.mediawiki#tagged-hashes>.

The whole algorithm thus looks in the following way:
1. Serialize proof with a procedure described in the [Proof](#proof) section
2. Compute SHA256 hash of the serialized data, which is also will serve as a unique identifier for the proof: 
   `id = SHA256(serialized_proof)`
1. Get result of `hash(message, tag) := SHA256(SHA256(tag) || SHA256(tag) || message)` function
   (see [Taproot BIP](https://github.com/sipa/bips/blob/bip-schnorr/bip-taproot.mediawiki#tagged-hashes) for the details),
   where `message` MUST contain concatenated original public key `original_pubkey` and proof's `id`:
   `h = hash(original_pubkey || id, 'openseal')`
2. Compute `new_pubkey = original_pubkey + h * G`
3. Compute the address as a standard Bitcoin `P2(W)PKH` using `new_pubkey` as public key

In order to be able to spend the output later, the same procedure should be applied to the private key.

#### OP_RETURN-based

This type MUST BE used only to commit the proofs created with a special hardware (digital wallets) which is unable to
support modification of output public keys.

A transaction committed to a proof using ORB type is considered valid if:

1. The `n`th output defined by the [deterministic committed output](#deterministic-definition-of-committed-output) 
   pays an arbitrary amount of satoshis to `OP_RETURN` output
2. This output contains a 32-bytes push which is SHA256 of the entity which the transaction is committing to 
   (i.e. SHA256 of serialized proof data, like in P2C commitments), prefixed with 'openseal' tag: 
   `OP_RETURN <SHA256('openseal' || SHA256(serialized_proof))>`

### Schemata

The schema in openseal defines the exact structure of a seal-bound state, including:
* relation between the seals pointing to transaction outputs and parts of the state
* structure for the state data and metadata 
* serialization and deserealization rules for state data and metadata (see [Proof data structure](#proof) section)
* rules to validate the state and state changes on top of the validation runes used by the OpenSeals

The schema can be defined in formal or an informal name. One of OpenSeals schema samples is an 
[RGB protocol](04-RGB.md), defining RGB schema for digital asset (digitalized securities, collectibles etc) issuing 
and transfer.

Schemata are identified by a cryptographic SHA256-hash of the schema name (for informally-defined schemas) or 
SHA256-hash of serialized formal schema definition data (see [Schemata definition](#schema) section).
OpenSeals-enabled user agents MAY use the hash to locate and download schema formal definition file (QSD) and use it 
in order to parse the sealed state and validate parts of it in relation to schema-defined state validation rules.


### Proofs

Proof consists of data that are cryptographically committed, i.e. must be preserved as immutable; and additional data,
which always may be deterministically re-computed basing on the data from the Bitcoin blockchain transactions and other
proofs. Thus, they represent the prunable part of the proof and may be discarded. The reason why it may be reasonable
to keep and transfer them is the performance: some data will require significant verification orverload in order to be
recomputed, and it will be much easier to check their correctness having the data itself than to re-compute them from
the scratch.

#### PRoof formats

There are four main formats of the proofs: 
* **Root proof**, which define the source for the state, i.e. it represents DAG root node. Root proof MUST start with 
  a root flag (the highest bit in the first byte = 1) followed by a second byte with `0x00` value (see 
  [prof serialization format](#proof-serialization-formats) for the details) and MUST contain special additional 
  fields absent in the rest of proofs: 
  * `ver`, specifying the OpenSeals framework version used for proof serialization, interpretation and verification. 
    This field MUST BE masked with the highest bit set to `1` .
  * `root`, pointing to transaction output which MUST be spent and become one of the inputs for the transaction containing
    an output committed to the root proof. This mechanism is necessary to prevent possible double-publication of the root
    proof and ambiguity in the state.
  * `schema`: a cryptographic SHA256-hash of the schema name (for informally-defined schemas) or SHA256-hash of 
    serialized formal schema definition data
  * `network`: Bitcoin network in use (mainnet, testnet)
* **Version upgrade proofs**, that signal OpenSeals version upgrade for all *descendant proofs* according to the
  [version upgrade procedure](#versioning). These proofs has the following additional fields:
  * `ver`, specifying a new OpenSeals framework version used for proof serialization, interpretation and verification. 
    This field MUST BE masked with the highest bit set to `1`.
  * `schema`: a cryptographic SHA256-hash of the updated schema name (for informally-defined schemas) or SHA256-hash of 
    serialized formal schema definition data. If the proof does not assign a new schema, this field must be set to
    256 zero bits.
* **Normal proofs**
* **[Proof of state destruction](#proof-of-state-destruction)** is a special form of the proof that is a normal proof 
  with zero seals.


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


### Versioning

OpenSeals framework, in order to allow future enhancements to the used commitment protocols and proof validation 
mechanics supports **versioning**.

Versioning defines:
* which cryptographic commitments are allowed and how the proofs have to be validated regarding the commitment rules;
* which format is defined for parsing serialized proofs and schema files;
* which schema version is used by the proofs.

#### Commitment and serialization versioning with `ver` field

The first two parts are defined using generic versioning field, present in *root* and *version upgrade proofs*. This

The version used by other proofs is defined by the [root proof](#proof-formats), and *state DAG* MUST by default
follow the version provided by the *root proof*. However, it is possible to update the version using special 
[**version upgrade proof**](#proof-formats), signifying that all *descendant proofs* of it must follow the new updated 
OpenSeal version.

A special attention must be paid to such version upgrades. These updates, in order to address the associated risk of
"double-spent attack" (or, multiple conflicting state changes), MUST follow very specific procedure:
1. An on-chain committed valid *version upgrade proof* defines a new version for all descending proofs **except** itself.
   This proof MUST use and MUST BE validated with the commitment scheme rules from the *previous* version.
3. All the descending proof unsealing at lease some of the seals defined by the *version upgrade proof* adapting a new
   version MUST adapt and MUST BE validated with the new commitment scheme as defined by the new version specification.
4. There is no possibility to downgrade the version of the proofs that has adopted a commitment scheme upgrade.

Creators of the *state DAG* (i.e. publishers of the *root proof*) MAY specify additional rules for version upgrade
mechanics, like presence of specially-designed normal proof signaling their support for the version upgrade (see, for
example, version upgrades in the [RGB protocol](./04-RGB.md)).

#### Schema version upgrades

The third form of versioning allows modification of the proof `meta`, `state` and `seals` format with migration to a 
newer schema version. This upgrade is performed also using *version upgrade proofs* with non-zero *schema* field
(see [proof serialization formats](#proof-serialization-formats) for more information). Unlikely commitment serialization
a schema upgrade is applied to the *version upgrade proof* as well as to all of its descendants.


## Data structures

The following chapters explain the exact data structure and serialization format for different entities which constitute
parts of OpenSeals framework.

### Schema

Schema file uniquely defines which kinds of proofs can be used for the given schema; how they can be constructed into
a DAG via different seals and which kinds of state and metadata they have to provide. First, schema defines all possible
data types for metadata fields, state and seals; than it lists definitions for proof types, which 

Field         | Serialization format    | Description
------------- | ----------------------- | -----------------------
`name`        | `String`                | Schema name (human-readable string)
`schema_ver`  | `VarInt`, `u8`, `u8`    | Schema version in [semantic versioning format](https://semver.org/)
`prev_schema` | `SHA256`                | Previous schema version reference or 256 zero-bits for the first schema definition
`meta_fields` | `VarInt[`[`MetaField`](#metafield)`]` | Definition of all possible fields with their corresponding data types that can be used in the `meta` section of the proos
`state_types` | `VarInt[`[`StateType`](#statetype)`]` | Definition of all possible state types that will be managed by the proofs
`seal_types`  | `VarInt[`[`SealType`](#sealtype)`]`   | Definition of different seal types that can be used by the proofs 
`proof_types` | `VarInt[`[`ProofType`](#prooftype)`]` | List of possible proof formats, bridging meta fields, state types and seal types together with their validation rules


#### MetaField

Metadata are composed of metafield types, which are the same as used by the normal bitcoin serialization function, like:
* `String`: first byte encodes string length, the rest — the actual string content. Zero-length strings equals to NULL
  if the optional value is implied.
* 8- to 64-bit integer
* Variable-length integer
* SHA256 and RIPMD160 hashes
* Public key (in compressed format)

Each metafield type is encoded as a tuple of `(title: str, type: u8)`, where title string is bitcoin-encoded string.
Values for each types are given in the following table:

Type       | TypeId
---------- | -------
String     | 0x00
u8         | 0x01
u16        | 0x02
u32        | 0x03
u64        | 0x04
i8         | 0x05
i16        | 0x06
i32        | 0x07
i64        | 0x08
VarInt     | 0x09
FlagVarInt | 0x0a
SHA256     | 0x10
RIPMD160   | 0x11
PubKey     | 0x12
VarInt[u8] | 0x20


#### StateType

State sealed and updated by the proofs can be of the following kinds:

* **State without a value**: this type of state may help to track proofs of some binary actions taken by owners, like 
  the proofs for the fact of asset reissuance.
* **Unspent balances**, as fractions of total value, useful as a unit of accounting. The state is stored as u64 values,
  like bitcoin satoshis, representing the minimum indivisible part of some asset. The total asset supply in this case
  MUST BE defined as one of the meta fields.
* **Array of immutable data**: TBD
* **Mutable complex single value**: TBD
* **Distributed value components**: TBD

Each state type is encoded as a tuple of `(title: str, type: u8)`, where title string is bitcoin-encoded string.
Values for each types are given in the following table:

State Type | TypeId
---------- | -------
No value   | 0x00
Balances   | 0x01


#### SealType

Since proofs can manage multiple kinds of the state at the same time, it's important to define which seals will be able
to manage which types. This is done through `SealType` data structure, consisting of tuples 
`(title: str, state_type_idx: u8`), where `state_type_idx` is the reference to the `StateType` withing the same schema 
under the corresponding index within `state_types` list.


#### ProofType

The first proof listed in the `proot_fypes` array MUST BE the type used for root proofs. The other proof types are 
defined by the type of seal they unseal; there can be only a single proof type unsealing each type of seal.

Field         | Type                    | Description
------------- | ----------------------- | ---------------------------------------
`title`       | `str`                   | Human-readable name of the proof type
`unseals`     | `VarInt`                | Index of `SealType` which has to be unsealed by the proof; must be abset for the first proof type in the list (since it is a root proof which does not unseal any data)
`meta_fields` | `VarInt[`[`FlagVarInt`](#flagvarint)`]` | Indexes of `MetaField` that can be used by this proof type (with optionality flag)
`seal_types`  | `VarInt[(VarInt, i8, i8)]` | Indexes of `SealType` that can be created by this proof type with minimum and maximum count; `-1` (`0xFF`) value signifies no minimum and no maximum limits correspondingly.



### Proof

Field        | Serialized       | Committed | Optionality  | Description
------------ | ---------------- | --------- | ------------ | -----------
`ver`        | `byte`           | yes       | optional     | Version of the OpenSeals protocol, with the highest bit always set to `1`
`flag`       | `byte`           | yes       | optional*    | Special flag specifying **version upgrade proofs** (see [Proof types](#proof-serialization-formats) below)
`schema`     | `SHA256`         | yes       | root & version upgrades | Schema ID applied to parse the `data` and `meta` fields.
`root`       | `OutPoint`       | yes       | only in root | TxOut which is to be spent as a proof of publication for the root entity.
`network`    | `byte`           | yes       | only in root | Network to which this root proof is deployed: Mainnet, testnet etc
`pubkey`     | `PubKey`         | yes**     | for P2C only | Original public key before the key tweaking procedure applied
`seals`      | [`FlagVarInt`](#flagvarint)`[Seal]` | yes | obligatory*** | References to sealed txouts or vouts. Must always start with a highest bit = `0` in order to distinguish normal proofs from root proofs (which have the highest byte in the first bet = `1`)
`state`      | `VarInt[bytes]`  | yes       | obligatory   | Sealed state: some data structures linked to the sealed transaction outputs
`metadata`   | `VarInt[bytes]`  | yes       | obligatory   | Metadata representing additional information other then the sealed data
`parents`    | `VarInt[SHA256]` | no        | prunable     | List of parent proofs some of which seals are unsealed by the current proof (the field MAY BE added for performance reasons)
`txid`       | `TxId`           | no        | prunable     | Transaction ID that contains an output with the commitment to the proof (the field MAY BE added for performance reasons)

* - MUST BE present if the highest bit of the `ver` is set to `1` (see [Proof types](#proof-serialization-formats) below)
** — `pubkey` is committed not into a hash of the proof, but as a part of tagged [P2C commitment](#pay-to-contract).
*** — has zero member for [proofs of state destruction](#proof-of-state-destruction)

This serialization format is designed in a way that allows to maintain the smallest size for *normal proofs*, to reduce
necessary off-chain data storage as much as possible. Our estimation for a size of a smallest normal P2C-committed proof 
is around 38 bytes.

#### Proof serialization formats

Proofs by their serialization structure may be one of the following types:
* **Root proofs** having the highest bit of the first byte of the proof is set to `1`, the rest of bits representing
  OpenSeals framework version used to parse the proof, which are followed by `0x00` byte. In other words, root proofs
  are defined by `1*** **** 0000 0000`binary signature of the first two bytes (where `*` denotes any possible value for 
  the corresponding bit).
* **Version upgrade proofs** having the highest bit of the first byte of the proof is set to `1`, the rest of bits 
  representing OpenSeals framework version used to parse all descendant proofs. The first byte MUST BE followed by
  which are followed by `0xFF` byte. In other words, root proofs are defined by `1*** **** 1111 1111`binary signature of 
  the first two bytes (where `*` denotes any possible value for the corresponding bit). Version upgrade proofs are used
  to signify [upgrades of the OpenSeals version](#versioning). If the proof does not provides a new schema, the schema
  field MUST BE set to 256 zero bits.
* **Normal proofs** and **proofs of state destruction** having binary signature in form of `0*** ****`.

#### Seal

Field        | Serialized   | Length (bytes)      
------------ | ------------ | ------------------
`typeflag`   | bit flag     | 1 bit
`vout`       | [`FlagVarInt`](#flagvarint) | 1..5
`txid`       | `TxId`       | 0 or 36

#### FlagVarInt

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


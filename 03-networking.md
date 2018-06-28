# RGB Protocol Specification #03: Networking - Bifröst

* [Exchange of proofs](#exchange-of-proofs)
* [Transport layer](#transport-layer)
* [Protocol](#protocol)
  * [The `push` message](#the-push-message)
  * [The `get_by_pk_hash` message](#the-get_by_pk_hash-message)
  * [The `get_by_txid` message](#the-get_by_txid-message)
  * [The `blob` message](#the-blob-message)
* [Privacy concerns](#privacy-concerns)
  * [Connecting through Tor](#connecting-through-tor)
* [Notes](#notes)

## Exchange of proofs

The networking section describes how wallets should exchange chain of proofs when sending on-chain RGB transactions. 

The process described here involves a set of trustless third-party servers, acting as a temporary "storage" server. The payer, after the creation of a new transfer proof and the broadcast of the corresponding Bitcoin tranasction, will upload the newly-created proof, together with the chain of proofs up to the contract, to the servers specified by the payee in its invoice (TODO: reference to wallet chapter).

## Introduction

We propose a method inspired by BIPs [157](https://github.com/bitcoin/bips/blob/master/bip-0157.mediawiki) & [158](https://github.com/bitcoin/bips/blob/master/bip-0157.mediawiki) (client-side filtering): the archive server will pack multiple blobs received into ideal "blocks", one for each block seen on the Bitcoin blockchain.

## Structure

Archive servers will have a static Bitcoin public key, which is going to be used by clients to detect/prevent MITM attacks and verify filer header signatures.

### Filter Header

The filter header is designed to be very small and easy to download/store, while at the same time provide some informations about the blobs contained in a block.

Headers create a chain, which is obviously much "weaker" compared to Bitcoin's blockchain, but it still gives the client confidence in the fact that the chain has not been changed since the last time the headers have been synced.

Fields included in the header are:

* `1`:`type`
* `32`:`previous_filter_hash`
* `32`:`blob_merkle_root`
* `32`:`bitcoin_block_hash`
* `4`:`number_of_blobs`
* `??`:`bit_array` `// DOES THIS MAKE SENSE?`
* `??`:`signature`

`type` is actually unused now, and MUST be always set to `0x01`. In will allow future expansion of this protocol.

`bit_array` is used as a Bloom filter bit array: it allows clients to check if a specific blob *can* be inside the filter.

`signature` is the signature of the header using the server's static public key.

### Filter Block

The filter block contains a "list" of the blobs coded in a GCS included in the block (not the blobs themselves). Blobs are indexed using a 16-byte-long hash, generally the first half of `double_sha(dark-tag)`.

See [BIP 158](https://github.com/bitcoin/bips/blob/master/bip-0157.mediawiki) for more details on the construction and querying of such data structures.

## Transport layer

To maximize interoperability with the BOLT specification, the same transport protocol described in [BOLT #8](https://github.com/lightningnetwork/lightning-rfc/blob/master/08-transport.md) is used, with a couple of changes:

1. The maximum packet length is encoded as a [bitcoin compactSize uint](https://bitcoin.org/en/developer-reference#compactsize-unsigned-integers). To maintain "retrocompatibilty" with the protocol described in BOLT #8, RGB nodes should try to decode the packet using a 16-bit length first and then, if the length MAC validation fails, try again interpreting the first bytes as compactSize uint;

2. During the [handshake phase](https://github.com/lightningnetwork/lightning-rfc/blob/master/08-transport.md#handshake-exchange), the initiator (which in RGB has no static key), will use a randomly-generated "static key"[<sup>[1]</sup>](#notes);

## Protocol

The message format is, once again, inspired by [#BOLT 1](https://github.com/lightningnetwork/lightning-rfc/blob/master/01-messaging.md#lightning-message-format): 

1. `type`: a 2-byte big-endian field indicating the type of message
2. `payload`: a variable-length payload that comprises the remainder of the message and that conforms to a format matching the `type`

### The `push` message

Pushes a blob to the server

1. type: ?? (`push`)
2. data:
    * [`16`:`key`]
    * [`compactSize uint`:`len`]
    * [`len`:`data`]

### The `getfheaders` message

### The `fheader` message

### The `getfilters` message

### The `filter` message

### The `getblocks` message

### The `block` message

### Tor support

While probably superfluous it's still important to point out that it's strongly recommended for archive server to be reachable as Tor hidden services, to increase the privacy of both the payer and payee.

## Notes

1. Theoretically, by tweaking the [handshake initialization](https://github.com/lightningnetwork/lightning-rfc/blob/master/08-transport.md#handshake-state-initialization), the "Act Three" could be entirely skipped, but it is being kept in order to allow future developments (like authentication of RGB wallets using their static public key) and maximize compatibility with LN.
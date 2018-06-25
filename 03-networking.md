# RGB Protocol Specification #03: Networking

## Exchange of proofs

The networking section describes how wallets should exchange chain of proofs when sending on-chain RGB transactions. 

The process described here involves a set of trustless third-party servers, acting as a temporary "storage" server. The payer, after the creation of a new transfer proof and the broadcast of the corresponding Bitcoin tranasction, will upload the newly-created proof, together with the chain of proofs up to the contract, to the servers specified by the payee in its invoice (TODO: reference to wallet chapter).

## Transport layer

To maximize interoperability with the BOLT specification, the same transport protocol described in [BOLT #8](https://github.com/lightningnetwork/lightning-rfc/blob/master/08-transport.md) is used, with a couple of changes:

1. The maximum packet length is encoded as a [bitcoin compactSize uint](https://bitcoin.org/en/developer-reference#compactsize-unsigned-integers). To maintain "retrocompatibilty" with the protocol described in BOLT #8, RGB nodes should try to decode the packet using a 16-bit length first and then, if the length MAC validation fails, try again interpreting the first bytes as compactSize uint;

2. During the [handshake phase](https://github.com/lightningnetwork/lightning-rfc/blob/master/08-transport.md#handshake-exchange), the initiator (which in RGB has no static key), will use a randomly-generated "static key"[<sup>[1]</sup>](#notes);

## Protocol

### The `push` message

Pushes a blob to the server

1. type: 2064 (`push`)
2. data:
    * [`32`:`orig_pubkey_hash`]
    * [`32`:`txid`]
    * [`compactSize uint`:`len`]
    * [`len`:`data`]

### The `get_by_pk_hash` message

Returns (if found) the blob matching a pubkey hash

1. type: 2080 (`get_by_pk_hash`)
2. data:
    * [`32`:`orig_pubkey_hash`]

### The `get_by_txid` message

Returns (if found) the blob matching a txid

1. type: 2080 (`get_by_txid`)
2. data:
    * [`32`:`txid `]

## Notes

1. Theoretically, by tweaking the [handshake initialization](), the "Act Three" could be entirely skipped, but it is being kept in order to allow future developments (like authentication of RGB wallets using their static public key) and maximize compatibility with LN.
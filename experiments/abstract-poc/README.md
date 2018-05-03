# Abstract RGB Proof of Concept

The source code provided in this folder is NOT the source of the RGB node. This is just a little proof of concept that helps understanding how the chain of proof is built and, later, verified.

## How to run

To run the examples provided, install the dependencies with:

```
pip3 install -r requirements.txt
```

Then compile the protobuf definition with:

```
make
```

You can now run the examples using `python3`.

## What's inside

The `model/blockchain` folder contains the definition of many entities found in the Bitcoin field: blocks, transactions, utxos and the blockchain itself. These entities are a "placeholder" used in place of the much more complex real counterparties.

The `model/contracts` folder contains the definition of two different kind of contracts: simple contracts which are used to simply "print" tokens and send all of them to a single address and crowdsale contract, which can be used to "print" new tokens whenever a Bitcoin transaction is received on a predetermined address.

The `model/proofs` folder contains the definition of all the proofs used to move tokens around: some proofs are used as "nodes" that "connect" to a contract and fulfill  their requirements, while the simple `Proof` is used as a normal proof of transfer.
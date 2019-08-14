# RGB: Digital assets on LNP/BP stack with Quicksilver framework

The protocol allows initial and secondary issuance, upgrades, transfers of digital assets (securities, collectionables 
etc) on top of LNP/BP technology stack and [Quicksilver framework](01-Quicksilver.md). With RGB protocol the assets 
can be issued, re-issued, updated, transferred using different types of Quicksilver proofs, as defined with 
[RGB schema definition](#rgb-schema).


## Meta field types

Field           | Type         | Description
--------------- | ------------ | -----------------------------------------------------------------------
`title`         | `String`     | Title of the asset
`description`   | `String`     | Description for the asset
`contract_url`  | `String`     | Unique url for the publication of the contract and the light-anchors
`issued_supply` | `u64`        | Total issued supply, using the smallest indivisible available unit
`max_supply`    | `u64`        | A limit to the total amount of assets that may be issued by subsequent inflation contracts.
`dust_limit`    | `u32`        | Minimum amount of assets that can be transferred together, like a dust limit in Lightning Network
`signature`     | `VarInt[u8]` | Signature of the creator of the proof, which signs only committed part of the proof without the signature field


## State types

State type  | Data type | Description
----------- | --------- | --------------
`amount`    | Balance   | Asset amount
`inflation` | No value  | Right to inflate the asset supply
`upgrade`   | No value  | Right to upgrade major version number of the asset proof format
`prune`     | No value  | Right to prune parts of the asset history proofs


## Seal types

* `assets`: asset balance output. Operates `amount` state type.
* `inflation`: output for asset re-issuance. Can be set to 0 in order to disable asset re-issuance. Operates `inflation`
  state type.
* `upgrade`: output for upgrading major version number of the asset proof format. Operates `upgrade` state type.
* `pruning`: output used to prune parts of the asset history proofs. Operators `prune` state type.


## Proof types

### Initial asset issuance

Root proof type

Fields:
* `title`: obligatory
* `description`: obligatory
* `contract_url`: optional
* `issued_supply`: obligatory
* `max_supply`: optional
* `dust_limit`: optional
* `signature`: optional

Seals:
* `inflation`: 0 or 1
* `upgrade`: 1
* `pruning`: 1
* `assets`: 1 or more

### Secondary asset issuances

The proof unsealing `inflation` seals
* `issued_supply`: obligatory
* `signature`: optional

Seals:
* `inflation`: 0 or 1
* `upgrade`: 1
* `pruning`: 1
* `assets`: 1 or more

### Asset version upgrade

The proof unsealing `upgrade` seals

Seals:
* `upgrade`: 1

### Asset history checkpruning

The proof unsealing `pruning` seals

Seals:
* `upgrade`: 1
* `pruning`: 1
* `assets`: 1 or more

### Asset transfer

The proof unsealing `assets` seals

Seals:
* `assets`: 1 or more


## Schema data

```yaml
meta_fields:
  - [ 'title', 0x00 ]
  - [ 'description', 0x00 ]
  - [ 'contract_url', 0x00 ]
  - [ 'issued_supply', 0x04 ]
  - [ 'max_supply', 0x04 ]
  - [ 'dust_limit', 0x03 ]
  - [ 'signature', 0x20 ]
state_types:
  - [ 'amount', 0x01 ]
  - [ 'inflation', 0x00 ]
  - [ 'upgrade', 0x00 ]
  - [ 'prune', 0x00 ]
seal_types:
  - [ 'assets', 0x00 ]
  - [ 'inflation', 0x01 ]
  - [ 'upgrade', 0x02 ]
  - [ 'pruning', 0x03 ]
proof_types:
  - title: 'Primary issue'
    meta_fields: [ [0, 0], [1, 0], [2, 1], [3, 0], [4, 1], [5, 0], [6, 1] ]
    seal_types: [ [0, 1, -1 ], [1, 0, 1], [2, 1, 1], [3, 1, 1] ]
  - title: 'Secondary issue'
    unseals: 1
    meta_fields: [ [3, 0], [6, 1] ]
    seal_types: [ [0, 1, -1 ], [1, 0, 1], [2, 1, 1], [3, 1, 1] ]
  - title: 'Asset version upgrade'
    unseals: 2
    meta_fields: [ [0, 1, -1], [2, 1, 1], [3, 1, 1] ]
    seal_types: [ [2, 1, 1] ]
  - title: 'Asset history checkpruning'
    unseals: 3
    meta_fields: [ ]
    seal_types: [ [2, 1, 1] ]
  - title: 'Asset transfer'
    unseals: 0
    meta_fields: [ ]
    seal_types: [ [0, 1, -1] ]
```

```
 07 <title> 00 <description> 00 <contract_url> 00 <issued_supply> 04 <max_supply> 04 <dust_limit> 03 <signature> 20
 04 <amount> 01 <inflation> 00 <upgrade> 00 <prune> 00
 04 <asset> 00 <inflation> 01 <upgrade> 02 <pruning> 03
 05 <Primary issue> 07 00 00 01 00 02 01 03 00 04 01 05 00 06 01 04 00 01 FF 01 00 01 02 01 01 03 01 01
    <Secondary issue> 01 02 03 00 06 01 04 00 01 FF 01 00 01 02 01 01 03 01 01
    <Asset version upgrade> 02 03 00 01 FF 02 01 01 03 01 01 01 02 01 01
    <Asset history checkpruning> 03 00 01 02 01 01
    <Asset transfer> 00 00 01 00 01 FF
```

# RGB: Digital assets on LNP/BP stack with OpenSeals framework

The protocol allows initial and secondary issuance, upgrades, transfers of digital assets (securities, collectionables 
etc) on top of LNP/BP technology stack and [OpenSeals framework](01-OpenSeals.md). With RGB protocol the assets 
can be issued, re-issued, updated, transferred using different types of OpenSeals proofs, as defined with 
[RGB schema definition](#rgb-schema).


## Schema definition

### Meta field types

Field           | Type         | Description
--------------- | ------------ | -----------------------------------------------------------------------
`ver_major`     | `u16`        | Version number, major par
`ver_minor`     | `u8`         | -"-, minor part
`title`         | `String`     | Title of the asset
`description`   | `String`     | Description for the asset
`contract_url`  | `String`     | Unique url for the publication of the contract and the light-anchors
`max_supply`    | `u64`        | A limit to the total amount of assets that may be issued by subsequent inflation contracts.
`dust_limit`    | `u32`        | Minimum amount of assets that can be transferred together, like a dust limit in Lightning Network
`signature`     | `VarInt[u8]` | Signature of the creator of the proof, which signs only committed part of the proof without the signature field


### State types

State type  | Data type | Description
----------- | --------- | --------------
`amount`    | Balance   | Asset amount
`inflation` | No value  | Right to inflate the asset supply
`upgrade`   | No value  | Right to upgrade major version number of the asset proof format
`prune`     | No value  | Right to prune parts of the asset history proofs


### Seal types

* `assets`: asset balance output. Operates `amount` state type.
* `inflation`: output for asset re-issuance. Can be set to 0 in order to disable asset re-issuance. Operates `inflation`
  state type.
* `upgrade`: output for upgrading major version number of the asset proof format. Operates `upgrade` state type.
* `pruning`: output used to prune parts of the asset history proofs. Operators `prune` state type.


### Proof types

#### Initial asset issuance

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

#### Secondary asset issuances

The proof unsealing `inflation` seals
* `issued_supply`: obligatory
* `signature`: optional

Seals:
* `inflation`: 0 or 1
* `upgrade`: 1
* `pruning`: 1
* `assets`: 1 or more

#### Asset version upgrade

The proof unsealing `upgrade` seals

Seals:
* `upgrade`: 1

#### Asset history checkpruning

The proof unsealing `pruning` seals

Seals:
* `upgrade`: 1
* `pruning`: 1
* `assets`: 1 or more

#### Asset transfer

The proof unsealing `assets` seals

Seals:
* `assets`: 1 or more


### Schema data

```yaml
meta_fields:
  - &ver ver: fvi
  - &ver_minor ver_minor: u8
  - &title title: str
  - &description description: str
  - &url url: str
  - &max_supply max_supply: u64
  - &dust_limit dust_limit: u64
  - &signature signature: signature
seal_types:
  - &assets assets: balance
  - &inflation inflation: none
  - &upgrade upgrade: none
  - &pruning pruning: none
proof_types:
  - title: 'Primary issue'
    meta:
      - *ver: 1
      - *title: 0..1
      - *description: 0..1
      - *url: 0..1
      - *max_supply: 0..1
      - *dust_limit: 1
      - *signature: 0..1
    seals:
      - *assets: 1..
      - *inflation: 0..1
      - *upgrade: 1
      - *pruning: 1
  - title: 'Secondary issue'
    unseals: *inflation
    meta_fields:
      - *url: 0..1
      - *signature: 0..1
    seal_types:
      - *assets: 1..
      - *inflation: 0..1
      - *pruning: 1
  - title: 'Asset version upgrade'
    unseals: *upgrade
    meta_fields:
      - *ver: 1
      - *signature: 0..1
    seal_types:
      - *upgrade: 1
  - title: 'Asset history pruning'
    unseals: *pruning
    meta_fields: [ ]
    seal_types:
      - *assets: 1..
      - *pruning: 1
  - title: 'Asset transfer'
    unseals: *assets
    meta_fields:
      - *ver: 1
    seal_types:
      - *assets: 1..
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

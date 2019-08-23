# RGB: Digital assets on LNP/BP stack with OpenSeals framework

The protocol allows initial and secondary issuance, upgrades, transfers of digital assets (securities, collectionables 
etc) on top of LNP/BP technology stack and [OpenSeals framework](01-OpenSeals.md). With RGB protocol the assets 
can be issued, re-issued, updated, transferred using different types of OpenSeals proofs, as defined with 
[RGB schema definition](#rgb-schema).

## Details of implementation

### Versioning

The proofs MUST stick to the version provided by the parent proofs. If the issuers of some of the assets under the proof 
has not adopted (according to the [algotithm](#upgrade)) the highest version which is adopted by the other assets from 
the proof, these assets MUST be transferred by a separate proof.

The asset issuer must announce that he supports the update by committing to an appropriate 
[asset version upgrade proof](#asset-version-upgrade). All the asset owners which would like to upgrade the asset 
will be publishing a new **version upgrade proof** (NB: this is defined not by RGB, but by OpenSeals framework and
is different from the asset version upgrade proof) committed to the transaction in a block with bigger height that the
asset version upgrade proof. Version upgrade proof proof MUST use and MUST BE validated with the commitment rules from 
the *previous* version, as specified by the OpenSeals framework. All the descending proofs after this first 
proof adapting the new major version MUST adapt and MUST BE validated with the new commitment rules as defined by the 
new version specification.

The schema upgrade is done in the same way except that the *version upgrade proof* has to be serialized with the new
schema rules.

There is no possibility to downgrade the version of the proofs that has adopted a commitment or a scheme upgrade.

## Schema definition

### Meta field types

Field           | Type         | Description
--------------- | ------------ | -----------------------------------------------------------------------
`ticker`        | `String`     | Ticker name for the asset
`title`         | `String`     | Title of the asset
`description`   | `String`     | Description for the asset
`contract_url`  | `String`     | Unique url for the publication of the contract and the light-anchors
`max_supply`    | `u64`        | A limit to the total amount of assets that may be issued by subsequent inflation contracts.
`dust_limit`    | `u32`        | Minimum amount of assets that can be transferred together, like a dust limit in Lightning Network
`signature`     | `VarInt[u8]` | Signature of the creator of the proof, which signs only committed part of the proof without the signature field


### Seal types

* `assets`: asset balance output. Operates `balance` state.
* `inflation`: output for asset re-issuance. Can be set to 0 in order to disable asset re-issuance. 
  Has no associated state.
* `upgrade`: output for upgrading major version number of the asset proof format. Has no associated state.
* `pruning`: output used to prune parts of the asset history proofs.   Has no associated state.


### Proof types

#### Initial asset issuance

Root proof type

Fields:
* `ticker`: optional
* `title`: obligatory
* `description`: optional
* `contract_url`: optional
* `max_supply`: optional
* `dust_limit`: optional
* `signature`: optional

Seals:
* `inflation`: 0 or 1
* `upgrade`: 1
* `pruning`: 1
* `assets`: 1 or more

Issued supply of the asset is defined by the total amount sealed with `asset` seals.

#### Secondary asset issuances

The proof MUST BE unsealing exactly one `inflation` seal

The proof seals:
* `issued_supply`: obligatory
* `signature`: optional

Fields:
* `ver`: obligatory
* `schema`: obligatory; if filled with 0-bits signifies no schema upgrade

Seals:
* `inflation`: 0 or 1
* `upgrade`: 1
* `pruning`: 1
* `assets`: 1 or more

#### Asset version upgrade

The proof MUST BE unsealing exactly one `upgrade` seal

Seals:
* `upgrade`: 1

#### Asset history checkpruning

The proof MUST BE unsealing exactly one `pruning` seal

Seals:
* `upgrade`: 1
* `pruning`: 1
* `assets`: 1 or more

#### Asset transfer

The proof MUST BE unsealing at least one of `assets` seals

Seals:
* `assets`: 0 or more


### Schema data

```yaml
name: RGB
schema_ver: 1.0.0
prev_schema: 0
field_types:
  ver: u8
  schema: sha256
  ticker: str
  title: str
  description: str
  url: str
  max_supply: u64
  dust_limit: u64
  signature: signature
seal_types:
  assets: balance
  inflation: none
  upgrade: none
  pruning: none
proof_types:
  - title: Primary issue
    fields:
      ticker: optional
      title: optional
      description: optional
      url: optional
      max_supply: optional
      dust_limit: single
      signature: optional
    seals:
      assets: many
      inflation: optional
      upgrade: single
      pruning: single
  - title: Secondary issue
    unseals:
      inflation: single
    fields:
      url: optional
      signature: optional
    seals:
      assets: many
      inflation: optional
      pruning: single
  - title: Asset version upgrade
    unseals:
      upgrade: single
    fields:
      ver: single
      schema: optional
      signature: optional
    seals:
      upgrade: single
  - title: Asset history pruning
    unseals:
      pruning: single
    fields: [ ]
    seals:
      assets: many
      pruning: single
  - title: Asset transfer
    unseals:
      assets: many
    fields:
      ver: single
    seals:
      assets: any
```

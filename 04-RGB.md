# RGB: Digital assets on LNP/BP stack with Quicksilver framework

The protocol allows initial and secondary issuance, upgrades, transfers of digital assets (securities, collectionables 
etc) on top of LNP/BP technology stack and [Quicksilver framework](01-Quicksilver.md). With RGB protocol the assets 
can be issued, re-issued, updated, transferred using different types of Quicksilver proofs, as defined with 
[RGB schema definition](#rgb-schema).

## State types

State type | Data type | Sealed by | Description
---------- | --------- | --------- | --------------
`amount`   | Fraction  | `assets`  | Asset amount


## Seal types

* `inflation`: 
* `upgrade`: 
* `pruning`: 
* `assets`: amount


## Meta field types

Field           | Type         | Description
--------------- | ------------ | -------------
`title`         | `String`     | 
`description`   | `String`     | 
`contract_url`  | `String`     | 
`issued_supply` | `u64`        | 
`max_supply`    | `u64`        | 
`dust_limit`    | `u32`        | 
`signature`     | `VarInt[u8]` | 


## Proof types

### Initial asset issuance

Root proofs only

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

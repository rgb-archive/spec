# About RGB
The RGB Project is a completely free, open-source, no-profit and community-oriented effort, promoted by the BHB Network and aimed at the development of standards and best practices to issue, transmit and store "Bitcoin-based non-bitcoin" assets.
Motivations and rationale for this effort are outlined in the [Introduction document](00-introduction.md).
Basic information about the project can be provided by the developers in the [Telegram Group](https://t.me/joinchat/AgBz-Q-r2xoeQeZLsWqFUA).

# RGB Resource Map
The present repository contains, along with an [Introduction](00-introduction.md) to the RGB Project and some thoughts concerning its possible [Future Evolution](06-future-evolution.md), the specifications for the RGB standard proposal and its different modules, while the source code for the reference implementation of each module is contained in a specific repository within this same [GitHub Organization](https://github.com/rgb-org).

# RGB Protocol Specifications
1. The [Contracts](01-contracts.md) module represents the core of the protocol, documenting the low level asset logic; its reference implementation source code (written in Rust) can be found in the [RGB](https://github.com/rgb-org/rgb) repository.
2. The [Wallet](02-wallet.md) module wraps up and coordinates all the other modules, documenting the high level functions to interact with the protocol; its reference implementation source code (written in Rust) can be found in the [RGB-Wallet](https://github.com/rgb-org/rgb-wallet) repository, this module makes use of [a fork of Libwally](https://github.com/rgb-org/libwally-core), modified to include the necessary sign-to-contract low level functions.
3. The [Networking](03-networking.md) module documents the transmission, the storage and the publication of the proofs in the Client-Side-Validation paradigm; its reference implementation source code (written in Rust) can be found in the [RGB-Networking](https://github.com/rgb-org/rgb-networking) repository.
4. The [Lightning-Network Integration](04-lightning-network.md) module documents the Lightning-Network-based off-chain functionalities, like the creation, the update and the closing of asset-enabled channels and the BOLT-based routing/exchange functionalities for the assets; its reference implementation source code (written in Rust) can be found in the [RGB-Lightning-Network](https://github.com/rgb-org/rgb-lightning) repository, this module makes use of [a fork of C-Lightning](https://github.com/rgb-org/lightning), modified to include the necessary sign-to-contract low level functions and to interact with our [a fork of Libwally](https://github.com/rgb-org/libwally-core).
5. The [Proofmarshal Integration](05-proofmarshal.md) module documents another, asset-specific, layer 2 solution to improve scalability and privacy, alternative and complementary to the Lightning-Network one, based on the Proofmarshal idea; its reference implementation source code (written in Rust) can be found in the [RGB-Proofmarshal](https://github.com/rgb-org/rgb-proofmarshal) repository.

# License

![Creative Commons License](https://i.creativecommons.org/l/by/4.0/88x31.png "License CC-BY")

This work is licensed under a [Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/).

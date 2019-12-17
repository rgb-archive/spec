# About RGB

The RGB Project is a completely free, open-source, non-profit and community-oriented effort aimed at the development of 
standards and best practices to issue, transmit and store digital assets issued in LNP/BP networks.

Basic information about the project can be provided by the developers in the [RGB Telegram Group](https://t.me/rgbtelegram).

RGB is a based on a stack of LNP/BP standards, defined and being developed in the https://github.com/lnp-bp/lnpbps
repository. The current version of the specification is outdated; it will be replaced with the new one once the
required set of the underlying standards is completed.

The present parts of the RGB project under development include:
* [LNPBPS](https://github.com/lnp-bp/lnpbps): aforementioned set of core standards
* [rust-lnpbp](https://github.com/lnp-bp/lnpbps): core LNPBP library implementing LNPBPS written in Rust
* [lbx](https://github.com/lnp-bp/lbx): command-line tool for performing basic operations (commitments etc)
  defined in LNP/BP standards; based on the rust-lnpbp library
* [rust-rgb](https://github.com/rgb-org/rust-rgb): library implementing asset-specific functionality on top
  of generic client-validated state paradigm
* [Kaleidoscope](https://github.com/rgb-org/kaleidoscope): command-line wallet for Bitcoin and RGB protocols
* [Bifrost](https://github.com/rgb-org/Bifrost): server for storing client-validated data blobs. On hold.

In this repository  you can browse the most recent version under this develop branch, which existed before it was 
split into the impending layered LNP/BP standards. You can also check a history of RGB development in the 
branches of the current repo:
* [rgb-v0.4](https://github.com/rgb-org/spec/tree/old-master) branch – original specification created in 2018
  by Alekos Fillini, Giacomo Zucco and contributors
* [rgb-v0.5](https://github.com/rgb-org/spec/tree/rgb-0.5) branch – finalization on the original specification
  performed in the mid 2019 by Maxim Orlovsky

# RGB protocol old specification, v0.9
1. [OpenSeals](01-OpenSeals.md) – a framework defining distributed state management mechanics used by
   RGB to issue and account issued assets on top of LNP/BP stack.
2. [LightningNetwork](02-LightningNetwork.md) – implementation of OpenSeals for Lightning Network channels
3. [Wire protocol](03-Wire.md) – wire protocol for OpenSeals P2P node communications
4. [RGB](04-RGB.md) – digital asset issuing and management based on OpenSeals framework
5. [Spectrum](05-Spectrum.md) – Lightning Network extension for asset liquidity provisioning (DEX)
6. [ConfidentialAssets](06-ConfidentialAssets.md) – confidential assets interoperability

# Donations
Donations are welcome: `1RGB1TAg6xrUJmvWQqc5Q1SmjdLSCzdnu`

# License

![Creative Commons License](https://i.creativecommons.org/l/by/4.0/88x31.png "License CC-BY")

This work is licensed under a [Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/).

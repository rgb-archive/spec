# RGB Protocol Specification #04: Lightning Network Integration

This document describes how Lightning Network is able to support RGB with a very  little number of changes. We will refer mostly to the implementation-agnostic `lightning-rfc` and, occasionally, to source code itself (mostly `c-lightning`'s one, the reason being that we are more familiar with it. Support for `lnd` is 100% possibile planned in the future too).

A precise documentation of all the "patched" messages and parts of the code will follow soon, but in the meantime in this document we will write down the generic guidelines we plan to follow.

### Feature bits

First of all, we picked bits `8/9` of the [`features`](https://github.com/lightningnetwork/lightning-rfc/blob/master/09-features.md) bit-array to signal for RGB support. We plan to use mostly the ninth bit (so that the node will still be able to connect to "vanilla" ones), but reserving the even bit too allows to, if a node admin wants to, connect exclusively to RGB-compatbile nodes.

### Guidelines

1. Reuse the existing messages as much as possibile, to ensure compatibility with non-RGB nodes. This is very important, mostly in order to be able to rely on the nodes which don't support RGB to broadcast messages about channel creations.
2. When creating a new message type is necessary to replace a "vanilla" one, use the same `type` + a constant.

### Extra considerations

* Since the `short_channel_id` cannot be changed, we plan to treat each "colored" channel as multiple virtual channels running on top of a "physical" channel (which, has a precise `short_channel_id`). Signaling of the additional colors is challening: being compatible with the current [`channel_announcement` message](https://github.com/lightningnetwork/lightning-rfc/blob/master/07-routing-gossip.md#the-channel_announcement-message) is a huge plus, but there's very little space to pack extra informations into it. Our best bet right now, is to reserve another odd feature bit, to signal that additional info are coded into the feature bits themselves, and then use the variable-length space to encode the list of `asset_id`s running on that channel.
* Signaling fees is also pretty challenging: the [`channel_update` message](https://github.com/lightningnetwork/lightning-rfc/blob/master/07-routing-gossip.md#the-channel_update-message) has *no* variable length field, so encoding the `asset_id` is very hard. Fortunately, since in the case of colored channels we want to spread the exchange rate against bitcoin instead of a "fee" amount, we can recover 4 bytes from the `fee_base_msat` field.
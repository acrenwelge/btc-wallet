#!/bin/bash
# usage: `source setup_env_vars.sh`

# setup web sources to get blockchain data from
PYCOIN_CACHE_DIR=~/.pycoin_cache
PYCOIN_BTC_PROVIDERS="blockchain.info blockexplorer.com"
export PYCOIN_CACHE_DIR PYCOIN_BTC_PROVIDERS

# setup QUICKNODE API for blockchain communication
export QUICKNODE_API=https://floral-black-seed.btc-testnet.discover.quiknode.pro/b8903e56206c0d3570d0837e8c8ee27813d2f7cf/
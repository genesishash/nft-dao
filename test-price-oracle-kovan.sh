#!/bin/bash
export NETWORK=kovan
export WEB3_INFURA_PROJECT_ID=b7b474054fd840098a64dec665138997
export ETHERSCAN_TOKEN=1IXN9XW64WASRZMGF1QCKMS1C6W5FTKJTY
brownie run test_price_oracle --network kovan


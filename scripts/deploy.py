#!/usr/bin/python3

import os

from brownie import (
    accounts,
    cryptopunks,
    ico_token,
    erc20_token,
    stable_token,
    vault_cryptopunks,
    dao,
    price_oracle,
)

NETWORK = os.environ.get('NETWORK')

# example punks
PUNK_INDEX_FLOOR = 2
PUNK_INDEX_APE = 372
PUNK_INDEX_ALIEN = 635

def main():
  publish_source = False
  account = accounts.load('devel')

  print('Deploying on network',NETWORK)

  # deploy price oracle
  _price_oracle = price_oracle.deploy('Oracle',{'from':account},publish_source=publish_source)

  # set chainlink address in oracle
  if NETWORK == 'kovan':
    _price_oracle.set_chainlink_contract("0x9326BFA02ADD2366b30bacB125260Af641031331")
  if NETWORK == 'mainnet':
    _price_oracle.set_chainlink_contract("0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419")

  # deploy dao
  _dao = dao.deploy('DAO',{'from':account},publish_source=publish_source)

  # deploy cryptopunks contract
  _cryptopunks = cryptopunks.deploy({'from':account},publish_source=publish_source)

  # deploy stablecoin
  _stable_token = stable_token.deploy("Stablecoin","PUSD",{'from':account},publish_source=publish_source)

  # deploy vault
  _vault = vault_cryptopunks.deploy("Vault",_stable_token,_cryptopunks,_dao,_price_oracle,{"from":account},publish_source=publish_source)

  # add the vault and dao as a minter for the stablecoin
  _stable_token.addMinter(_vault,{'from':account})
  _stable_token.addMinter(_dao,{'from':account})

  # mint 2m for the dao
  _stable_token.mint(_dao,(2000000 * 10**18),{'from':account})

  print("DAO stablecoin balance:",_stable_token.balanceOf(_dao))

  # claim some punks
  _cryptopunks.getPunk(PUNK_INDEX_FLOOR,{'from':account})
  _cryptopunks.getPunk(PUNK_INDEX_APE,{'from':account})

  print("Cryptobunks balance:",_cryptopunks.balanceOf(account))

  # preview position
  print('Preview position',_vault.preview_position(PUNK_INDEX_FLOOR,{'from':account}))

  # open a new position with my ape
  _vault.open_position(PUNK_INDEX_FLOOR,{'from':account})

  # ..ui waits for deposit before borrow() is able to be called
  # ui can actually call _vault.get_punk_owner() until it's the vault address

  # deposit the punk into the vault (user does this via web3)
  _cryptopunks.transferPunk(_vault,PUNK_INDEX_FLOOR,{'from':account})

  # borrow some stablecoin against it now that we have it in vault
  _vault.borrow(PUNK_INDEX_FLOOR,(9000 * 10**18),{'from':account})

  print('Position:',_vault.show_position(PUNK_INDEX_FLOOR))

  # add some interest to this thing
  for i in range(5): _vault.tick()

  # make a payment against my floorpunk
  _vault.repay(PUNK_INDEX_FLOOR,(500 * 10**18),{'from':account})
  _vault.repay(PUNK_INDEX_FLOOR,(8500 * 10**18),{'from':account})

  print('Position:',_vault.show_position(PUNK_INDEX_FLOOR))

  # close my position
  _vault.close_position(PUNK_INDEX_FLOOR,{'from':account})

  #####################################

  # output details
  prefix = ''

  if NETWORK == 'mainnet':
    prefix = 'https://etherscan.io/address/'
  if NETWORK == 'kovan':
    prefix = 'https://kovan.etherscan.io/address/'
  if NETWORK == 'ropsten':
    prefix = 'https://ropsten.etherscan.io/address/'

  print("\n\n")

  print("wallet", prefix + str(account))
  print("_dao", prefix + str(_dao))
  print("_vault", prefix + str(_vault))
  print("_stable_token", prefix + str(_stable_token))
  print("_cryptopunks", prefix + str(_cryptopunks))
  print("_price_oracle", prefix + str(_price_oracle))

  print("\n\n")

  return True


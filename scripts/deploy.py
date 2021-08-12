#!/usr/bin/python3

import os
from brownie import (
    accounts,
    cryptopunks,
    ico_token,
    erc20_token,
    stable_token,
    vault_erc20,
    vault_cryptopunks,
    dao
)

# example punks
PUNK_INDEX_FLOOR = 2
PUNK_INDEX_APE = 635
PUNK_INDEX_ALIEN = 372

def main():
  publish_source = False
  account = accounts.load('devel')

  # deploy dao
  _dao = _dao.deploy('DAO',{'from':account},publish_source=publish_source)

  # deploy cryptopunks contract and claim a few punks
  _cryptopunks = cryptopunks.deploy({'from':account},publish_source=publish_source)

  _cryptopunks.getPunk(PUNK_INDEX_FLOOR,{'from':account})
  _cryptopunks.getPunk(PUNK_INDEX_APE,{'from':account})
  _cryptopunks.getPunk(PUNK_INDEX_ALIEN,{'from':account})

  print("Cryptobunks balance:",_cryptopunks.balanceOf(account))

  # deploy stablecoin and vault
  _stable_token = stable_token.deploy("Stablecoin","PUSD",0,{'from':account},publish_source=publish_source)
  _vault = vault_cryptopunks.deploy("Vault",_stable_token,_cryptopunks,{"from":account},publish_source=publish_source)

  # add the vault and dao as a minter for the stablecoin
  _stable_token.add_minter(_vault,{'from':account})
  _stable_token.add_minter(_dao,{'from':account})

  # mint 2m for the dao
  _stable_token.mint(dao,2000000,{'from':account})

  # open a new position with my ape
  _vault.open_position(PUNK_INDEX_APE,{'from':account})

  # ..ui waits for deposit before borrow() is able to be called
  # ui can actually call _vault.get_punk_owner() until it's the vault address

  # deposit the punk into the vault (user does this via web3)
  _cryptopunks.transferPunk(_vault,PUNK_INDEX_APE,{'from':account})

  # borrow some stablecoin against it now that we have it in vault
  _vault.borrow(PUNK_INDEX_APE,9000,{'from':account})

  # make a payment against my ape loan
  _vault.repay(PUNK_INDEX_APE,500,{'from':account})

  #####################################

  # output details
  prefix = 'https://etherscan.io/address/'
  if os.environ.get('NETWORK') == 'kovan':
    prefix = 'https://kovan.etherscan.io/address/'
  if os.environ.get('NETWORK') ==  'ropsten':
    prefix = 'https://ropsten.etherscan.io/address/'

  print("\n\n")
  print("wallet", prefix + str(account))
  print('---')
  print("_dao", prefix + str(_dao))
  print("_vault", prefix + str(_vault))
  print("_stable_token", prefix + str(_stable_token))
  print("_cryptopunks", prefix + str(_cryptopunks))

  return True


# @version ^0.2.0

# Vault Contract

from vyper.interfaces import ERC20

name: public(String[64])
owner: public(address)

stablecoin_contract: public(address)

event position_opened:
    owner: address
    index: uint256

event position_closed:
    owner: address
    index: uint256

struct Position:
    open: bool
    owner: address
    asset_type: String[64]
    asset_token: address
    asset_amount: uint256
    asset_index: uint256
    credit_limit: uint256
    credit_minted: uint256
    ctime: uint256

positions_index: uint256
positions: public(HashMap[uint256, Position])

balances: HashMap[address, uint256]
token_values: HashMap[address, uint256]

interface StableCoin:
    def mint(_to:address,_value:uint256): nonpayable

@external
def __init__(_name:String[64], _stablecoin_addr:address):
    self.name = _name
    self.owner = msg.sender
    self.stablecoin_contract = _stablecoin_addr
    self.positions_index = 0

@external
def deposit(_token_addr:address, _amount:uint256) -> bool:
    assert self.token_values[_token_addr] > 0, 'Token unsupported'
    assert ERC20(_token_addr).transferFrom(msg.sender,self,_amount), 'Token transfer failed'

    self.balances[_token_addr] += _amount

    #log Deposit(msg.sender,_token_addr,_amount)

    # @todo: determine price of asset
    # @todo: open position

    # mint coins
    StableCoin(self.stablecoin_contract).mint(msg.sender,(self.token_values[_token_addr] * _amount))

    return True

#
# open a new position
#
@external
def open_position(_token_addr:address, _amount:uint256) -> bool:
  assert self.token_values[_token_addr] > 0, 'Unsupported token'
  assert ERC20(_token_addr).transferFrom(msg.sender,self,_amount), 'Transfer failed'

  self.positions_index += 1
  self.positions[self.positions_index] = Position({
    open: True,
    owner: msg.sender,
    asset_type: 'ERC20',
    asset_token: _token_addr,
    asset_amount: _amount,
    asset_index: 0,
    credit_limit: (self.token_values[_token_addr] * _amount),
    credit_minted: 0,
    ctime: block.timestamp,
  })

  self.balances[_token_addr] += _amount

  log position_opened(msg.sender,self.positions_index)

  return True

#
# borrow against a position with credit
#
@external
def borrow(_positions_index:uint256, _amount:uint256) -> bool:
  assert msg.sender == self.positions[_positions_index].owner, 'Unauthorized'

  return True

# get the value of a token
@view
@external
def get_token_value(_token_addr:address) -> uint256:
    assert self.token_values[_token_addr] > 0, 'Unsupported token'
    return self.token_values[_token_addr]

# set the value of a token
@external
def set_token_value(_token_addr:address, _value:uint256) -> bool:
    assert msg.sender == self.owner, 'Unauthorized'
    self.token_values[_token_addr] = _value
    return True


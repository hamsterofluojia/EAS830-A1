// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "./BridgeToken.sol";

contract Destination is AccessControl {
    bytes32 public constant WARDEN_ROLE = keccak256("BRIDGE_WARDEN_ROLE");
    bytes32 public constant CREATOR_ROLE = keccak256("CREATOR_ROLE");
	mapping( address => address) public underlying_tokens;
	mapping( address => address) public wrapped_tokens;
	address[] public tokens;

	event Creation( address indexed underlying_token, address indexed wrapped_token );
	event Wrap( address indexed underlying_token, address indexed wrapped_token, address indexed to, uint256 amount );
	event Unwrap( address indexed underlying_token, address indexed wrapped_token, address frm, address indexed to, uint256 amount );

    constructor( address admin ) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(CREATOR_ROLE, admin);
        _grantRole(WARDEN_ROLE, admin);
    }

	function wrap(address _underlying_token, address _recipient, uint256 _amount ) public onlyRole(WARDEN_ROLE) {
		//YOUR CODE HERE

		// Check if the underlying asset has been registered 
    address wrappedToken = wrapped_tokens[_underlying_token];
    require(wrappedToken != address(0), "Token not registered");

    // Mint the wrapped token 
    BridgeToken(wrappedToken).mint(_recipient, _amount);

    // Emit the Wrap event with details of the transaction
    emit Wrap(_underlying_token, wrappedToken, _recipient, _amount);

	}

	function unwrap(address _wrapped_token, address _recipient, uint256 _amount ) public {
		//YOUR CODE HERE
		// Verify that the wrapped token is registered
    address underlyingToken = underlying_tokens[_wrapped_token];
    require(underlyingToken != address(0), "Wrapped token not registered");

    // Check that the caller has enough balance to burn
    require(BridgeToken(_wrapped_token).balanceOf(msg.sender) >= _amount, "Insufficient balance");

    // Burn the wrapped tokens from balance
    BridgeToken(_wrapped_token).burn(msg.sender, _amount);

    // Emit the Unwrap event 
    emit Unwrap(underlyingToken, _wrapped_token, msg.sender, _recipient, _amount);
	}

	function createToken(address _underlying_token, string memory name, string memory symbol ) public onlyRole(CREATOR_ROLE) returns(address) {
		//YOUR CODE HERE
		// Check if the underlying token has already been registered
    require(wrapped_tokens[_underlying_token] == address(0), "Token already created");

    // Deploy new BridgeToken contract 
    BridgeToken newToken = new BridgeToken(name, symbol);
    address newTokenAddress = address(newToken);

    // Register the new BridgeToken 
    underlying_tokens[newTokenAddress] = _underlying_token;
    wrapped_tokens[_underlying_token] = newTokenAddress;
    tokens.push(newTokenAddress);

    // Emit a Creation event with 
    emit Creation(_underlying_token, newTokenAddress);

    // Return the address of the newly created BridgeToken
    return newTokenAddress;
	}

}



pragma solidity >=0.6.0 <0.9.0;

contract DonateToCharity {

    address payable owner;
    uint256 public  numberOfCharities;
    uint256 public  totalAmountRaised;
    address private biggestDonator;
    uint256 private highestDonation;
    
    // The addresses of the charities should not be publicly available
    address payable[] private charities;


    // Use a modifier to restrict access to functionality
    modifier onlyOwner {
      require(msg.sender == owner, " Only the user that deployed the contract can perform this action.");
      _;
    }
    
    // You will also have to provide some means to destroy the contract and render it unusable.
    // This functionality should be available only to the user that deployed the contract.
    function destroy() public onlyOwner {
        selfdestruct(owner);
    }
    
    constructor(address payable[] memory _charities) public {
        owner = msg.sender;
        charities = _charities;
        numberOfCharities = charities.length;
        totalAmountRaised = 0;
        highestDonation = 0;
        
    }

    // When a donation has been made through the contract, an event transmitting the address
   // of the donor and the amount donated, should be emitted.
    event DonationInformation(address donatorAddress, uint amountDonated);
    
    
    // First Variation --
    function TransferFunds() {
      
    }
     
    // Use method overloading for providing two different variations of the same method that facilitates the transfer of funds 
    // Second Variation -- 
    function TransferFunds() {
        
}
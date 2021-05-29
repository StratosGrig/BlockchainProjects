pragma solidity ^0.5.0;

contract DonateToCharity {

    address payable owner;
    uint256 public  numberOfCharities;
    uint256 public  totalAmountRaised;
    address private biggestDonator;
    uint256 private highestDonation;
    
    // The addresses of the charities should not be publicly available
    address payable[] private charities;


    // Using a modifier to restrict access to functionality
    modifier onlyOwner {
      require(msg.sender == owner, " Only the user that deployed the contract can perform this action.");
      _;
    }
    
   constructor(address payable[] memory _charities) public {
        owner = msg.sender;
        charities = _charities;
        numberOfCharities = charities.length;
        totalAmountRaised = 0;
        highestDonation = 0;
        
    }

    // When a donation has been made through the contract, an event transmitting the address of the donor and the amount donated, will be emitted.
    event DonationInformation(address donatorAddress, uint amountDonated);
    
    
    // First Variation --
    function TransferFunds(address payable destinationAddress, uint charityIndex) public payable returns (uint256) {

        //  The contract should make appropriate checks if the user that originated the transfer has sufficient funds 
        //  This is done by setting the function payable.
        
        //  The contract makes appropriate checks if the charity index number that is provided is a valid one
        require(charityIndex >= 0 && charityIndex <= numberOfCharities, "Please provide a valid index number of the charity.");
        
        // The method redirects 10% of the funds to the selected charity, while transferring the rest to the destination address
        uint256 charityFunds;
        uint256 destinationFunds;
        charityFunds = (msg.value/10) ;
        destinationFunds = msg.value - charityFunds;
        
        charities[charityIndex].transfer(charityFunds);
        destinationAddress.transfer(destinationFunds);
        
        //Keep track of the total amount raised by all donations and towards any charity, collectively, and provide means for any interested party to access that information
        totalAmountRaised += charityFunds;

        // Keep track of who is the person that made the highest donation,identified by their address, along with the amount they donated. 
        
        if (charityFunds > highestDonation) {
            biggestDonator = msg.sender;
            highestDonation = charityFunds;
        }
        
        
        // When a donation has been made through the contract, an event transmitting the address of the donor and the amount donated, should be emitted
        emit DonationInformation(msg.sender, charityFunds);

        return charityFunds;
        
      
    }
     
    // Use method overloading for providing two different variations of the same method that facilitates the transfer of funds 
    // Second Variation -- 
    function TransferFunds(address payable destinationAddress, uint charityIndex, uint256 donationAmount) public payable {
        //  The contract should make appropriate checks if the user that originated the transfer has sufficient funds
        
        //  The contract should make appropriate checks if the charity index number that is provided is a valid one
        require(charityIndex >= 0 && charityIndex <= numberOfCharities, "Please provide a valid index number of the charity.");
        
        // a donation has to be at least 1% of the total transferred amount, while it cannot exceed half of the total transferred amount.
        require(donationAmount >= (msg.value/100) , "A donation has to be at least 1% of the total transferred amount.");
        require(donationAmount <= (msg.value/2), "A donation cannot exceed half the total transferred amount");
        
        
        charities[charityIndex].transfer(donationAmount);
        destinationAddress.transfer(msg.value - donationAmount);
        
        //The contract should keep track of the total amount raised by all donations (in wei) and 
        //towards any charity, collectively, and provide means for any interested party to access that information
        totalAmountRaised += donationAmount;

        // Keep track of who is the person that made the highest donation,identified by their address, along with the amount they donated. 
        
        if (donationAmount > highestDonation) {
            biggestDonator = msg.sender;
            highestDonation = donationAmount;
        }
        
        
        // When a donation has been made through the contract, an event transmitting the address of the donor and the amount donated, should be emitted
        emit DonationInformation(msg.sender, donationAmount);

        
    }
    
    // This information should be available with a single call to one method in the contract. It should also be available only to the user that deployed the contract.
    function getHighestDonationInfo() public onlyOwner view returns (address, uint256) {
        return (biggestDonator, highestDonation);
    }
    
    // You will also have to provide some means to destroy the contract and render it unusable.This functionality should be available only to the user that deployed the contract.
    function destroy() public onlyOwner {
        selfdestruct(owner);
    }
        
}
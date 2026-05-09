# Objective
Develop a command-line application that takes three input files

- Pricing Information - represents the service pricing and credit packages mentioned above
- Purchase Information - represents multiple customers purchasing different/same packages
-Usage Information - represents the usage information of multiple customers 
and produces an output file that shows the transaction history (purchase + usage) for each customer with their respective available credit balances.

# Additional Information

- The customer can purchase multiple packages, and upon each purchase, the associated credits are added to their account. For example, if C1 purchases both the Basic and Standard packages, they will have 350 credits.
- There is no expiry associated with the credits. You can consider them as forever.
- Services and Packages are independent of each other. Packages define how many credits a customer can purchase, and services define how many credits it consumes for a single usage.
- If the customer tries to use a service without enough credits in their account, their usage should be marked as denied, and it should be reflected in the transaction history output file.


# Ground Rules
- Use the latest version of .NET core for building this console application
- You can choose any human readable file format for the input and output files.
- Apart from using a library for parsing the file content, DO NOT USE any other libraries or frameworks to aid you.

# What we look for

- Clean Code - We care a lot about code and make sure it is clean, readable, and maintainable.
- Right abstractions - Create abstractions only if they make sense, and DO NOT OVER-ENGINEER.
- Meaningful Automation Test Cases - Test cases covering the critical aspects of the application.
- Create a README.md file - Showcasing how to run the project
- Create a thought Process file - A brief brain dump that describes how you approached this problem, things you considered or skipped, key decisions you made and the whys behind them.

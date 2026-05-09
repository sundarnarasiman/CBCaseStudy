# Graviton Billing

A .NET Core console application for processing credit-based billing transactions (purchases and usages) for Graviton SaaS.

## Requirements
- .NET 8.0 SDK

## Setup & Running

1. **Build the Application**
   ```bash
   dotnet build
   ```

2. **Run Tests**
   ```bash
   dotnet test
   ```

3. **Run the Application**
   You can run the application by providing the paths to the input JSON files and specifying an output JSON file path.
   ```bash
   dotnet run --project src/GravitonBilling.App -- pricing.json purchases.json usages.json output.json
   ```

## Input File Formats

The application expects JSON files for its inputs. 

- **pricing.json**: Contains services and credit packages.
- **purchases.json**: Array of purchase events (`customerId`, `packageName`, `occurredAt`).
- **usages.json**: Array of usage events (`customerId`, `serviceName`, `occurredAt`).

*(Note: Adding `occurredAt` ensures that transactions are processed chronologically, enabling correct "insufficient balance" handling even if events are stored out of order).*

## Output

The output will be written to the specified JSON file (e.g., `output.json`). It will contain an array of customers, their final `AvailableBalance`, and a comprehensive history of their `Transactions` (Approved and Denied).

# Thought Process

## 1. Domain Modeling
I modeled the entities (`Customer`, `ServicePricing`, `CreditPackage`, `PurchaseEvent`, `UsageEvent`, `Transaction`) separately from any file input/output concerns. This allows the core billing logic to be entirely decoupled from JSON serialization and console application specifics.

## 2. Chronological Processing (Event Sourcing lite)
To accurately deny usage when a customer runs out of credits, it's crucial to process purchases and usage in chronological order. I introduced an `OccurredAt` timestamp to the input files. The `BillingProcessor` combines purchases and usages into a single stream of `BaseEvent`, sorts them by this timestamp, and then processes them sequentially. This mimics a lightweight event-sourcing model and guarantees the correct state is calculated.

## 3. Technology Choices
- **.NET 8.0**: Latest LTS version of .NET.
- **System.Text.Json**: To adhere strictly to the rule "DO NOT USE any other libraries or frameworks", I selected JSON for all file formats because .NET Core has built-in parsing (`System.Text.Json`). If I used CSV, I would either have to write my own parser (violating the "don't reinvent the wheel / clean code" spirit) or use `CsvHelper` (violating the no 3rd party library rule).
- **xUnit**: For testing, as it's the standard .NET testing framework and is not a business logic library.

## 4. Design Decisions
- **Denied Transactions**: I log denied usages with `0` actual credit deduction but I retain the cost amount with a `Denied` status to ensure maximum visibility into what happened. 
- **Graceful Error Handling**: If a customer requests a package or service that isn't defined in the `pricing.json`, the transaction is skipped and marked as `Denied` rather than crashing the system.
- **Clean Architecture Principles**: The solution is split into three projects (`Core`, `App`, `Tests`). `Core` has zero dependencies and only pure logic. `App` handles IO. This demonstrates good abstraction without over-engineering.

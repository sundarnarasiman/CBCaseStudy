using System;
using System.Collections.Generic;
using System.Linq;
using GravitonBilling.Core.Models;

namespace GravitonBilling.Core.Services;

public class BillingProcessor
{
    private readonly PricingConfig _pricingConfig;

    public BillingProcessor(PricingConfig pricingConfig)
    {
        _pricingConfig = pricingConfig ?? throw new ArgumentNullException(nameof(pricingConfig));
    }

    public List<Customer> Process(IEnumerable<BaseEvent> events)
    {
        var customers = new Dictionary<string, Customer>();

        // Sort events chronologically to ensure correct sequence of operations
        var sortedEvents = events.OrderBy(e => e.OccurredAt).ToList();

        foreach (var ev in sortedEvents)
        {
            if (!customers.TryGetValue(ev.CustomerId, out var customer))
            {
                customer = new Customer { CustomerId = ev.CustomerId };
                customers[ev.CustomerId] = customer;
            }

            if (ev is PurchaseEvent purchaseEvent)
            {
                ProcessPurchase(customer, purchaseEvent);
            }
            else if (ev is UsageEvent usageEvent)
            {
                ProcessUsage(customer, usageEvent);
            }
        }

        return customers.Values.ToList();
    }

    private void ProcessPurchase(Customer customer, PurchaseEvent purchaseEvent)
    {
        var package = _pricingConfig.Packages.FirstOrDefault(p => p.Name.Equals(purchaseEvent.PackageName, StringComparison.OrdinalIgnoreCase));
        
        if (package == null)
        {
            customer.Transactions.Add(new Transaction
            {
                OccurredAt = purchaseEvent.OccurredAt,
                Type = TransactionType.Purchase,
                Item = purchaseEvent.PackageName,
                Credits = 0,
                Status = TransactionStatus.Denied
            });
            return;
        }

        customer.AvailableBalance += package.Credits;

        customer.Transactions.Add(new Transaction
        {
            OccurredAt = purchaseEvent.OccurredAt,
            Type = TransactionType.Purchase,
            Item = package.Name,
            Credits = package.Credits,
            Status = TransactionStatus.Approved
        });
    }

    private void ProcessUsage(Customer customer, UsageEvent usageEvent)
    {
        var service = _pricingConfig.Services.FirstOrDefault(s => s.Name.Equals(usageEvent.ServiceName, StringComparison.OrdinalIgnoreCase));

        if (service == null)
        {
            customer.Transactions.Add(new Transaction
            {
                OccurredAt = usageEvent.OccurredAt,
                Type = TransactionType.Usage,
                Item = usageEvent.ServiceName,
                Credits = 0,
                Status = TransactionStatus.Denied
            });
            return;
        }

        if (customer.AvailableBalance >= service.CreditCost)
        {
            customer.AvailableBalance -= service.CreditCost;

            customer.Transactions.Add(new Transaction
            {
                OccurredAt = usageEvent.OccurredAt,
                Type = TransactionType.Usage,
                Item = service.Name,
                Credits = -service.CreditCost,
                Status = TransactionStatus.Approved
            });
        }
        else
        {
            customer.Transactions.Add(new Transaction
            {
                OccurredAt = usageEvent.OccurredAt,
                Type = TransactionType.Usage,
                Item = service.Name,
                Credits = -service.CreditCost, // Note: Not deducted, just showing the cost
                Status = TransactionStatus.Denied
            });
        }
    }
}

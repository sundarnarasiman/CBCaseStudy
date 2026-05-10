using System;
using System.Collections.Generic;
using System.Linq;
using GravitonBilling.Core.Models;
using GravitonBilling.Core.Services;
using Xunit;

namespace GravitonBilling.Tests;

public class BillingProcessorTests
{
    private readonly PricingConfig _pricingConfig;

    public BillingProcessorTests()
    {
        _pricingConfig = new PricingConfig
        {
            Services = new List<ServicePricing>
            {
                new ServicePricing { Name = "S1", CreditCost = 1 },
                new ServicePricing { Name = "S2", CreditCost = 2 },
                new ServicePricing { Name = "S3", CreditCost = 3 }
            },
            Packages = new List<CreditPackage>
            {
                new CreditPackage { Name = "Basic", Credits = 100, Price = 100.00m },
                new CreditPackage { Name = "Standard", Credits = 250, Price = 225.00m }
            }
        };
    }

    [Fact]
    public void Process_WithValidPurchase_AddsCredits()
    {
        var processor = new BillingProcessor(_pricingConfig);
        var events = new List<BaseEvent>
        {
            new PurchaseEvent { CustomerId = "C1", PackageName = "Basic", OccurredAt = DateTime.UtcNow }
        };

        var customers = processor.Process(events);

        Assert.Single(customers);
        Assert.Equal("C1", customers[0].CustomerId);
        Assert.Equal(100, customers[0].AvailableBalance);
        Assert.Single(customers[0].Transactions);
        Assert.Equal(TransactionStatus.Approved, customers[0].Transactions[0].Status);
        Assert.Equal(100, customers[0].Transactions[0].Credits);
    }

    [Fact]
    public void Process_WithValidUsage_DeductsCredits()
    {
        var processor = new BillingProcessor(_pricingConfig);
        var baseTime = DateTime.UtcNow;
        var events = new List<BaseEvent>
        {
            new PurchaseEvent { CustomerId = "C1", PackageName = "Basic", OccurredAt = baseTime },
            new UsageEvent { CustomerId = "C1", ServiceName = "S2", OccurredAt = baseTime.AddMinutes(1) }
        };

        var customers = processor.Process(events);

        Assert.Single(customers);
        Assert.Equal(98, customers[0].AvailableBalance); // 100 - 2
        Assert.Equal(2, customers[0].Transactions.Count);
        
        var usageTransaction = customers[0].Transactions[1];
        Assert.Equal(TransactionType.Usage, usageTransaction.Type);
        Assert.Equal("S2", usageTransaction.Item);
        Assert.Equal(-2, usageTransaction.Credits);
        Assert.Equal(TransactionStatus.Approved, usageTransaction.Status);
    }

    [Fact]
    public void Process_WithInsufficientCredits_DeniesUsage()
    {
        var processor = new BillingProcessor(_pricingConfig);
        var baseTime = DateTime.UtcNow;
        var events = new List<BaseEvent>
        {
            new PurchaseEvent { CustomerId = "C1", PackageName = "Basic", OccurredAt = baseTime }, // 100
            new UsageEvent { CustomerId = "C1", ServiceName = "S1", OccurredAt = baseTime.AddMinutes(1) } // 99 (assume we purchased fewer... wait I'll add another setup)
        };
        // wait let's just make a specific test for insufficient credits
        
        var specificPricing = new PricingConfig
        {
             Services = new List<ServicePricing> { new ServicePricing { Name = "Expensive", CreditCost = 1000 } },
             Packages = new List<CreditPackage> { new CreditPackage { Name = "Small", Credits = 10, Price = 10 } }
        };
        
        var proc = new BillingProcessor(specificPricing);
        var evt = new List<BaseEvent>
        {
            new PurchaseEvent { CustomerId = "C1", PackageName = "Small", OccurredAt = baseTime },
            new UsageEvent { CustomerId = "C1", ServiceName = "Expensive", OccurredAt = baseTime.AddMinutes(1) }
        };
        
        var result = proc.Process(evt);
        Assert.Equal(10, result[0].AvailableBalance); // Still 10
        Assert.Equal(TransactionStatus.Denied, result[0].Transactions[1].Status);
    }

    [Fact]
    public void Process_SortsEventsChronologically()
    {
        var processor = new BillingProcessor(_pricingConfig);
        var baseTime = DateTime.UtcNow;
        
        // Even though Usage is first in list, its time is later
        var events = new List<BaseEvent>
        {
            new UsageEvent { CustomerId = "C1", ServiceName = "S1", OccurredAt = baseTime.AddMinutes(1) },
            new PurchaseEvent { CustomerId = "C1", PackageName = "Basic", OccurredAt = baseTime }
        };

        var customers = processor.Process(events);

        // If chronological works, S1 (cost 1) will be approved because it runs after Basic purchase (100)
        Assert.Equal(99, customers[0].AvailableBalance);
        Assert.Equal(TransactionStatus.Approved, customers[0].Transactions[0].Status); // Purchase
        Assert.Equal(TransactionStatus.Approved, customers[0].Transactions[1].Status); // Usage
    }

    [Fact]
    public void Process_UnknownPackageOrService_HandlesGracefullyAndDenies()
    {
        var processor = new BillingProcessor(_pricingConfig);
        var baseTime = DateTime.UtcNow;
        
        var events = new List<BaseEvent>
        {
            new PurchaseEvent { CustomerId = "C1", PackageName = "UnknownPack", OccurredAt = baseTime },
            new UsageEvent { CustomerId = "C1", ServiceName = "UnknownServ", OccurredAt = baseTime.AddMinutes(1) }
        };

        var customers = processor.Process(events);

        Assert.Equal(0, customers[0].AvailableBalance);
        Assert.Equal(TransactionStatus.Denied, customers[0].Transactions[0].Status);
        Assert.Equal(TransactionStatus.Denied, customers[0].Transactions[1].Status);
    }
}

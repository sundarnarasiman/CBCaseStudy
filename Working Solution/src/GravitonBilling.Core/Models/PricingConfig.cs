using System.Collections.Generic;

namespace GravitonBilling.Core.Models;

public class ServicePricing
{
    public string Name { get; set; } = string.Empty;
    public int CreditCost { get; set; }
}

public class CreditPackage
{
    public string Name { get; set; } = string.Empty;
    public int Credits { get; set; }
    public decimal Price { get; set; }
}

public class PricingConfig
{
    public List<ServicePricing> Services { get; set; } = new List<ServicePricing>();
    public List<CreditPackage> Packages { get; set; } = new List<CreditPackage>();
}

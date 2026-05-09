using System.Collections.Generic;

namespace GravitonBilling.Core.Models;

public class Customer
{
    public string CustomerId { get; set; } = string.Empty;
    public int AvailableBalance { get; set; }
    public List<Transaction> Transactions { get; set; } = new List<Transaction>();
}

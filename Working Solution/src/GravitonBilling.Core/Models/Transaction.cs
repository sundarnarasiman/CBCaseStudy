using System;

namespace GravitonBilling.Core.Models;

public class Transaction
{
    public DateTime OccurredAt { get; set; }
    public TransactionType Type { get; set; }
    public string Item { get; set; } = string.Empty;
    public int Credits { get; set; }
    public TransactionStatus Status { get; set; }
}

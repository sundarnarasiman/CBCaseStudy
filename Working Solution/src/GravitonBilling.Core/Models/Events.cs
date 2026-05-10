using System;

namespace GravitonBilling.Core.Models;

public abstract class BaseEvent
{
    public string CustomerId { get; set; } = string.Empty;
    public DateTime OccurredAt { get; set; }
}

public class PurchaseEvent : BaseEvent
{
    public string PackageName { get; set; } = string.Empty;
}

public class UsageEvent : BaseEvent
{
    public string ServiceName { get; set; } = string.Empty;
}

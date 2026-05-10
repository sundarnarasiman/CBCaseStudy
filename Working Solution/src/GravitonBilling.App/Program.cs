using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;
using GravitonBilling.Core.Models;
using GravitonBilling.Core.Services;

namespace GravitonBilling.App;

class Program
{
    static async Task Main(string[] args)
    {
        if (args.Length < 4)
        {
            Console.WriteLine("Usage: dotnet run -- <pricing.json> <purchases.json> <usages.json> <output.json>");
            return;
        }

        string pricingPath = args[0];
        string purchasesPath = args[1];
        string usagesPath = args[2];
        string outputPath = args[3];

        try
        {
            var options = new JsonSerializerOptions 
            { 
                PropertyNameCaseInsensitive = true,
                Converters = { new JsonStringEnumConverter() }
            };

            // Read inputs
            var pricingConfig = JsonSerializer.Deserialize<PricingConfig>(await File.ReadAllTextAsync(pricingPath), options) 
                                ?? new PricingConfig();
            
            var purchases = JsonSerializer.Deserialize<List<PurchaseEvent>>(await File.ReadAllTextAsync(purchasesPath), options)
                            ?? new List<PurchaseEvent>();
            
            var usages = JsonSerializer.Deserialize<List<UsageEvent>>(await File.ReadAllTextAsync(usagesPath), options)
                         ?? new List<UsageEvent>();

            // Combine events
            var allEvents = new List<BaseEvent>();
            allEvents.AddRange(purchases);
            allEvents.AddRange(usages);

            // Process
            var processor = new BillingProcessor(pricingConfig);
            var customers = processor.Process(allEvents);

            // Write output
            var outputJson = JsonSerializer.Serialize(customers, new JsonSerializerOptions 
            { 
                WriteIndented = true,
                Converters = { new JsonStringEnumConverter() }
            });
            await File.WriteAllTextAsync(outputPath, outputJson);

            Console.WriteLine($"Successfully processed billing. Output written to {outputPath}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"An error occurred: {ex.Message}");
        }
    }
}

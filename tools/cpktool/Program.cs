// cpktool — minimal CLI over CriFsV2Lib (read-only).
//   cpktool list    <file.cpk> [out.tsv]
//   cpktool extract <file.cpk> <outDir> [regex]   (regex matched against full path, case-insensitive)
using System.Text.RegularExpressions;
using CriFsV2Lib;
using CriFsV2Lib.Definitions;
using CriFsV2Lib.Definitions.Interfaces;
using CriFsV2Lib.Definitions.Structs;

if (args.Length < 2) { Console.Error.WriteLine("usage: cpktool list <cpk> [out.tsv] | extract <cpk> <outDir> [regex]"); return 1; }

var lib = CriFsLib.Instance;
var decrypt = lib.GetKnownDecryptionFunction(KnownDecryptionFunction.P5R);
string cpk = args[1];

static string FullPath(in CpkFile f) => string.IsNullOrEmpty(f.Directory) ? f.FileName : $"{f.Directory}/{f.FileName}";

CpkFile[] files;
using (var fs = new FileStream(cpk, FileMode.Open, FileAccess.Read, FileShare.Read))
using (var reader = lib.CreateCpkReader(fs, false, decrypt))
    files = reader.GetFiles();

switch (args[0])
{
    case "list":
    {
        using TextWriter w = args.Length > 2 ? new StreamWriter(args[2]) : Console.Out;
        w.WriteLine("path\tsize\textract_size\tuser_string");
        foreach (var f in files.OrderBy(f => FullPath(f), StringComparer.OrdinalIgnoreCase))
            w.WriteLine($"{FullPath(f)}\t{f.FileSize}\t{f.ExtractSize}\t{f.UserString}");
        Console.Error.WriteLine($"{files.Length} files");
        return 0;
    }
    case "extract":
    {
        string outDir = args[2];
        var rx = args.Length > 3 ? new Regex(args[3], RegexOptions.IgnoreCase) : null;
        var sel = files.Where(f => rx == null || rx.IsMatch(FullPath(f))).ToArray();
        Console.Error.WriteLine($"extracting {sel.Length}/{files.Length} files -> {outDir}");
        using var ex = lib.CreateBatchExtractor<Item>(cpk, decrypt);
        foreach (var f in sel)
            ex.QueueItem(new Item(Path.Combine(outDir, FullPath(f).Replace('/', Path.DirectorySeparatorChar)), f));
        ex.WaitForCompletion(500, () => Console.Error.Write($"\r{ex.ItemsProcessed}/{sel.Length}"));
        Console.Error.WriteLine($"\rdone: {ex.ItemsProcessed}/{sel.Length}");
        return 0;
    }
    default:
        Console.Error.WriteLine($"unknown command {args[0]}"); return 1;
}

record Item(string FullPath, CpkFile File) : IBatchFileExtractorItem;

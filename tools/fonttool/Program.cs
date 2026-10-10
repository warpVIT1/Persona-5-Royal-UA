// fonttool — dump / rebuild Atlus FNT fonts (P5R FONT0.FNT) via PersonaEditorLib.
//   fonttool dump  <in.fnt> <outDir>                       -> glyphs.bin, widths.tsv, palette.tsv, info.txt
//   fonttool build <in.fnt> <glyphs.bin> <widths.tsv> <out.fnt>
// glyphs.bin: Count glyphs, each Size2 rows of ceil(Size1*bpp/8) bytes of palette indices (as stored).
// widths.tsv: index<TAB>left<TAB>right  (visible column range of each glyph).
using System.Globalization;
using PersonaEditorLib.Other;

if (args.Length < 3) { Console.Error.WriteLine("usage: fonttool dump <fnt> <dir> | build <fnt> <glyphs.bin> <widths.tsv> <out>"); return 1; }

var fnt = new FNT(args[1]);
var g = fnt.Header.Glyphs;
switch (args[0])
{
    case "dump":
    {
        Directory.CreateDirectory(args[2]);
        var glyphs = fnt.Compressed.GetDecompressedData();
        using (var fs = File.Create(Path.Combine(args[2], "glyphs.bin")))
            foreach (var b in glyphs) fs.Write(b);
        using (var w = new StreamWriter(Path.Combine(args[2], "widths.tsv")))
            for (int i = 0; i < fnt.WidthTable.Count; i++)
                w.WriteLine($"{i}\t{fnt.WidthTable[i].Value.Left}\t{fnt.WidthTable[i].Value.Right}");
        using (var w = new StreamWriter(Path.Combine(args[2], "palette.tsv")))
        {
            var pal = fnt.Palette.Pallete;
            for (int i = 0; i < pal.Length; i++) w.WriteLine($"{i}\t{pal[i].R}\t{pal[i].G}\t{pal[i].B}\t{pal[i].A}");
        }
        File.WriteAllText(Path.Combine(args[2], "info.txt"),
            $"count\t{g.Count}\nwidth\t{g.Size1}\nheight\t{g.Size2}\nbpp\t{g.BitsPerPixel}\nglyph_bytes\t{g.ByteSize}\n" +
            $"decompressed\t{glyphs.Count}\nwidth_entries\t{fnt.WidthTable.Count}\n");
        Console.WriteLine($"{glyphs.Count} glyphs {g.Size1}x{g.Size2} {g.BitsPerPixel}bpp -> {args[2]}");
        return 0;
    }
    case "build":
    {
        byte[] all = File.ReadAllBytes(args[2]);
        int n = all.Length / g.ByteSize;
        if (n * g.ByteSize != all.Length) throw new Exception("glyphs.bin size is not a multiple of glyph size");
        if (n != g.Count) fnt.Resize(n);
        var list = new List<byte[]>();
        for (int i = 0; i < n; i++) list.Add(all.AsSpan(i * g.ByteSize, g.ByteSize).ToArray());
        fnt.Compressed.CompressData(list);
        foreach (var line in File.ReadAllLines(args[3]))
        {
            var p = line.Split('\t');
            if (p.Length < 3) continue;
            int i = int.Parse(p[0], CultureInfo.InvariantCulture);
            fnt.WidthTable[i] = new VerticalCut(byte.Parse(p[1]), byte.Parse(p[2]));
        }
        File.WriteAllBytes(args[4], fnt.GetData());
        Console.WriteLine($"{n} glyphs -> {args[4]}");
        return 0;
    }
}
Console.Error.WriteLine("unknown command"); return 1;

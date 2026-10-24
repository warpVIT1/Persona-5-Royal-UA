// Mod settings shown by Reloaded-II ("Configure Mod"). Stored as Config.json in the mod's config directory.
using System;
using System.ComponentModel;
using System.IO;
using System.Text.Json;
using System.Text.Json.Serialization;
using Reloaded.Mod.Interfaces;

namespace P5RUkr
{
    public class Config : IConfigurable
    {
        [DisplayName("Введення імені українською")]
        [Description("Ім'я, набране в українській розкладці на екрані введення імені, записується кирилицею.")]
        public bool UkrainianNameInput { get; set; } = true;

        [DisplayName("Перетворити ім'я зі старого перекладу")]
        [Description("Імена латиницею зі збережень іншого перекладу (напр. ieyhfy) перетворюються за українською " +
                     "розкладкою (шунран). Увага: справжні латинські імена (Ren) теж буде перетворено. " +
                     "Після перетворення збережіть гру.")]
        public bool ConvertOldNames { get; set; } = false;

        [Browsable(false), JsonIgnore] public string ConfigName { get; set; } = "Налаштування";
        [Browsable(false), JsonIgnore] public Action Save { get; set; }

        static readonly JsonSerializerOptions Json = new() { WriteIndented = true };

        public static Config Load(string dir)
        {
            var path = Path.Combine(dir, "Config.json");
            Config c = null;
            try { if (File.Exists(path)) c = JsonSerializer.Deserialize<Config>(File.ReadAllText(path)); } catch { }
            c ??= new Config();
            c.Save = () => { try { Directory.CreateDirectory(dir); File.WriteAllText(path, JsonSerializer.Serialize(c, Json)); } catch { } };
            return c;
        }
    }

    public class Configurator : IConfiguratorV3
    {
        string _configDir, _modDir;

        public IConfigurable[] GetConfigurations() => new IConfigurable[] { Config.Load(_configDir ?? _modDir) };
        public bool TryRunCustomConfiguration() => false;
        public void SetModDirectory(string modDirectory) => _modDir = modDirectory;
        public void SetConfigDirectory(string configDirectory) => _configDir = configDirectory;
        public void Migrate(string oldDirectory, string newDirectory) { }
        public void SetContext(in ConfiguratorContext context) { }
    }
}

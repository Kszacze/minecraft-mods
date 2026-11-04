package com.example.quickoffhand;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.item.Item;
import net.minecraft.item.Items;
import net.minecraft.registry.Registries;
import net.minecraft.util.Identifier;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class QuickOffhandConfig {
    public boolean swapWhenOccupied = false;
    public List<String> whitelist = new ArrayList<>(Arrays.asList("minecraft:shield", "minecraft:totem_of_undying"));
    
    private transient final Set<Item> resolvedWhitelist = new HashSet<>();
    private static final File FILE = new File(FabricLoader.getInstance().getConfigDir().toFile(), "quick_offhand.json");
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    public static QuickOffhandConfig INSTANCE = new QuickOffhandConfig();

    public static void load() {
        try {
            if (FILE.exists()) INSTANCE = GSON.fromJson(new FileReader(FILE), QuickOffhandConfig.class);
            else save();
        } catch (Exception e) { e.printStackTrace(); }
        INSTANCE.rebuildCache();
    }
    public static void save() {
        try (FileWriter writer = new FileWriter(FILE)) { GSON.toJson(INSTANCE, writer); } 
        catch (Exception e) { e.printStackTrace(); }
        INSTANCE.rebuildCache();
    }
    public void rebuildCache() {
        resolvedWhitelist.clear();
        for (String rawId : whitelist) {
            Identifier id = Identifier.tryParse(rawId.trim());
            if (id != null && Registries.ITEM.containsId(id)) {
                Item item = Registries.ITEM.get(id);
                if (item != Items.AIR) resolvedWhitelist.add(item);
            }
        }
    }
    public boolean isWhitelisted(Item item) { return resolvedWhitelist.contains(item); }
}
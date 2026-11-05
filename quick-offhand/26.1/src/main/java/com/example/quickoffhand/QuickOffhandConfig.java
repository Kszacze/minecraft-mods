package com.example.quickoffhand;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public final class QuickOffhandConfig {
    public boolean swapWhenOccupied = false;
    public List<String> whitelist = new ArrayList<>(Arrays.asList("minecraft:shield", "minecraft:totem_of_undying"));

    private transient final Set<Item> resolvedWhitelist = new HashSet<>();
    private static final File FILE = new File(FabricLoader.getInstance().getConfigDir().toFile(), "quick_offhand.json");
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    public static QuickOffhandConfig INSTANCE = new QuickOffhandConfig();

    public static void load() {
        if (FILE.exists()) {
            try (FileReader reader = new FileReader(FILE)) {
                QuickOffhandConfig loaded = GSON.fromJson(reader, QuickOffhandConfig.class);
                if (loaded != null) INSTANCE = loaded;
            } catch (Exception ignored) {}
        } else { save(); }
        INSTANCE.rebuildCache();
    }

    public static void save() {
        try (FileWriter writer = new FileWriter(FILE)) { GSON.toJson(INSTANCE, writer); } catch (Exception ignored) {}
        INSTANCE.rebuildCache();
    }

    public void rebuildCache() {
        resolvedWhitelist.clear();
        if (whitelist == null) return;
        for (String rawId : whitelist) {
            ResourceLocation id = ResourceLocation.tryParse(rawId.trim());
            if (id != null && BuiltInRegistries.ITEM.containsKey(id)) {
                Item item = BuiltInRegistries.ITEM.getValue(id);
                if (item != null && item != Items.AIR) resolvedWhitelist.add(item);
            }
        }
    }
    public boolean isWhitelisted(Item item) { return resolvedWhitelist.contains(item); }
}

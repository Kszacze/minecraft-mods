package com.example.crosshair;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import net.fabricmc.loader.api.FabricLoader;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;

public class CrosshairConfig {
    public float scale = 1.0f;
    public String targetColor = "#FF0000";
    public String shieldColor = "#00FF00";
    
    private static final File FILE = new File(FabricLoader.getInstance().getConfigDir().toFile(), "custom_crosshair.json");
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    public static CrosshairConfig INSTANCE = new CrosshairConfig();

    public static void load() {
        try {
            if (FILE.exists()) {
                INSTANCE = GSON.fromJson(new FileReader(FILE), CrosshairConfig.class);
            } else save();
        } catch (Exception e) { e.printStackTrace(); }
    }
    public static void save() {
        try (FileWriter writer = new FileWriter(FILE)) {
            GSON.toJson(INSTANCE, writer);
        } catch (Exception e) { e.printStackTrace(); }
    }
    
    public int getTargetColorInt() { return parseHex(targetColor); }
    public int getShieldColorInt() { return parseHex(shieldColor); }
    private int parseHex(String hex) {
        try { return (int) Long.parseLong(hex.replace("#", ""), 16) | 0xFF000000; } 
        catch (Exception e) { return 0xFFFFFFFF; }
    }
}
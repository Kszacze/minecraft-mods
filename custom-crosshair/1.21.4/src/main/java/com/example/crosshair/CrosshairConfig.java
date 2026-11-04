package com.example.crosshair;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import net.fabricmc.loader.api.FabricLoader;

import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;

public final class CrosshairConfig {
    public int scale = 1;
    public int targetColor = 0xFFFF0000;
    public int shieldColor = 0xFF00FF00;

    private static final File FILE = new File(FabricLoader.getInstance().getConfigDir().toFile(), "custom_crosshair.json");
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    public static CrosshairConfig INSTANCE = new CrosshairConfig();

    public static void load() {
        if (FILE.exists()) {
            try (FileReader reader = new FileReader(FILE)) {
                CrosshairConfig loaded = GSON.fromJson(reader, CrosshairConfig.class);
                if (loaded != null) {
                    loaded.scale = Math.max(1, Math.min(5, loaded.scale));
                    loaded.targetColor |= 0xFF000000;
                    loaded.shieldColor |= 0xFF00FF00 == loaded.shieldColor ? 0xFF000000 : 0xFF000000;
                    INSTANCE = loaded;
                }
            } catch (Exception ignored) {
            }
        } else {
            save();
        }
    }

    public static void save() {
        INSTANCE.scale = Math.max(1, Math.min(5, INSTANCE.scale));
        INSTANCE.targetColor |= 0xFF000000;
        INSTANCE.shieldColor |= 0xFF000000;
        try (FileWriter writer = new FileWriter(FILE)) {
            GSON.toJson(INSTANCE, writer);
        } catch (Exception ignored) {
        }
    }

    public static String toHex(int color) {
        return String.format("#%06X", color & 0xFFFFFF);
    }

    public static int parseHex(String text, int fallback) {
        if (text == null) return fallback;
        String clean = text.trim();
        if (clean.startsWith("#")) clean = clean.substring(1);
        if (clean.length() != 6) return fallback;
        try {
            return (Integer.parseInt(clean, 16) & 0xFFFFFF) | 0xFF000000;
        } catch (NumberFormatException e) {
            return fallback;
        }
    }
}

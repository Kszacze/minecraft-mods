import os

files = {
    ".github/workflows/build.yml": """name: Build Mods
on:
  push:
  pull_request:
  workflow_dispatch:

jobs:
  build-1-21:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '21'
      - uses: gradle/actions/setup-gradle@v3
      - name: Build 1.21.x Mods
        run: |
          cd auto-sprint-1.21 && gradle build && cd ..
          cd custom-crosshair-1.21 && gradle build && cd ..
          cd quick-offhand-1.21 && gradle build && cd ..
      - uses: actions/upload-artifact@v4
        with:
          name: mods-1.21.11
          path: |
            *-1.21/build/libs/*.jar
            !*-1.21/build/libs/*-sources.jar

  build-26:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '25'
      - uses: gradle/actions/setup-gradle@v3
      - name: Build 26.x Mods
        run: |
          cd auto-sprint-26 && gradle build && cd ..
          cd custom-crosshair-26 && gradle build && cd ..
          cd quick-offhand-26 && gradle build && cd ..
      - uses: actions/upload-artifact@v4
        with:
          name: mods-26.x
          path: |
            *-26/build/libs/*.jar
            !*-26/build/libs/*-sources.jar
""",

    # ==========================================
    # CUSTOM CROSSHAIR (1.21.11)
    # ==========================================
    "custom-crosshair-1.21/src/main/resources/fabric.mod.json": """{
  "schemaVersion": 1,
  "id": "custom_crosshair",
  "version": "${version}",
  "name": "Custom Crosshair",
  "description": "Replaces the crosshair with a simple plus that changes color when aiming at entities or shields.",
  "environment": "client",
  "entrypoints": {
    "client": [
      "com.example.crosshair.CrosshairClient"
    ],
    "modmenu": [
      "com.example.crosshair.ModMenuIntegration"
    ]
  },
  "mixins": [
    "crosshair.mixins.json"
  ],
  "depends": {
    "fabricloader": ">=0.18.0",
    "minecraft": ">=1.21 <=1.21.11",
    "java": ">=21"
  }
}
""",

    "custom-crosshair-1.21/src/main/java/com/example/crosshair/CrosshairConfig.java": """package com.example.crosshair;

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
""",

    "custom-crosshair-1.21/src/main/java/com/example/crosshair/CrosshairConfigScreen.java": """package com.example.crosshair;

import net.minecraft.client.gui.DrawContext;
import net.minecraft.client.gui.screen.Screen;
import net.minecraft.client.gui.widget.ButtonWidget;
import net.minecraft.client.gui.widget.SliderWidget;
import net.minecraft.client.gui.widget.TextFieldWidget;
import net.minecraft.text.Text;

public final class CrosshairConfigScreen extends Screen {
    private final Screen parent;
    private int scale;
    private int targetColor;
    private int shieldColor;

    private TextFieldWidget targetHexField;
    private TextFieldWidget shieldHexField;
    private boolean updatingFromSliders = false;

    private ColorChannelSlider targetR, targetG, targetB;
    private ColorChannelSlider shieldR, shieldG, shieldB;

    public CrosshairConfigScreen(Screen parent) {
        super(Text.literal("Custom Crosshair"));
        this.parent = parent;
        this.scale = CrosshairConfig.INSTANCE.scale;
        this.targetColor = CrosshairConfig.INSTANCE.targetColor;
        this.shieldColor = CrosshairConfig.INSTANCE.shieldColor;
    }

    @Override
    protected void init() {
        int cx = this.width / 2;
        int top = 28;

        // Scale Slider (1x to 5x integer pixel scale)
        this.addDrawableChild(new SliderWidget(cx - 100, top, 200, 20, Text.literal("Scale: " + this.scale + "x"), (this.scale - 1) / 4.0) {
            @Override
            protected void updateMessage() {
                this.setMessage(Text.literal("Scale: " + scale + "x"));
            }

            @Override
            protected void applyValue() {
                scale = Math.max(1, Math.min(5, 1 + (int) Math.round(this.value * 4.0)));
            }
        });

        int leftCol = cx - 155;
        int rightCol = cx + 5;
        int colY = top + 36;

        // Target Hex Field
        this.targetHexField = new TextFieldWidget(this.textRenderer, leftCol, colY, 150, 18, Text.literal("Target Hex"));
        this.targetHexField.setMaxLength(7);
        this.targetHexField.setText(CrosshairConfig.toHex(this.targetColor));
        this.targetHexField.setChangedListener(str -> {
            if (!this.updatingFromSliders) {
                int parsed = CrosshairConfig.parseHex(str, -1);
                if (parsed != -1) {
                    this.targetColor = parsed;
                    if (this.targetR != null) {
                        this.targetR.setChannelValue((parsed >> 16) & 0xFF);
                        this.targetG.setChannelValue((parsed >> 8) & 0xFF);
                        this.targetB.setChannelValue(parsed & 0xFF);
                    }
                }
            }
        });
        this.addDrawableChild(this.targetHexField);

        this.targetR = this.addDrawableChild(new ColorChannelSlider(leftCol, colY + 22, 150, 18, "R", (this.targetColor >> 16) & 0xFF, val -> updateTargetChannel(16, val)));
        this.targetG = this.addDrawableChild(new ColorChannelSlider(leftCol, colY + 42, 150, 18, "G", (this.targetColor >> 8) & 0xFF, val -> updateTargetChannel(8, val)));
        this.targetB = this.addDrawableChild(new ColorChannelSlider(leftCol, colY + 62, 150, 18, "B", this.targetColor & 0xFF, val -> updateTargetChannel(0, val)));

        // Shield Hex Field
        this.shieldHexField = new TextFieldWidget(this.textRenderer, rightCol, colY, 150, 18, Text.literal("Shield Hex"));
        this.shieldHexField.setMaxLength(7);
        this.shieldHexField.setText(CrosshairConfig.toHex(this.shieldColor));
        this.shieldHexField.setChangedListener(str -> {
            if (!this.updatingFromSliders) {
                int parsed = CrosshairConfig.parseHex(str, -1);
                if (parsed != -1) {
                    this.shieldColor = parsed;
                    if (this.shieldR != null) {
                        this.shieldR.setChannelValue((parsed >> 16) & 0xFF);
                        this.shieldG.setChannelValue((parsed >> 8) & 0xFF);
                        this.shieldB.setChannelValue(parsed & 0xFF);
                    }
                }
            }
        });
        this.addDrawableChild(this.shieldHexField);

        this.shieldR = this.addDrawableChild(new ColorChannelSlider(rightCol, colY + 22, 150, 18, "R", (this.shieldColor >> 16) & 0xFF, val -> updateShieldChannel(16, val)));
        this.shieldG = this.addDrawableChild(new ColorChannelSlider(rightCol, colY + 42, 150, 18, "G", (this.shieldColor >> 8) & 0xFF, val -> updateShieldChannel(8, val)));
        this.shieldB = this.addDrawableChild(new ColorChannelSlider(rightCol, colY + 62, 150, 18, "B", this.shieldColor & 0xFF, val -> updateShieldChannel(0, val)));

        int bottomY = this.height - 28;
        this.addDrawableChild(ButtonWidget.builder(Text.literal("Reset"), b -> {
            this.scale = 1;
            this.targetColor = 0xFFFF0000;
            this.shieldColor = 0xFF00FF00;
            this.clearAndInit();
        }).dimensions(cx - 155, bottomY, 95, 20).build());

        this.addDrawableChild(ButtonWidget.builder(Text.literal("Save & Done"), b -> {
            CrosshairConfig.INSTANCE.scale = this.scale;
            CrosshairConfig.INSTANCE.targetColor = this.targetColor;
            CrosshairConfig.INSTANCE.shieldColor = this.shieldColor;
            CrosshairConfig.save();
            if (this.client != null) this.client.setScreen(this.parent);
        }).dimensions(cx - 50, bottomY, 100, 20).build());

        this.addDrawableChild(ButtonWidget.builder(Text.literal("Cancel"), b -> {
            if (this.client != null) this.client.setScreen(this.parent);
        }).dimensions(cx + 60, bottomY, 95, 20).build());
    }

    private void updateTargetChannel(int shift, int val) {
        this.updatingFromSliders = true;
        this.targetColor = (this.targetColor & ~(0xFF << shift)) | ((val & 0xFF) << shift) | 0xFF000000;
        this.targetHexField.setText(CrosshairConfig.toHex(this.targetColor));
        this.updatingFromSliders = false;
    }

    private void updateShieldChannel(int shift, int val) {
        this.updatingFromSliders = true;
        this.shieldColor = (this.shieldColor & ~(0xFF << shift)) | ((val & 0xFF) << shift) | 0xFF000000;
        this.shieldHexField.setText(CrosshairConfig.toHex(this.shieldColor));
        this.updatingFromSliders = false;
    }

    @Override
    public void render(DrawContext context, int mouseX, int mouseY, float delta) {
        super.render(context, mouseX, mouseY, delta);
        int cx = this.width / 2;
        int colY = 64;

        context.drawCenteredTextWithShadow(this.textRenderer, this.title, cx, 10, 0xFFFFFFFF);
        context.drawTextWithShadow(this.textRenderer, "Target Color:", cx - 155, colY - 11, this.targetColor);
        context.drawTextWithShadow(this.textRenderer, "Shield Color:", cx + 5, colY - 11, this.shieldColor);

        // Live Preview Boxes (Default White, Target Color, Shield Color)
        int previewY = colY + 95;
        drawPreviewBox(context, cx - 90, previewY, 0xFFFFFFFF, "Idle");
        drawPreviewBox(context, cx, previewY, this.targetColor, "Target");
        drawPreviewBox(context, cx + 90, previewY, this.shieldColor, "Shield");
    }

    private void drawPreviewBox(DrawContext context, int x, int y, int color, String label) {
        context.fill(x - 24, y - 24, x + 25, y + 25, 0xAA000000);
        int s = this.scale;
        int half = s / 2;
        context.fill(x - 2 * s, y - half, x + 3 * s, y - half + s, color);
        context.fill(x - half, y - 2 * s, x - half + s, y - half, color);
        context.fill(x - half, y - half + s, x - half + s, y + 3 * s, color);
        context.drawCenteredTextWithShadow(this.textRenderer, label, x, y + 28, 0xFFCCCCCC);
    }

    private static final class ColorChannelSlider extends SliderWidget {
        private final String label;
        private final java.util.function.IntConsumer consumer;
        private int channelVal;

        public ColorChannelSlider(int x, int y, int width, int height, String label, int initial, java.util.function.IntConsumer consumer) {
            super(x, y, width, height, Text.literal(label + ": " + initial), initial / 255.0);
            this.label = label;
            this.channelVal = initial;
            this.consumer = consumer;
        }

        public void setChannelValue(int val) {
            this.channelVal = Math.max(0, Math.min(255, val));
            this.value = this.channelVal / 255.0;
            this.updateMessage();
        }

        @Override
        protected void updateMessage() {
            this.setMessage(Text.literal(this.label + ": " + this.channelVal));
        }

        @Override
        protected void applyValue() {
            this.channelVal = (int) Math.round(this.value * 255.0);
            this.consumer.accept(this.channelVal);
        }
    }
}
""",

    "custom-crosshair-1.21/src/main/java/com/example/crosshair/mixin/InGameHudMixin.java": """package com.example.crosshair.mixin;

import com.example.crosshair.CrosshairConfig;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.gui.DrawContext;
import net.minecraft.client.gui.hud.InGameHud;
import net.minecraft.client.render.RenderTickCounter;
import net.minecraft.entity.LivingEntity;
import net.minecraft.item.Items;
import net.minecraft.util.hit.EntityHitResult;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(InGameHud.class)
public abstract class InGameHudMixin {

    @Unique
    private static final int COLOR_WHITE = 0xFFFFFFFF;

    @Shadow
    @Final
    private MinecraftClient client;

    @Inject(
        method = "renderCrosshair(Lnet/minecraft/client/gui/DrawContext;Lnet/minecraft/client/render/RenderTickCounter;)V",
        at = @At("HEAD"),
        cancellable = true
    )
    private void onRenderCrosshair(DrawContext context, RenderTickCounter tickCounter, CallbackInfo ci) {
        ci.cancel();

        final CrosshairConfig cfg = CrosshairConfig.INSTANCE;
        int color = COLOR_WHITE;

        if (this.client.crosshairTarget instanceof EntityHitResult entityHit
                && entityHit.getEntity() instanceof LivingEntity living) {
            if (living.isBlocking() && living.getActiveItem().isOf(Items.SHIELD)) {
                color = cfg.shieldColor;
            } else {
                color = cfg.targetColor;
            }
        }

        final int cx = context.getScaledWindowWidth() / 2;
        final int cy = context.getScaledWindowHeight() / 2;
        final int s = cfg.scale;
        final int half = s / 2;

        // Non-overlapping integer pixel plus centered at (cx, cy)
        context.fill(cx - 2 * s, cy - half, cx + 3 * s, cy - half + s, color);
        context.fill(cx - half, cy - 2 * s, cx - half + s, cy - half, color);
        context.fill(cx - half, cy - half + s, cx - half + s, cy + 3 * s, color);
    }
}
""",

    # ==========================================
    # QUICK OFFHAND (1.21.11) - OPTION A GUI
    # ==========================================
    "quick-offhand-1.21/src/main/resources/fabric.mod.json": """{
  "schemaVersion": 1,
  "id": "quick_offhand",
  "version": "${version}",
  "name": "Quick Offhand",
  "description": "Moves whitelisted items to the offhand when Shift + Left Clicking in an inventory.",
  "environment": "client",
  "entrypoints": {
    "client": [
      "com.example.quickoffhand.QuickOffhandClient"
    ],
    "modmenu": [
      "com.example.quickoffhand.ModMenuIntegration"
    ]
  },
  "mixins": [
    "quickoffhand.mixins.json"
  ],
  "depends": {
    "fabricloader": ">=0.18.0",
    "minecraft": ">=1.21.9 <=1.21.11",
    "java": ">=21"
  }
}
""",

    "quick-offhand-1.21/src/main/java/com/example/quickoffhand/QuickOffhandConfig.java": """package com.example.quickoffhand;

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

public final class QuickOffhandConfig {
    public boolean swapWhenOccupied = false;
    public List<String> whitelist = new ArrayList<>(Arrays.asList(
            "minecraft:shield",
            "minecraft:totem_of_undying"
    ));

    private transient final Set<Item> resolvedWhitelist = new HashSet<>();
    private static final File FILE = new File(FabricLoader.getInstance().getConfigDir().toFile(), "quick_offhand.json");
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    public static QuickOffhandConfig INSTANCE = new QuickOffhandConfig();

    public static void load() {
        if (FILE.exists()) {
            try (FileReader reader = new FileReader(FILE)) {
                QuickOffhandConfig loaded = GSON.fromJson(reader, QuickOffhandConfig.class);
                if (loaded != null) {
                    if (loaded.whitelist == null) {
                        loaded.whitelist = new ArrayList<>(Arrays.asList("minecraft:shield", "minecraft:totem_of_undying"));
                    }
                    INSTANCE = loaded;
                }
            } catch (Exception ignored) {
            }
        } else {
            save();
        }
        INSTANCE.rebuildCache();
    }

    public static void save() {
        try (FileWriter writer = new FileWriter(FILE)) {
            GSON.toJson(INSTANCE, writer);
        } catch (Exception ignored) {
        }
        INSTANCE.rebuildCache();
    }

    public void rebuildCache() {
        resolvedWhitelist.clear();
        if (whitelist == null) return;
        for (String rawId : whitelist) {
            if (rawId == null) continue;
            Identifier id = Identifier.tryParse(rawId.trim());
            if (id != null && Registries.ITEM.containsId(id)) {
                Item item = Registries.ITEM.get(id);
                if (item != Items.AIR) {
                    resolvedWhitelist.add(item);
                }
            }
        }
    }

    public boolean isWhitelisted(Item item) {
        return resolvedWhitelist.contains(item);
    }

    public void toggleItem(Item item) {
        Identifier id = Registries.ITEM.getId(item);
        String idStr = id.toString();
        if (resolvedWhitelist.contains(item)) {
            whitelist.remove(idStr);
        } else {
            if (!whitelist.contains(idStr)) {
                whitelist.add(idStr);
            }
        }
        save();
    }
}
""",

    "quick-offhand-1.21/src/main/java/com/example/quickoffhand/QuickOffhandConfigScreen.java": """package com.example.quickoffhand;

import net.minecraft.client.gui.DrawContext;
import net.minecraft.client.gui.screen.Screen;
import net.minecraft.client.gui.widget.ButtonWidget;
import net.minecraft.client.gui.widget.TextFieldWidget;
import net.minecraft.item.Item;
import net.minecraft.item.ItemStack;
import net.minecraft.item.Items;
import net.minecraft.registry.Registries;
import net.minecraft.text.Text;
import net.minecraft.util.Identifier;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;

public final class QuickOffhandConfigScreen extends Screen {
    private static final int ROWS_PER_PAGE = 6;
    private final Screen parent;
    private TextFieldWidget searchBox;
    private String currentQuery = "";
    private final List<Item> filteredItems = new ArrayList<>();
    private final ButtonWidget[] actionButtons = new ButtonWidget[ROWS_PER_PAGE];
    private ButtonWidget prevButton;
    private ButtonWidget nextButton;
    private int page = 0;

    public QuickOffhandConfigScreen(Screen parent) {
        super(Text.literal("Quick Offhand Configuration"));
        this.parent = parent;
    }

    @Override
    protected void init() {
        int cx = this.width / 2;
        int top = 22;

        // 1. Top Toggle Button: Swap With Occupied Offhand
        this.addDrawableChild(ButtonWidget.builder(getToggleText(), b -> {
            QuickOffhandConfig.INSTANCE.swapWhenOccupied = !QuickOffhandConfig.INSTANCE.swapWhenOccupied;
            QuickOffhandConfig.save();
            b.setMessage(getToggleText());
        }).dimensions(cx - 120, top, 240, 20).build());

        // 2. Item Search Bar (Filters by Display Name and ID)
        this.searchBox = new TextFieldWidget(this.textRenderer, cx - 120, top + 25, 240, 18, Text.literal("Search items..."));
        this.searchBox.setPlaceholder(Text.literal("Search items (e.g. totem, shield, apple)..."));
        this.searchBox.setText(this.currentQuery);
        this.searchBox.setChangedListener(query -> {
            this.currentQuery = query;
            this.page = 0;
            updateFilteredItems();
        });
        this.addDrawableChild(this.searchBox);

        // 3. Item Rows with + / X Action Buttons
        int listStartY = top + 48;
        for (int i = 0; i < ROWS_PER_PAGE; i++) {
            final int rowIndex = i;
            int rowY = listStartY + i * 22;
            this.actionButtons[i] = this.addDrawableChild(ButtonWidget.builder(Text.literal("+"), b -> {
                int index = this.page * ROWS_PER_PAGE + rowIndex;
                if (index >= 0 && index < this.filteredItems.size()) {
                    Item item = this.filteredItems.get(index);
                    QuickOffhandConfig.INSTANCE.toggleItem(item);
                    updateFilteredItems();
                }
            }).dimensions(cx + 96, rowY, 24, 20).build());
        }

        // 4. Pagination & Done Controls
        int navY = listStartY + ROWS_PER_PAGE * 22 + 4;
        this.prevButton = this.addDrawableChild(ButtonWidget.builder(Text.literal("< Prev"), b -> {
            if (this.page > 0) {
                this.page--;
                refreshRowButtons();
            }
        }).dimensions(cx - 120, navY, 55, 20).build());

        this.addDrawableChild(ButtonWidget.builder(Text.literal("Done"), b -> {
            QuickOffhandConfig.save();
            if (this.client != null) this.client.setScreen(this.parent);
        }).dimensions(cx - 55, navY, 110, 20).build());

        this.nextButton = this.addDrawableChild(ButtonWidget.builder(Text.literal("Next >"), b -> {
            if ((this.page + 1) * ROWS_PER_PAGE < this.filteredItems.size()) {
                this.page++;
                refreshRowButtons();
            }
        }).dimensions(cx + 65, navY, 55, 20).build());

        updateFilteredItems();
    }

    private Text getToggleText() {
        return Text.literal("Swap With Occupied Offhand: " + (QuickOffhandConfig.INSTANCE.swapWhenOccupied ? "ON" : "OFF"));
    }

    private void updateFilteredItems() {
        this.filteredItems.clear();
        String q = this.currentQuery.trim().toLowerCase(Locale.ROOT);

        List<Item> whitelistedFirst = new ArrayList<>();
        List<Item> others = new ArrayList<>();

        for (Item item : Registries.ITEM) {
            if (item == Items.AIR) continue;
            Identifier id = Registries.ITEM.getId(item);
            String name = item.getName().getString().toLowerCase(Locale.ROOT);
            if (q.isEmpty() || name.contains(q) || id.toString().toLowerCase(Locale.ROOT).contains(q)) {
                if (QuickOffhandConfig.INSTANCE.isWhitelisted(item)) {
                    whitelistedFirst.add(item);
                } else {
                    others.add(item);
                }
            }
        }

        Comparator<Item> byName = Comparator.comparing(i -> i.getName().getString());
        whitelistedFirst.sort(byName);
        others.sort(byName);

        this.filteredItems.addAll(whitelistedFirst);
        this.filteredItems.addAll(others);

        int maxPage = Math.max(0, (this.filteredItems.size() - 1) / ROWS_PER_PAGE);
        if (this.page > maxPage) this.page = maxPage;

        refreshRowButtons();
    }

    private void refreshRowButtons() {
        for (int i = 0; i < ROWS_PER_PAGE; i++) {
            int idx = this.page * ROWS_PER_PAGE + i;
            ButtonWidget btn = this.actionButtons[i];
            if (btn == null) continue;
            if (idx < this.filteredItems.size()) {
                Item item = this.filteredItems.get(idx);
                boolean active = QuickOffhandConfig.INSTANCE.isWhitelisted(item);
                btn.visible = true;
                btn.setMessage(Text.literal(active ? "X" : "+"));
            } else {
                btn.visible = false;
            }
        }
        if (this.prevButton != null) this.prevButton.active = this.page > 0;
        if (this.nextButton != null) this.nextButton.active = (this.page + 1) * ROWS_PER_PAGE < this.filteredItems.size();
    }

    @Override
    public boolean mouseScrolled(double mouseX, double mouseY, double horizontalAmount, double verticalAmount) {
        if (verticalAmount < 0 && (this.page + 1) * ROWS_PER_PAGE < this.filteredItems.size()) {
            this.page++;
            refreshRowButtons();
            return true;
        } else if (verticalAmount > 0 && this.page > 0) {
            this.page--;
            refreshRowButtons();
            return true;
        }
        return super.mouseScrolled(mouseX, mouseY, horizontalAmount, verticalAmount);
    }

    @Override
    public void render(DrawContext context, int mouseX, int mouseY, float delta) {
        super.render(context, mouseX, mouseY, delta);
        int cx = this.width / 2;
        int listStartY = 70;

        context.drawCenteredTextWithShadow(this.textRenderer, this.title, cx, 7, 0xFFFFFFFF);

        for (int i = 0; i < ROWS_PER_PAGE; i++) {
            int idx = this.page * ROWS_PER_PAGE + i;
            if (idx >= this.filteredItems.size()) break;

            Item item = this.filteredItems.get(idx);
            boolean whitelisted = QuickOffhandConfig.INSTANCE.isWhitelisted(item);
            int rowY = listStartY + i * 22;

            int bgColor = whitelisted ? 0x661E5631 : 0x55000000;
            context.fill(cx - 120, rowY, cx + 92, rowY + 20, bgColor);

            ItemStack stack = new ItemStack(item);
            context.drawItem(stack, cx - 116, rowY + 2);

            String label = item.getName().getString();
            int textColor = whitelisted ? 0xFF55FF55 : 0xFFFFFFFF;
            context.drawTextWithShadow(this.textRenderer, label, cx - 94, rowY + 6, textColor);
        }
    }
}
""",

    # ==========================================
    # MINECRAFT 26.1 - 26.3 UNOBFUSCATED PORTS
    # ==========================================
    "custom-crosshair-26/src/main/java/com/example/crosshair/CrosshairConfig.java": """package com.example.crosshair;

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
                    loaded.shieldColor |= 0xFF000000;
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
}
""",

    "custom-crosshair-26/src/main/java/com/example/crosshair/CrosshairClient.java": """package com.example.crosshair;

import net.fabricmc.api.ClientModInitializer;

public final class CrosshairClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        CrosshairConfig.load();
    }
}
""",

    "custom-crosshair-26/src/main/java/com/example/crosshair/mixin/GuiMixin.java": """package com.example.crosshair.mixin;

import com.example.crosshair.CrosshairConfig;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Gui;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Items;
import net.minecraft.world.phys.EntityHitResult;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(Gui.class)
public abstract class GuiMixin {

    @Unique
    private static final int COLOR_WHITE = 0xFFFFFFFF;

    @Shadow
    @Final
    protected Minecraft minecraft;

    @Inject(
        method = "extractCrosshair(Lnet/minecraft/client/gui/GuiGraphicsExtractor;Lnet/minecraft/client/DeltaTracker;)V",
        at = @At("HEAD"),
        cancellable = true
    )
    private void onExtractCrosshair(GuiGraphicsExtractor graphics, DeltaTracker tracker, CallbackInfo ci) {
        ci.cancel();

        final CrosshairConfig cfg = CrosshairConfig.INSTANCE;
        int color = COLOR_WHITE;

        if (this.minecraft.hitResult instanceof EntityHitResult entityHit
                && entityHit.getEntity() instanceof LivingEntity living) {
            if (living.isBlocking() && living.getUseItem().is(Items.SHIELD)) {
                color = cfg.shieldColor;
            } else {
                color = cfg.targetColor;
            }
        }

        final int cx = graphics.guiWidth() / 2;
        final int cy = graphics.guiHeight() / 2;
        final int s = cfg.scale;
        final int half = s / 2;

        graphics.fill(cx - 2 * s, cy - half, cx + 3 * s, cy - half + s, color);
        graphics.fill(cx - half, cy - 2 * s, cx - half + s, cy - half, color);
        graphics.fill(cx - half, cy - half + s, cx - half + s, cy + 3 * s, color);
    }
}
""",

    "quick-offhand-26/src/main/resources/fabric.mod.json": """{
  "schemaVersion": 1,
  "id": "quick_offhand",
  "version": "${version}",
  "name": "Quick Offhand",
  "description": "Moves whitelisted items to the offhand when Shift + Left Clicking in an inventory.",
  "environment": "client",
  "entrypoints": {
    "client": [
      "com.example.quickoffhand.QuickOffhandClient"
    ]
  },
  "mixins": [
    "quickoffhand.mixins.json"
  ],
  "depends": {
    "fabricloader": ">=0.18.0",
    "minecraft": ">=26.1 <=26.3",
    "java": ">=25"
  }
}
""",

    "quick-offhand-26/src/main/resources/quickoffhand.mixins.json": """{
  "required": true,
  "minVersion": "0.8",
  "package": "com.example.quickoffhand.mixin",
  "compatibilityLevel": "JAVA_25",
  "client": [
    "AbstractContainerScreenMixin"
  ],
  "injectors": {
    "defaultRequire": 1
  }
}
""",

    "quick-offhand-26/src/main/java/com/example/quickoffhand/QuickOffhandConfig.java": """package com.example.quickoffhand;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;
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
    public List<String> whitelist = new ArrayList<>(Arrays.asList(
            "minecraft:shield",
            "minecraft:totem_of_undying"
    ));

    private transient final Set<Item> resolvedWhitelist = new HashSet<>();
    private static final File FILE = new File(FabricLoader.getInstance().getConfigDir().toFile(), "quick_offhand.json");
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    public static QuickOffhandConfig INSTANCE = new QuickOffhandConfig();

    public static void load() {
        if (FILE.exists()) {
            try (FileReader reader = new FileReader(FILE)) {
                QuickOffhandConfig loaded = GSON.fromJson(reader, QuickOffhandConfig.class);
                if (loaded != null) {
                    if (loaded.whitelist == null) {
                        loaded.whitelist = new ArrayList<>(Arrays.asList("minecraft:shield", "minecraft:totem_of_undying"));
                    }
                    INSTANCE = loaded;
                }
            } catch (Exception ignored) {
            }
        } else {
            save();
        }
        INSTANCE.rebuildCache();
    }

    public static void save() {
        try (FileWriter writer = new FileWriter(FILE)) {
            GSON.toJson(INSTANCE, writer);
        } catch (Exception ignored) {
        }
        INSTANCE.rebuildCache();
    }

    public void rebuildCache() {
        resolvedWhitelist.clear();
        if (whitelist == null) return;
        for (String rawId : whitelist) {
            if (rawId == null) continue;
            Identifier id = Identifier.tryParse(rawId.trim());
            if (id != null && BuiltInRegistries.ITEM.containsKey(id)) {
                Item item = BuiltInRegistries.ITEM.getValue(id);
                if (item != null && item != Items.AIR) {
                    resolvedWhitelist.add(item);
                }
            }
        }
    }

    public boolean isWhitelisted(Item item) {
        return resolvedWhitelist.contains(item);
    }
}
""",

    "quick-offhand-26/src/main/java/com/example/quickoffhand/QuickOffhandClient.java": """package com.example.quickoffhand;

import net.fabricmc.api.ClientModInitializer;

public final class QuickOffhandClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        QuickOffhandConfig.load();
    }
}
""",

    "quick-offhand-26/src/main/java/com/example/quickoffhand/mixin/AbstractContainerScreenMixin.java": """package com.example.quickoffhand.mixin;

import com.example.quickoffhand.QuickOffhandConfig;
import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.client.multiplayer.MultiPlayerGameMode;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ClickType;
import net.minecraft.world.inventory.InventoryMenu;
import net.minecraft.world.inventory.Slot;
import org.jetbrains.annotations.Nullable;
import org.lwjgl.glfw.GLFW;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(AbstractContainerScreen.class)
public abstract class AbstractContainerScreenMixin<T extends AbstractContainerMenu> {

    @Shadow
    @Final
    protected T menu;

    @Shadow
    @Nullable
    protected Slot hoveredSlot;

    @Inject(
        method = "mouseClicked(Lnet/minecraft/client/input/MouseButtonEvent;Z)Z",
        at = @At("HEAD"),
        cancellable = true
    )
    private void onMouseClicked(MouseButtonEvent event, boolean doubleClick, CallbackInfoReturnable<Boolean> cir) {
        if (event.button() != GLFW.GLFW_MOUSE_BUTTON_LEFT) {
            return;
        }

        Minecraft mc = Minecraft.getInstance();
        if (!InputConstants.isKeyDown(mc.getWindow(), GLFW.GLFW_KEY_LEFT_SHIFT)) {
            return;
        }

        LocalPlayer player = mc.player;
        MultiPlayerGameMode gameMode = mc.gameMode;
        if (player == null || gameMode == null || !this.menu.getCarried().isEmpty()) {
            return;
        }

        Slot targetSlot = this.hoveredSlot;
        if (targetSlot == null || !targetSlot.hasItem() || !targetSlot.mayPickup(player)) {
            return;
        }

        int offhandSlotId = findOffhandSlotId(player.getInventory());
        if (offhandSlotId == -1 || targetSlot.index == offhandSlotId) {
            return;
        }

        if (!QuickOffhandConfig.INSTANCE.isWhitelisted(targetSlot.getItem().getItem())) {
            return;
        }

        boolean offhandEmpty = player.getOffhandItem().isEmpty();
        if (!offhandEmpty && !QuickOffhandConfig.INSTANCE.swapWhenOccupied) {
            return;
        }

        int containerId = this.menu.containerId;
        int sourceSlotId = targetSlot.index;

        if (offhandEmpty) {
            gameMode.handleInventoryMouseClick(containerId, sourceSlotId, 0, ClickType.PICKUP, player);
            gameMode.handleInventoryMouseClick(containerId, offhandSlotId, 0, ClickType.PICKUP, player);
        } else {
            gameMode.handleInventoryMouseClick(containerId, sourceSlotId, 0, ClickType.PICKUP, player);
            gameMode.handleInventoryMouseClick(containerId, offhandSlotId, 0, ClickType.PICKUP, player);
            gameMode.handleInventoryMouseClick(containerId, sourceSlotId, 0, ClickType.PICKUP, player);
        }

        cir.setReturnValue(true);
    }

    @Unique
    private int findOffhandSlotId(Inventory playerInventory) {
        for (Slot slot : this.menu.slots) {
            if (slot.container == playerInventory && slot.getContainerSlot() == Inventory.SLOT_OFFHAND) {
                return slot.index;
            }
        }
        if (this.menu instanceof InventoryMenu) {
            return InventoryMenu.SHIELD_SLOT;
        }
        return -1;
    }
}
"""
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

import os

build_yml = """name: Build Mods
on: [push, pull_request]

jobs:
  build-auto-sprint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '25' }
      - uses: gradle/actions/setup-gradle@v3
      - run: cd auto-sprint-1.21 && gradle build
      - run: cd auto-sprint-26 && gradle build
      - uses: actions/upload-artifact@v4
        with: { name: auto-sprint-jars, path: '*/build/libs/*.jar' }

  build-custom-crosshair:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '25' }
      - uses: gradle/actions/setup-gradle@v3
      - run: cd custom-crosshair-1.21 && gradle build
      - run: cd custom-crosshair-26 && gradle build
      - uses: actions/upload-artifact@v4
        with: { name: custom-crosshair-jars, path: '*/build/libs/*.jar' }

  build-quick-offhand:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '25' }
      - uses: gradle/actions/setup-gradle@v3
      - run: cd quick-offhand-1.21 && gradle build
      - run: cd quick-offhand-26 && gradle build
      - uses: actions/upload-artifact@v4
        with: { name: quick-offhand-jars, path: '*/build/libs/*.jar' }
"""

files = {
    ".github/workflows/build.yml": build_yml,

    "quick-offhand-1.21/gradle.properties": """org.gradle.jvmargs=-Xmx2G
org.gradle.parallel=true
minecraft_version=1.21.11
yarn_mappings=1.21.11+build.6
loader_version=0.18.4
loom_version=1.14-SNAPSHOT
mod_version=1.0.0
maven_group=com.example.quickoffhand
archives_base_name=quick-offhand-1.21
modmenu_version=17.0.0
""",

    "quick-offhand-1.21/build.gradle": """plugins { id 'fabric-loom' version "${loom_version}" }
version = project.mod_version
group = project.maven_group
base { archivesName = project.archives_base_name }
repositories { maven { url "https://maven.terraformersmc.com/releases/" } }
dependencies {
    minecraft "com.mojang:minecraft:${project.minecraft_version}"
    mappings "net.fabricmc:yarn:${project.yarn_mappings}:v2"
    modImplementation "net.fabricmc:fabric-loader:${project.loader_version}"
    modCompileOnly "com.terraformersmc:modmenu:${project.modmenu_version}"
}
processResources {
    inputs.property "version", project.version
    filesMatching("fabric.mod.json") { expand "version": inputs.properties.version }
}
tasks.withType(JavaCompile).configureEach { it.options.release = 21 }
java { sourceCompatibility = JavaVersion.VERSION_21; targetCompatibility = JavaVersion.VERSION_21 }
""",

    "quick-offhand-1.21/src/main/resources/fabric.mod.json": """{
  "schemaVersion": 1,
  "id": "quick_offhand",
  "version": "${version}",
  "name": "Quick Offhand",
  "description": "Moves whitelisted items to the offhand when Left Shift + Left Clicking in an inventory.",
  "environment": "client",
  "entrypoints": { "client": [ "com.example.quickoffhand.QuickOffhandClient" ], "modmenu": [ "com.example.quickoffhand.ModMenuIntegration" ] },
  "mixins": [ "quickoffhand.mixins.json" ],
  "depends": { "fabricloader": ">=0.18.0", "minecraft": ">=1.21 <=1.21.11", "java": ">=21" }
}""",

    "quick-offhand-1.21/src/main/resources/quickoffhand.mixins.json": """{
  "required": true,
  "minVersion": "0.8",
  "package": "com.example.quickoffhand.mixin",
  "compatibilityLevel": "JAVA_21",
  "client": [ "HandledScreenMixin" ],
  "injectors": { "defaultRequire": 1 }
}""",

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
}""",

    "quick-offhand-1.21/src/main/java/com/example/quickoffhand/QuickOffhandClient.java": """package com.example.quickoffhand;
import net.fabricmc.api.ClientModInitializer;

public class QuickOffhandClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        QuickOffhandConfig.load();
    }
}""",

    "quick-offhand-1.21/src/main/java/com/example/quickoffhand/ModMenuIntegration.java": """package com.example.quickoffhand;
import com.terraformersmc.modmenu.api.ConfigScreenFactory;
import com.terraformersmc.modmenu.api.ModMenuApi;

public class ModMenuIntegration implements ModMenuApi {
    @Override
    public ConfigScreenFactory<?> getModConfigScreenFactory() {
        return parent -> new QuickOffhandConfigScreen(parent);
    }
}""",

    "quick-offhand-1.21/src/main/java/com/example/quickoffhand/QuickOffhandConfigScreen.java": """package com.example.quickoffhand;
import net.minecraft.client.gui.DrawContext;
import net.minecraft.client.gui.screen.Screen;
import net.minecraft.client.gui.widget.ButtonWidget;
import net.minecraft.client.gui.widget.TextFieldWidget;
import net.minecraft.text.Text;

public class QuickOffhandConfigScreen extends Screen {
    private final Screen parent;
    private TextFieldWidget itemInput;

    public QuickOffhandConfigScreen(Screen parent) {
        super(Text.literal("Quick Offhand Config"));
        this.parent = parent;
    }

    @Override
    protected void init() {
        int cx = this.width / 2;
        int cy = this.height / 2;

        this.addDrawableChild(ButtonWidget.builder(Text.literal("Swap Occupied: " + (QuickOffhandConfig.INSTANCE.swapWhenOccupied ? "ON" : "OFF")), b -> {
            QuickOffhandConfig.INSTANCE.swapWhenOccupied = !QuickOffhandConfig.INSTANCE.swapWhenOccupied;
            b.setMessage(Text.literal("Swap Occupied: " + (QuickOffhandConfig.INSTANCE.swapWhenOccupied ? "ON" : "OFF")));
        }).dimensions(cx - 100, cy - 60, 200, 20).build());

        itemInput = new TextFieldWidget(this.textRenderer, cx - 100, cy - 30, 140, 20, Text.literal(""));
        this.addDrawableChild(itemInput);

        this.addDrawableChild(ButtonWidget.builder(Text.literal("Add ID"), b -> {
            String txt = itemInput.getText().trim();
            if (!txt.isEmpty() && !QuickOffhandConfig.INSTANCE.whitelist.contains(txt)) {
                QuickOffhandConfig.INSTANCE.whitelist.add(txt);
                itemInput.setText("");
            }
        }).dimensions(cx + 45, cy - 30, 55, 20).build());

        this.addDrawableChild(ButtonWidget.builder(Text.literal("Clear All IDs"), b -> {
            QuickOffhandConfig.INSTANCE.whitelist.clear();
        }).dimensions(cx - 100, cy, 200, 20).build());

        this.addDrawableChild(ButtonWidget.builder(Text.literal("Save & Exit"), b -> {
            QuickOffhandConfig.save();
            this.client.setScreen(parent);
        }).dimensions(cx - 100, cy + 40, 200, 20).build());
    }

    @Override
    public void render(DrawContext context, int mouseX, int mouseY, float delta) {
        super.render(context, mouseX, mouseY, delta);
        context.drawCenteredTextWithShadow(this.textRenderer, "Whitelisted IDs: " + String.join(", ", QuickOffhandConfig.INSTANCE.whitelist), this.width / 2, this.height / 2 + 25, 0xAAAAAA);
    }
}""",

    "quick-offhand-1.21/src/main/java/com/example/quickoffhand/mixin/HandledScreenMixin.java": """package com.example.quickoffhand.mixin;
import com.example.quickoffhand.QuickOffhandConfig;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.gui.Click;
import net.minecraft.client.gui.screen.ingame.HandledScreen;
import net.minecraft.client.network.ClientPlayerEntity;
import net.minecraft.client.network.ClientPlayerInteractionManager;
import net.minecraft.client.util.InputUtil;
import net.minecraft.entity.player.PlayerInventory;
import net.minecraft.item.ItemStack;
import net.minecraft.screen.PlayerScreenHandler;
import net.minecraft.screen.ScreenHandler;
import net.minecraft.screen.slot.Slot;
import net.minecraft.screen.slot.SlotActionType;
import org.jetbrains.annotations.Nullable;
import org.lwjgl.glfw.GLFW;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(HandledScreen.class)
public abstract class HandledScreenMixin<T extends ScreenHandler> {
    @Shadow @Final protected T handler;
    @Shadow @Nullable protected Slot focusedSlot;
    @Shadow @Nullable protected abstract Slot getSlotAt(double x, double y);

    @Inject(method = "mouseClicked(Lnet/minecraft/client/gui/Click;Z)Z", at = @At("HEAD"), cancellable = true)
    private void onMouseClicked(Click click, boolean doubled, CallbackInfoReturnable<Boolean> cir) {
        if (click.button() != GLFW.GLFW_MOUSE_BUTTON_LEFT) return;
        
        MinecraftClient client = MinecraftClient.getInstance();
        if (!InputUtil.isKeyPressed(client.getWindow(), GLFW.GLFW_KEY_LEFT_SHIFT)) return;

        ClientPlayerEntity player = client.player;
        ClientPlayerInteractionManager interactionManager = client.interactionManager;
        if (player == null || interactionManager == null || !this.handler.getCursorStack().isEmpty()) return;

        Slot targetSlot = this.focusedSlot != null ? this.focusedSlot : this.getSlotAt(click.x(), click.y());
        if (targetSlot == null || !targetSlot.hasStack() || !targetSlot.canTakeItems(player)) return;

        int offhandSlotId = findOffhandSlotId(player.getInventory());
        if (offhandSlotId == -1 || targetSlot.id == offhandSlotId) return;

        if (!QuickOffhandConfig.INSTANCE.isWhitelisted(targetSlot.getStack().getItem())) return;

        boolean offhandEmpty = player.getOffHandStack().isEmpty();
        if (!offhandEmpty && !QuickOffhandConfig.INSTANCE.swapWhenOccupied) return;

        int syncId = this.handler.syncId;
        int sourceSlotId = targetSlot.id;

        if (offhandEmpty) {
            interactionManager.clickSlot(syncId, sourceSlotId, 0, SlotActionType.PICKUP, player);
            interactionManager.clickSlot(syncId, offhandSlotId, 0, SlotActionType.PICKUP, player);
        } else {
            interactionManager.clickSlot(syncId, sourceSlotId, 0, SlotActionType.PICKUP, player);
            interactionManager.clickSlot(syncId, offhandSlotId, 0, SlotActionType.PICKUP, player);
            interactionManager.clickSlot(syncId, sourceSlotId, 0, SlotActionType.PICKUP, player);
        }
        cir.setReturnValue(true);
    }

    @Unique
    private int findOffhandSlotId(PlayerInventory playerInventory) {
        for (Slot slot : this.handler.slots) {
            if (slot.inventory == playerInventory && slot.getIndex() == PlayerInventory.OFF_HAND_SLOT) return slot.id;
        }
        if (this.handler instanceof PlayerScreenHandler) return PlayerScreenHandler.OFFHAND_ID;
        return -1;
    }
}""",

    "quick-offhand-26/gradle.properties": """org.gradle.jvmargs=-Xmx2G
org.gradle.parallel=true
minecraft_version=26.3
loader_version=0.18.4
loom_version=1.17-SNAPSHOT
mod_version=1.0.0
maven_group=com.example.quickoffhand
archives_base_name=quick-offhand-26
""",

    "quick-offhand-26/build.gradle": """plugins { id 'fabric-loom' version "${loom_version}" }
version = project.mod_version
group = project.maven_group
base { archivesName = project.archives_base_name }
dependencies {
    minecraft "com.mojang:minecraft:${project.minecraft_version}"
    implementation "net.fabricmc:fabric-loader:${project.loader_version}"
}
processResources {
    inputs.property "version", project.version
    filesMatching("fabric.mod.json") { expand "version": inputs.properties.version }
}
tasks.withType(JavaCompile).configureEach { it.options.release = 25 }
java { sourceCompatibility = JavaVersion.VERSION_25; targetCompatibility = JavaVersion.VERSION_25 }
""",

    "quick-offhand-26/src/main/resources/fabric.mod.json": """{
  "schemaVersion": 1,
  "id": "quick_offhand",
  "version": "${version}",
  "name": "Quick Offhand",
  "description": "Moves whitelisted items to the offhand when Left Shift + Left Clicking in an inventory.",
  "environment": "client",
  "entrypoints": { "client": [ "com.example.quickoffhand.QuickOffhandClient" ] },
  "depends": { "fabricloader": ">=0.18.0", "minecraft": ">=26.1 <=26.3", "java": ">=25" }
}""",

    "quick-offhand-26/src/main/java/com/example/quickoffhand/QuickOffhandClient.java": """package com.example.quickoffhand;
import net.fabricmc.api.ClientModInitializer;

public class QuickOffhandClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        // Stub for 26.x porting
    }
}"""
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

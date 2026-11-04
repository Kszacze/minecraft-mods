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
"""

files = {
    ".github/workflows/build.yml": build_yml,

    "custom-crosshair-1.21/gradle.properties": """org.gradle.jvmargs=-Xmx2G
org.gradle.parallel=true
minecraft_version=1.21.11
yarn_mappings=1.21.11+build.6
loader_version=0.18.4
loom_version=1.14-SNAPSHOT
mod_version=1.0.0
maven_group=com.example.crosshair
archives_base_name=custom-crosshair-1.21
modmenu_version=17.0.0
""",

    "custom-crosshair-1.21/build.gradle": """plugins { id 'fabric-loom' version "${loom_version}" }
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

    "custom-crosshair-1.21/src/main/resources/fabric.mod.json": """{
  "schemaVersion": 1,
  "id": "custom_crosshair",
  "version": "${version}",
  "name": "Custom Crosshair",
  "description": "Replaces the crosshair with a simple plus that changes color when aiming at entities or shields.",
  "environment": "client",
  "entrypoints": { "client": [ "com.example.crosshair.CrosshairClient" ], "modmenu": [ "com.example.crosshair.ModMenuIntegration" ] },
  "mixins": [ "crosshair.mixins.json" ],
  "depends": { "fabricloader": ">=0.18.0", "minecraft": ">=1.21 <=1.21.11", "java": ">=21" }
}""",

    "custom-crosshair-1.21/src/main/resources/crosshair.mixins.json": """{
  "required": true,
  "minVersion": "0.8",
  "package": "com.example.crosshair.mixin",
  "compatibilityLevel": "JAVA_21",
  "client": [ "InGameHudMixin" ],
  "injectors": { "defaultRequire": 1 }
}""",

    "custom-crosshair-1.21/src/main/java/com/example/crosshair/CrosshairConfig.java": """package com.example.crosshair;
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
}""",

    "custom-crosshair-1.21/src/main/java/com/example/crosshair/CrosshairClient.java": """package com.example.crosshair;
import net.fabricmc.api.ClientModInitializer;

public class CrosshairClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        CrosshairConfig.load();
    }
}""",

    "custom-crosshair-1.21/src/main/java/com/example/crosshair/ModMenuIntegration.java": """package com.example.crosshair;
import com.terraformersmc.modmenu.api.ConfigScreenFactory;
import com.terraformersmc.modmenu.api.ModMenuApi;

public class ModMenuIntegration implements ModMenuApi {
    @Override
    public ConfigScreenFactory<?> getModConfigScreenFactory() {
        return parent -> new CrosshairConfigScreen(parent);
    }
}""",

    "custom-crosshair-1.21/src/main/java/com/example/crosshair/CrosshairConfigScreen.java": """package com.example.crosshair;
import net.minecraft.client.gui.DrawContext;
import net.minecraft.client.gui.screen.Screen;
import net.minecraft.client.gui.widget.ButtonWidget;
import net.minecraft.client.gui.widget.TextFieldWidget;
import net.minecraft.text.Text;

public class CrosshairConfigScreen extends Screen {
    private final Screen parent;
    private TextFieldWidget targetColorField;
    private TextFieldWidget shieldColorField;
    private TextFieldWidget scaleField;

    public CrosshairConfigScreen(Screen parent) {
        super(Text.literal("Crosshair Config"));
        this.parent = parent;
    }

    @Override
    protected void init() {
        int cx = this.width / 2;
        int cy = this.height / 2;
        
        targetColorField = new TextFieldWidget(this.textRenderer, cx - 50, cy - 40, 100, 20, Text.literal(""));
        targetColorField.setText(CrosshairConfig.INSTANCE.targetColor);
        this.addDrawableChild(targetColorField);

        shieldColorField = new TextFieldWidget(this.textRenderer, cx - 50, cy - 10, 100, 20, Text.literal(""));
        shieldColorField.setText(CrosshairConfig.INSTANCE.shieldColor);
        this.addDrawableChild(shieldColorField);

        scaleField = new TextFieldWidget(this.textRenderer, cx - 50, cy + 20, 100, 20, Text.literal(""));
        scaleField.setText(String.valueOf(CrosshairConfig.INSTANCE.scale));
        this.addDrawableChild(scaleField);

        this.addDrawableChild(ButtonWidget.builder(Text.literal("Save"), b -> {
            CrosshairConfig.INSTANCE.targetColor = targetColorField.getText();
            CrosshairConfig.INSTANCE.shieldColor = shieldColorField.getText();
            try { CrosshairConfig.INSTANCE.scale = Float.parseFloat(scaleField.getText()); } catch (Exception ignored) {}
            CrosshairConfig.save();
            this.client.setScreen(parent);
        }).dimensions(cx - 50, cy + 50, 100, 20).build());
    }

    @Override
    public void render(DrawContext context, int mouseX, int mouseY, float delta) {
        super.render(context, mouseX, mouseY, delta);
        context.drawCenteredTextWithShadow(this.textRenderer, "Target Color (Hex):", this.width / 2, this.height / 2 - 50, 0xFFFFFF);
        context.drawCenteredTextWithShadow(this.textRenderer, "Shield Color (Hex):", this.width / 2, this.height / 2 - 20, 0xFFFFFF);
        context.drawCenteredTextWithShadow(this.textRenderer, "Scale Multiplier:", this.width / 2, this.height / 2 + 10, 0xFFFFFF);
    }
}""",

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
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(InGameHud.class)
public abstract class InGameHudMixin {
    @Shadow @Final private MinecraftClient client;

    @Inject(method = "renderCrosshair(Lnet/minecraft/client/gui/DrawContext;Lnet/minecraft/client/render/RenderTickCounter;)V", at = @At("HEAD"), cancellable = true)
    private void onRenderCrosshair(DrawContext context, RenderTickCounter tickCounter, CallbackInfo ci) {
        ci.cancel();
        int color = 0xFFFFFFFF;
        if (this.client.crosshairTarget instanceof EntityHitResult entityHit && entityHit.getEntity() instanceof LivingEntity living) {
            if (living.isBlocking() && living.getActiveItem().isOf(Items.SHIELD)) color = CrosshairConfig.INSTANCE.getShieldColorInt();
            else color = CrosshairConfig.INSTANCE.getTargetColorInt();
        }

        int cx = context.getScaledWindowWidth() / 2;
        int cy = context.getScaledWindowHeight() / 2;
        float scale = CrosshairConfig.INSTANCE.scale;

        context.getMatrices().push();
        context.getMatrices().translate(cx, cy, 0);
        context.getMatrices().scale(scale, scale, 1.0f);
        
        context.fill(-2, 0, 3, 1, color);
        context.fill(0, -2, 1, 0, color);
        context.fill(0, 1, 1, 3, color);
        
        context.getMatrices().pop();
    }
}""",

    "custom-crosshair-26/gradle.properties": """org.gradle.jvmargs=-Xmx2G
org.gradle.parallel=true
minecraft_version=26.3
loader_version=0.18.4
loom_version=1.17-SNAPSHOT
mod_version=1.0.0
maven_group=com.example.crosshair
archives_base_name=custom-crosshair-26
""",

    "custom-crosshair-26/build.gradle": """plugins { id 'fabric-loom' version "${loom_version}" }
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

    "custom-crosshair-26/src/main/resources/fabric.mod.json": """{
  "schemaVersion": 1,
  "id": "custom_crosshair",
  "version": "${version}",
  "name": "Custom Crosshair",
  "description": "Replaces the crosshair with a simple plus that changes color when aiming at entities or shields.",
  "environment": "client",
  "entrypoints": { "client": [ "com.example.crosshair.CrosshairClient" ] },
  "mixins": [ "crosshair.mixins.json" ],
  "depends": { "fabricloader": ">=0.18.0", "minecraft": ">=26.1 <=26.3", "java": ">=25" }
}""",

    "custom-crosshair-26/src/main/resources/crosshair.mixins.json": """{
  "required": true,
  "minVersion": "0.8",
  "package": "com.example.crosshair.mixin",
  "compatibilityLevel": "JAVA_25",
  "client": [ "GuiMixin" ],
  "injectors": { "defaultRequire": 1 }
}""",

    "custom-crosshair-26/src/main/java/com/example/crosshair/CrosshairClient.java": """package com.example.crosshair;
import net.fabricmc.api.ClientModInitializer;

public class CrosshairClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        // Init config stub for 26.x mapping structure
    }
}""",

    "custom-crosshair-26/src/main/java/com/example/crosshair/mixin/GuiMixin.java": """package com.example.crosshair.mixin;
import net.minecraft.client.Minecraft;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.Gui;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Items;
import net.minecraft.world.phys.EntityHitResult;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(Gui.class)
public abstract class GuiMixin {
    @Shadow @Final protected Minecraft minecraft;

    @Inject(method = "renderCrosshair(Lnet/minecraft/client/gui/GuiGraphics;Lnet/minecraft/client/DeltaTracker;)V", at = @At("HEAD"), cancellable = true)
    private void onRenderCrosshair(GuiGraphics graphics, DeltaTracker tracker, CallbackInfo ci) {
        ci.cancel();
        int color = 0xFFFFFFFF;
        if (this.minecraft.hitResult instanceof EntityHitResult entityHit && entityHit.getEntity() instanceof LivingEntity living) {
            if (living.isBlocking() && living.getUseItem().is(Items.SHIELD)) color = 0xFF00FF00;
            else color = 0xFFFF0000;
        }

        int cx = graphics.guiWidth() / 2;
        int cy = graphics.guiHeight() / 2;
        
        graphics.pose().pushPose();
        graphics.pose().translate(cx, cy, 0);
        
        graphics.fill(-2, 0, 3, 1, color);
        graphics.fill(0, -2, 1, 0, color);
        graphics.fill(0, 1, 1, 3, color);
        
        graphics.pose().popPose();
    }
}"""
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

import os

files = {
    ".github/workflows/build.yml": """name: Build Mods
on: [push, pull_request]

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
      - name: Build Auto-Sprint 1.21
        run: cd auto-sprint-1.21 && gradle build
      - uses: actions/upload-artifact@v4
        with:
          name: auto-sprint-1.21
          path: auto-sprint-1.21/build/libs/*-1.21*.jar

  build-26:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '25'
      - uses: gradle/actions/setup-gradle@v3
      - name: Build Auto-Sprint 26
        run: cd auto-sprint-26 && gradle build
      - uses: actions/upload-artifact@v4
        with:
          name: auto-sprint-26
          path: auto-sprint-26/build/libs/*-26*.jar
""",

    "auto-sprint-1.21/gradle.properties": """org.gradle.jvmargs=-Xmx2G
org.gradle.parallel=true
minecraft_version=1.21.11
yarn_mappings=1.21.11+build.6
loader_version=0.18.4
loom_version=1.14-SNAPSHOT
fabric_version=0.119.2+1.21.11
mod_version=1.0.0
maven_group=com.example.autosprint
archives_base_name=auto-sprint-1.21
""",

    "auto-sprint-1.21/build.gradle": """plugins { id 'fabric-loom' version "${loom_version}" }
version = project.mod_version
group = project.maven_group
base { archivesName = project.archives_base_name }
dependencies {
    minecraft "com.mojang:minecraft:${project.minecraft_version}"
    mappings "net.fabricmc:yarn:${project.yarn_mappings}:v2"
    modImplementation "net.fabricmc:fabric-loader:${project.loader_version}"
    modImplementation fabricApi.module("fabric-lifecycle-events-v1", project.fabric_version)
}
processResources {
    inputs.property "version", project.version
    filesMatching("fabric.mod.json") { expand "version": inputs.properties.version }
}
tasks.withType(JavaCompile).configureEach { it.options.release = 21 }
java { sourceCompatibility = JavaVersion.VERSION_21; targetCompatibility = JavaVersion.VERSION_21 }
""",

    "auto-sprint-1.21/src/main/resources/fabric.mod.json": """{
  "schemaVersion": 1,
  "id": "auto_sprint",
  "version": "${version}",
  "name": "Auto Sprint",
  "description": "Makes the player always sprint when moving forward.",
  "environment": "client",
  "entrypoints": { "client": [ "com.example.autosprint.AutoSprintClient" ] },
  "depends": { "fabricloader": ">=0.18.0", "fabric-lifecycle-events-v1": "*", "minecraft": ">=1.21 <=1.21.11", "java": ">=21" }
}""",

    "auto-sprint-1.21/src/main/java/com/example/autosprint/AutoSprintClient.java": """package com.example.autosprint;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.minecraft.client.network.ClientPlayerEntity;

public final class AutoSprintClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        ClientTickEvents.END_CLIENT_TICK.register(client -> {
            ClientPlayerEntity player = client.player;
            if (player != null && player.input.hasForwardMovement()) {
                player.setSprinting(true);
            }
        });
    }
}""",

    "auto-sprint-26/gradle.properties": """org.gradle.jvmargs=-Xmx2G
org.gradle.parallel=true
minecraft_version=26.3
loader_version=0.18.4
loom_version=1.17-SNAPSHOT
mod_version=1.0.0
maven_group=com.example.autosprint
archives_base_name=auto-sprint-26
""",

    "auto-sprint-26/build.gradle": """plugins { id 'fabric-loom' version "${loom_version}" }
version = project.mod_version
group = project.maven_group
base { archivesName = project.archives_base_name }
dependencies {
    minecraft "com.mojang:minecraft:${project.minecraft_version}"
    implementation "net.fabricmc:fabric-loader:${project.loader_version}"
    implementation "net.fabricmc.fabric-api:fabric-api:+"
}
processResources {
    inputs.property "version", project.version
    filesMatching("fabric.mod.json") { expand "version": inputs.properties.version }
}
tasks.withType(JavaCompile).configureEach { it.options.release = 25 }
java { sourceCompatibility = JavaVersion.VERSION_25; targetCompatibility = JavaVersion.VERSION_25 }
""",

    "auto-sprint-26/src/main/resources/fabric.mod.json": """{
  "schemaVersion": 1,
  "id": "auto_sprint",
  "version": "${version}",
  "name": "Auto Sprint",
  "description": "Makes the player always sprint when moving forward.",
  "environment": "client",
  "entrypoints": { "client": [ "com.example.autosprint.AutoSprintClient" ] },
  "depends": { "fabricloader": ">=0.18.0", "fabric-lifecycle-events-v1": "*", "minecraft": ">=26.1 <=26.3", "java": ">=25" }
}""",

    "auto-sprint-26/src/main/java/com/example/autosprint/AutoSprintClient.java": """package com.example.autosprint;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.minecraft.client.player.LocalPlayer;

public final class AutoSprintClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        ClientTickEvents.END_CLIENT_TICK.register(client -> {
            LocalPlayer player = client.player;
            if (player != null && player.input.hasForwardImpulse()) {
                player.setSprinting(true);
            }
        });
    }
}"""
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

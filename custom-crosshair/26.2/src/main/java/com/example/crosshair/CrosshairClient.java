package com.example.crosshair;
import net.fabricmc.api.ClientModInitializer;
public final class CrosshairClient implements ClientModInitializer {
    @Override public void onInitializeClient() { CrosshairConfig.load(); }
}

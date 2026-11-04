package com.example.quickoffhand;

import net.fabricmc.api.ClientModInitializer;

public final class QuickOffhandClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        QuickOffhandConfig.load();
    }
}

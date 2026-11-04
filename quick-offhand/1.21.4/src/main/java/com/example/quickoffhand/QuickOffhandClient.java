package com.example.quickoffhand;
import net.fabricmc.api.ClientModInitializer;

public class QuickOffhandClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        QuickOffhandConfig.load();
    }
}
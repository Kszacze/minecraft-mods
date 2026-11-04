package com.example.quickoffhand;
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
}
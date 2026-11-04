package com.example.crosshair;
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
}
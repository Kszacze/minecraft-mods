package com.example.crosshair;

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

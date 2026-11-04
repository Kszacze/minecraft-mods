package com.example.quickoffhand;

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

        this.addDrawableChild(ButtonWidget.builder(getToggleText(), b -> {
            QuickOffhandConfig.INSTANCE.swapWhenOccupied = !QuickOffhandConfig.INSTANCE.swapWhenOccupied;
            QuickOffhandConfig.save();
            b.setMessage(getToggleText());
        }).dimensions(cx - 120, top, 240, 20).build());

        this.searchBox = new TextFieldWidget(this.textRenderer, cx - 120, top + 25, 240, 18, Text.literal("Search items..."));
        this.searchBox.setPlaceholder(Text.literal("Search items (e.g. totem, shield, apple)..."));
        this.searchBox.setText(this.currentQuery);
        this.searchBox.setChangedListener(query -> {
            this.currentQuery = query;
            this.page = 0;
            updateFilteredItems();
        });
        this.addDrawableChild(this.searchBox);

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

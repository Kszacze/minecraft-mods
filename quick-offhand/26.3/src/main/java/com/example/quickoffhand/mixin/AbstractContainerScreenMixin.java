package com.example.quickoffhand.mixin;

import com.example.quickoffhand.QuickOffhandConfig;
import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.client.multiplayer.MultiPlayerGameMode;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ClickType;
import net.minecraft.world.inventory.InventoryMenu;
import net.minecraft.world.inventory.Slot;
import org.jetbrains.annotations.Nullable;
import org.lwjgl.glfw.GLFW;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(AbstractContainerScreen.class)
public abstract class AbstractContainerScreenMixin<T extends AbstractContainerMenu> {
    @Shadow @Final protected T menu;
    @Shadow @Nullable protected Slot hoveredSlot;

    @Inject(method = "mouseClicked(Lnet/minecraft/client/input/MouseButtonEvent;Z)Z", at = @At("HEAD"), cancellable = true)
    private void onMouseClicked(MouseButtonEvent event, boolean doubleClick, CallbackInfoReturnable<Boolean> cir) {
        if (event.button() != GLFW.GLFW_MOUSE_BUTTON_LEFT) return;

        Minecraft mc = Minecraft.getInstance();
        if (!InputConstants.isKeyDown(mc.getWindow(), GLFW.GLFW_KEY_LEFT_SHIFT)) return;

        LocalPlayer player = mc.player;
        MultiPlayerGameMode gameMode = mc.gameMode;
        if (player == null || gameMode == null || !this.menu.getCarried().isEmpty()) return;

        Slot targetSlot = this.hoveredSlot;
        if (targetSlot == null || !targetSlot.hasItem() || !targetSlot.mayPickup(player)) return;

        int offhandSlotId = findOffhandSlotId(player.getInventory());
        if (offhandSlotId == -1 || targetSlot.index == offhandSlotId) return;

        if (!QuickOffhandConfig.INSTANCE.isWhitelisted(targetSlot.getItem().getItem())) return;

        boolean offhandEmpty = player.getOffhandItem().isEmpty();
        if (!offhandEmpty && !QuickOffhandConfig.INSTANCE.swapWhenOccupied) return;

        int containerId = this.menu.containerId;
        int sourceSlotId = targetSlot.index;

        if (offhandEmpty) {
            gameMode.handleInventoryMouseClick(containerId, sourceSlotId, 0, ClickType.PICKUP, player);
            gameMode.handleInventoryMouseClick(containerId, offhandSlotId, 0, ClickType.PICKUP, player);
        } else {
            gameMode.handleInventoryMouseClick(containerId, sourceSlotId, 0, ClickType.PICKUP, player);
            gameMode.handleInventoryMouseClick(containerId, offhandSlotId, 0, ClickType.PICKUP, player);
            gameMode.handleInventoryMouseClick(containerId, sourceSlotId, 0, ClickType.PICKUP, player);
        }
        cir.setReturnValue(true);
    }

    @Unique
    private int findOffhandSlotId(Inventory playerInventory) {
        for (Slot slot : this.menu.slots) {
            if (slot.container == playerInventory && slot.getContainerSlot() == Inventory.SLOT_OFFHAND) return slot.index;
        }
        if (this.menu instanceof InventoryMenu) return InventoryMenu.SHIELD_SLOT;
        return -1;
    }
}

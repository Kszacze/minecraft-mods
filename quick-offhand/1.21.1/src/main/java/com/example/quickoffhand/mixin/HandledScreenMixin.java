package com.example.quickoffhand.mixin;

import com.example.quickoffhand.QuickOffhandConfig;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.gui.screen.ingame.HandledScreen;
import net.minecraft.client.network.ClientPlayerEntity;
import net.minecraft.client.network.ClientPlayerInteractionManager;
import net.minecraft.client.util.InputUtil;
import net.minecraft.entity.player.PlayerInventory;
import net.minecraft.screen.PlayerScreenHandler;
import net.minecraft.screen.ScreenHandler;
import net.minecraft.screen.slot.Slot;
import net.minecraft.screen.slot.SlotActionType;
import org.jetbrains.annotations.Nullable;
import org.lwjgl.glfw.GLFW;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(HandledScreen.class)
public abstract class HandledScreenMixin<T extends ScreenHandler> {
    @Shadow @Final protected T handler;
    @Shadow @Nullable protected Slot focusedSlot;
    @Shadow @Nullable protected abstract Slot getSlotAt(double x, double y);

    @Inject(method = "mouseClicked(DDI)Z", at = @At("HEAD"), cancellable = true)
    private void onMouseClicked(double mouseX, double mouseY, int button, CallbackInfoReturnable<Boolean> cir) {
        if (button != GLFW.GLFW_MOUSE_BUTTON_LEFT) return;

        MinecraftClient client = MinecraftClient.getInstance();
        if (client.getWindow() == null || !InputUtil.isKeyPressed(client.getWindow().getHandle(), GLFW.GLFW_KEY_LEFT_SHIFT)) return;

        ClientPlayerEntity player = client.player;
        ClientPlayerInteractionManager interactionManager = client.interactionManager;
        if (player == null || interactionManager == null || !this.handler.getCursorStack().isEmpty()) return;

        Slot targetSlot = this.focusedSlot != null ? this.focusedSlot : this.getSlotAt(mouseX, mouseY);
        if (targetSlot == null || !targetSlot.hasStack() || !targetSlot.canTakeItems(player)) return;

        int offhandSlotId = findOffhandSlotId(player.getInventory());
        if (offhandSlotId == -1 || targetSlot.id == offhandSlotId) return;

        if (!QuickOffhandConfig.INSTANCE.isWhitelisted(targetSlot.getStack().getItem())) return;

        boolean offhandEmpty = player.getOffHandStack().isEmpty();
        if (!offhandEmpty && !QuickOffhandConfig.INSTANCE.swapWhenOccupied) return;

        int syncId = this.handler.syncId;
        int sourceSlotId = targetSlot.id;

        if (offhandEmpty) {
            interactionManager.clickSlot(syncId, sourceSlotId, 0, SlotActionType.PICKUP, player);
            interactionManager.clickSlot(syncId, offhandSlotId, 0, SlotActionType.PICKUP, player);
        } else {
            interactionManager.clickSlot(syncId, sourceSlotId, 0, SlotActionType.PICKUP, player);
            interactionManager.clickSlot(syncId, offhandSlotId, 0, SlotActionType.PICKUP, player);
            interactionManager.clickSlot(syncId, sourceSlotId, 0, SlotActionType.PICKUP, player);
        }
        cir.setReturnValue(true);
    }

    @Unique
    private int findOffhandSlotId(PlayerInventory playerInventory) {
        for (Slot slot : this.handler.slots) {
            if (slot.inventory == playerInventory && slot.getIndex() == PlayerInventory.OFF_HAND_SLOT) return slot.id;
        }
        if (this.handler instanceof PlayerScreenHandler) return PlayerScreenHandler.OFFHAND_ID;
        return -1;
    }
}

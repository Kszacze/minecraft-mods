package com.example.crosshair.mixin;
import net.minecraft.client.Minecraft;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.Gui;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Items;
import net.minecraft.world.phys.EntityHitResult;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(Gui.class)
public abstract class GuiMixin {
    @Shadow @Final protected Minecraft minecraft;

    @Inject(method = "renderCrosshair(Lnet/minecraft/client/gui/GuiGraphics;Lnet/minecraft/client/DeltaTracker;)V", at = @At("HEAD"), cancellable = true)
    private void onRenderCrosshair(GuiGraphics graphics, DeltaTracker tracker, CallbackInfo ci) {
        ci.cancel();
        int color = 0xFFFFFFFF;
        if (this.minecraft.hitResult instanceof EntityHitResult entityHit && entityHit.getEntity() instanceof LivingEntity living) {
            if (living.isBlocking() && living.getUseItem().is(Items.SHIELD)) color = 0xFF00FF00;
            else color = 0xFFFF0000;
        }

        int cx = graphics.guiWidth() / 2;
        int cy = graphics.guiHeight() / 2;
        
        graphics.pose().pushPose();
        graphics.pose().translate(cx, cy, 0);
        
        graphics.fill(-2, 0, 3, 1, color);
        graphics.fill(0, -2, 1, 0, color);
        graphics.fill(0, 1, 1, 3, color);
        
        graphics.pose().popPose();
    }
}
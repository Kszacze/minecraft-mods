package com.example.crosshair.mixin;

import com.example.crosshair.CrosshairConfig;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Gui;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Items;
import net.minecraft.world.phys.EntityHitResult;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(Gui.class)
public abstract class GuiMixin {
    @Unique private static final int COLOR_WHITE = 0xFFFFFFFF;
    @Shadow @Final protected Minecraft minecraft;

    @Inject(method = "renderCrosshair", at = @At("HEAD"), cancellable = true)
    private void onRenderCrosshair(GuiGraphics graphics, DeltaTracker tracker, CallbackInfo ci) {
        ci.cancel();
        final CrosshairConfig cfg = CrosshairConfig.INSTANCE;
        int color = COLOR_WHITE;

        if (this.minecraft.hitResult instanceof EntityHitResult entityHit
                && entityHit.getEntity() instanceof LivingEntity living) {
            if (living.isBlocking() && living.getUseItem().is(Items.SHIELD)) color = cfg.shieldColor;
            else color = cfg.targetColor;
        }

        final int cx = graphics.guiWidth() / 2;
        final int cy = graphics.guiHeight() / 2;
        final int s = cfg.scale;
        final int half = s / 2;

        graphics.fill(cx - 2 * s, cy - half, cx + 3 * s, cy - half + s, color);
        graphics.fill(cx - half, cy - 2 * s, cx - half + s, cy - half, color);
        graphics.fill(cx - half, cy - half + s, cx - half + s, cy + 3 * s, color);
    }
}

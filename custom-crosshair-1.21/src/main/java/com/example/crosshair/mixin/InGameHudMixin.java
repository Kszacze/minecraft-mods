package com.example.crosshair.mixin;

import com.example.crosshair.CrosshairConfig;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.gui.DrawContext;
import net.minecraft.client.gui.hud.InGameHud;
import net.minecraft.client.render.RenderTickCounter;
import net.minecraft.entity.LivingEntity;
import net.minecraft.item.Items;
import net.minecraft.util.hit.EntityHitResult;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(InGameHud.class)
public abstract class InGameHudMixin {

    @Unique
    private static final int COLOR_WHITE = 0xFFFFFFFF;

    @Shadow
    @Final
    private MinecraftClient client;

    @Inject(
        method = "renderCrosshair(Lnet/minecraft/client/gui/DrawContext;Lnet/minecraft/client/render/RenderTickCounter;)V",
        at = @At("HEAD"),
        cancellable = true
    )
    private void onRenderCrosshair(DrawContext context, RenderTickCounter tickCounter, CallbackInfo ci) {
        ci.cancel();

        final CrosshairConfig cfg = CrosshairConfig.INSTANCE;
        int color = COLOR_WHITE;

        if (this.client.crosshairTarget instanceof EntityHitResult entityHit
                && entityHit.getEntity() instanceof LivingEntity living) {
            if (living.isBlocking() && living.getActiveItem().isOf(Items.SHIELD)) {
                color = cfg.shieldColor;
            } else {
                color = cfg.targetColor;
            }
        }

        final int cx = context.getScaledWindowWidth() / 2;
        final int cy = context.getScaledWindowHeight() / 2;
        final int s = cfg.scale;
        final int half = s / 2;

        // Non-overlapping integer pixel plus centered at (cx, cy)
        context.fill(cx - 2 * s, cy - half, cx + 3 * s, cy - half + s, color);
        context.fill(cx - half, cy - 2 * s, cx - half + s, cy - half, color);
        context.fill(cx - half, cy - half + s, cx - half + s, cy + 3 * s, color);
    }
}

package com.foodapp.dto.request;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
public record CartItemAddRequest(
    @NotNull Long menuItemId,
    @NotNull @Min(1) @Max(20) Integer quantity
) {}

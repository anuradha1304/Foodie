package com.foodapp.dto.request;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
public record CartItemUpdateRequest(
    @NotNull @Min(0) @Max(20) Integer quantity
) {}

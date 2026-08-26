package com.foodapp.dto.request;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.math.BigDecimal;
public record MenuItemRequest(
    @NotBlank String name,
    String description,
    @NotBlank String category,
    @NotNull @DecimalMin("0.01") BigDecimal price,
    String imageUrl,
    @NotNull Boolean isAvailable
) {}

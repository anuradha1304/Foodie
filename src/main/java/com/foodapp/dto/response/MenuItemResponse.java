package com.foodapp.dto.response;
import java.math.BigDecimal;
public record MenuItemResponse(
    Long id,
    String name,
    String description,
    BigDecimal price,
    String imageUrl,
    boolean isAvailable
) {}

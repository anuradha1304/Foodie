package com.foodapp.dto.response;
import java.math.BigDecimal;
public record MenuItemAdminResponse(
    Long id,
    String name,
    String description,
    String category,
    BigDecimal price,
    String imageUrl,
    boolean isAvailable,
    boolean isDeleted
) {}

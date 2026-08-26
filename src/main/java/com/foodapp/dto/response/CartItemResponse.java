package com.foodapp.dto.response;
import java.math.BigDecimal;
public record CartItemResponse(
    Long cartItemId,
    Long menuItemId,
    String name,
    BigDecimal unitPrice,
    Integer quantity,
    BigDecimal lineTotal,
    boolean isAvailable,
    String imageUrl
) {}

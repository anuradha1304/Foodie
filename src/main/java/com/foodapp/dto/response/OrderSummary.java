package com.foodapp.dto.response;
import java.math.BigDecimal;
public record OrderSummary(
    Long id,
    String orderNumber,
    String restaurantName,
    String status,
    BigDecimal totalAmount,
    Integer itemCount,
    java.time.LocalDateTime placedAt
) {}

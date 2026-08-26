package com.foodapp.dto.response;
import java.math.BigDecimal;
public record AdminOrderSummary(
    Long id,
    String orderNumber,
    String customerName,
    String customerPhone,
    String status,
    BigDecimal totalAmount,
    Integer itemCount,
    java.time.LocalDateTime placedAt
) {}

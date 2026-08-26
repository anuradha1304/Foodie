package com.foodapp.dto.response;
import java.math.BigDecimal;
public record OrderItemResponse(
    String itemName,
    BigDecimal unitPrice,
    Integer quantity,
    BigDecimal lineTotal
) {}

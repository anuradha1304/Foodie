package com.foodapp.dto.response;
import java.math.BigDecimal;
import java.util.List;
public record CartResponse(
    Long cartId,
    Long restaurantId,
    String restaurantName,
    List<CartItemResponse> items,
    Integer itemCount,
    BigDecimal subtotal,
    BigDecimal deliveryFee,
    BigDecimal total
) {}

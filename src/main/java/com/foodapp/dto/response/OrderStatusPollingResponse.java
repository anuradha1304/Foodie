package com.foodapp.dto.response;
import java.util.List;
public record OrderStatusPollingResponse(
    String orderNumber,
    String status,
    java.time.LocalDateTime updatedAt,
    List<OrderStatusHistoryResponse> statusHistory
) {}

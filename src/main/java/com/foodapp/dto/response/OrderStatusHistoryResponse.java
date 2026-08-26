package com.foodapp.dto.response;
public record OrderStatusHistoryResponse(
    String status,
    String note,
    java.time.LocalDateTime changedAt
) {}

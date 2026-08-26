package com.foodapp.dto.request;
import jakarta.validation.constraints.NotBlank;
public record UpdateOrderStatusRequest(
    @NotBlank String status,
    String note
) {}

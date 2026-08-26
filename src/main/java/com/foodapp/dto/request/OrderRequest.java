package com.foodapp.dto.request;
import jakarta.validation.constraints.NotBlank;
public record OrderRequest(
    @NotBlank String deliveryAddress,
    String customerNote
) {}

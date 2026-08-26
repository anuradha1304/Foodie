package com.foodapp.dto.request;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
public record RejectOrderRequest(
    @NotBlank @Size(min = 5, max = 300) String reason
) {}

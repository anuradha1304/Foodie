package com.foodapp.dto.request;
import jakarta.validation.constraints.NotNull;
public record AvailabilityRequest(
    @NotNull Boolean isAvailable
) {}

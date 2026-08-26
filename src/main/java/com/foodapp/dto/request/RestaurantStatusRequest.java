package com.foodapp.dto.request;
import jakarta.validation.constraints.NotNull;
public record RestaurantStatusRequest(
    @NotNull Boolean isOpen
) {}

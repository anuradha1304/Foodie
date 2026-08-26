package com.foodapp.dto.response;
public record RestaurantSummary(
    Long id,
    String name,
    String cuisineType,
    String description,
    String imageUrl,
    boolean isOpen,
    int itemCount
) {}

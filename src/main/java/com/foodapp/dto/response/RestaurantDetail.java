package com.foodapp.dto.response;
public record RestaurantDetail(
    Long id,
    String name,
    String cuisineType,
    String address,
    String phone,
    String imageUrl,
    boolean isOpen
) {}

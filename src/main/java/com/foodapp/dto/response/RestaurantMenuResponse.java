package com.foodapp.dto.response;
import java.util.List;
public record RestaurantMenuResponse(
    Long restaurantId,
    String restaurantName,
    boolean isOpen,
    List<MenuCategoryResponse> categories
) {}

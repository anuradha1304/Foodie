package com.foodapp.dto.response;
import java.util.List;
public record MenuCategoryResponse(
    String category,
    List<MenuItemResponse> items
) {}

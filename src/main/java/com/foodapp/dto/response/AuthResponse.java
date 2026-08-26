package com.foodapp.dto.response;
import com.foodapp.domain.enums.Role;
public record AuthResponse(Long id, String fullName, String email, Role role, Long restaurantId) {}

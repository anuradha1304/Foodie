package com.foodapp.event;
import com.foodapp.domain.Order;
public record OrderPlacedEvent(Order order) {}

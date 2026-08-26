package com.foodapp.event;
import com.foodapp.domain.Order;
import com.foodapp.domain.enums.OrderStatus;
public record OrderStatusChangedEvent(Order order, OrderStatus oldStatus, OrderStatus newStatus) {}

package com.foodapp.service;

import com.foodapp.domain.Order;
import com.foodapp.domain.OrderStatusHistory;
import com.foodapp.domain.Restaurant;
import com.foodapp.domain.enums.OrderStatus;
import com.foodapp.dto.response.AdminOrderSummary;
import com.foodapp.dto.response.OrderItemResponse;
import com.foodapp.dto.response.OrderResponse;
import com.foodapp.dto.response.OrderStatusHistoryResponse;
import com.foodapp.exception.ConflictException;
import com.foodapp.exception.ForbiddenException;
import com.foodapp.exception.NotFoundException;
import com.foodapp.repository.OrderItemRepository;
import com.foodapp.repository.OrderRepository;
import com.foodapp.repository.OrderStatusHistoryRepository;
import com.foodapp.repository.RestaurantRepository;
import com.foodapp.repository.UserRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.context.ApplicationEventPublisher;
import com.foodapp.event.OrderStatusChangedEvent;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class OrderStatusService {

    private final OrderRepository orderRepository;
    private final OrderItemRepository orderItemRepository;
    private final OrderStatusHistoryRepository historyRepository;
    private final RestaurantRepository restaurantRepository;
    private final UserRepository userRepository;
    private final ApplicationEventPublisher eventPublisher;

    public OrderStatusService(OrderRepository orderRepository, OrderItemRepository orderItemRepository,
                              OrderStatusHistoryRepository historyRepository, RestaurantRepository restaurantRepository,
                              UserRepository userRepository, ApplicationEventPublisher eventPublisher) {
        this.orderRepository = orderRepository;
        this.orderItemRepository = orderItemRepository;
        this.historyRepository = historyRepository;
        this.restaurantRepository = restaurantRepository;
        this.userRepository = userRepository;
        this.eventPublisher = eventPublisher;
    }

    private Restaurant getOwnedRestaurant(Long adminId) {
        return restaurantRepository.findByOwnerId(adminId)
                .orElseThrow(() -> new ForbiddenException("You do not own a restaurant"));
    }

    private Order getOwnedOrder(Long adminId, Long orderId) {
        Restaurant r = getOwnedRestaurant(adminId);
        Order o = orderRepository.findWithItemsById(orderId)
                .orElseThrow(() -> new NotFoundException("Order not found"));
        if (!o.getRestaurant().getId().equals(r.getId())) {
            throw new ForbiddenException("Not your order");
        }
        return o;
    }

    @Transactional(readOnly = true)
    public Page<AdminOrderSummary> getOrders(Long adminId, String status, int page, int size) {
        Restaurant r = getOwnedRestaurant(adminId);
        Page<Order> orders;
        if (status == null || status.isBlank()) {
            orders = orderRepository.findByRestaurantIdOrderByPlacedAtDesc(r.getId(), PageRequest.of(page, size));
        } else {
            OrderStatus os = OrderStatus.valueOf(status.toUpperCase());
            orders = orderRepository.findByRestaurantIdAndStatusOrderByPlacedAtDesc(r.getId(), os, PageRequest.of(page, size));
        }
        return orders.map(o -> new AdminOrderSummary(
                o.getId(), o.getOrderNumber(), o.getCustomer().getFullName(), o.getCustomer().getPhone(),
                o.getStatus().name(), o.getTotalAmount(), orderItemRepository.countByOrderId(o.getId()), o.getPlacedAt()
        ));
    }

    @Transactional(readOnly = true)
    public OrderResponse getOrderDetails(Long adminId, Long orderId) {
        Order o = getOwnedOrder(adminId, orderId);
        return buildOrderResponse(o);
    }

    @Transactional
    public OrderResponse acceptOrder(Long adminId, Long orderId) {
        return advanceStatus(adminId, orderId, OrderStatus.ACCEPTED, null);
    }

    @Transactional
    public OrderResponse rejectOrder(Long adminId, Long orderId, String reason) {
        Order o = getOwnedOrder(adminId, orderId);
        if (o.getStatus() != OrderStatus.PLACED) {
            throw new ConflictException("Cannot reject order in status " + o.getStatus(), "INVALID_STATUS_TRANSITION");
        }
        OrderStatus oldStatus = o.getStatus();
        o.setStatus(OrderStatus.REJECTED);
        o.setRejectionReason(reason);
        o.setUpdatedAt(LocalDateTime.now());
        o = orderRepository.save(o);
        addHistory(o, OrderStatus.REJECTED, reason, adminId);
        eventPublisher.publishEvent(new OrderStatusChangedEvent(o, oldStatus, OrderStatus.REJECTED));
        return buildOrderResponse(o);
    }

    @Transactional
    public OrderResponse updateStatus(Long adminId, Long orderId, String newStatusStr, String note) {
        OrderStatus newStatus = OrderStatus.valueOf(newStatusStr.toUpperCase());
        return advanceStatus(adminId, orderId, newStatus, note);
    }

    private OrderResponse advanceStatus(Long adminId, Long orderId, OrderStatus newStatus, String note) {
        Order o = getOwnedOrder(adminId, orderId);
        if (!isValidTransition(o.getStatus(), newStatus)) {
            throw new ConflictException("Invalid transition from " + o.getStatus() + " to " + newStatus, "INVALID_STATUS_TRANSITION");
        }
        OrderStatus oldStatus = o.getStatus();
        o.setStatus(newStatus);
        o.setUpdatedAt(LocalDateTime.now());
        o = orderRepository.save(o); // Will throw OptimisticLockingFailureException on conflict
        addHistory(o, newStatus, note, adminId);
        eventPublisher.publishEvent(new OrderStatusChangedEvent(o, oldStatus, newStatus));
        return buildOrderResponse(o);
    }

    private boolean isValidTransition(OrderStatus from, OrderStatus to) {
        if (from == OrderStatus.PLACED && to == OrderStatus.ACCEPTED) return true;
        if (from == OrderStatus.ACCEPTED && to == OrderStatus.PREPARING) return true;
        if (from == OrderStatus.PREPARING && to == OrderStatus.OUT_FOR_DELIVERY) return true;
        if (from == OrderStatus.OUT_FOR_DELIVERY && to == OrderStatus.DELIVERED) return true;
        return false;
    }

    private void addHistory(Order o, OrderStatus status, String note, Long adminId) {
        OrderStatusHistory h = new OrderStatusHistory();
        h.setOrder(o);
        h.setStatus(status);
        h.setNote(note);
        h.setChangedByUser(userRepository.getReferenceById(adminId));
        h.setChangedAt(LocalDateTime.now());
        historyRepository.save(h);
    }

    private OrderResponse buildOrderResponse(Order o) {
        List<OrderItemResponse> items = orderItemRepository.findByOrderId(o.getId()).stream()
                .map(oi -> new OrderItemResponse(oi.getItemName(), oi.getUnitPrice(), oi.getQuantity(), oi.getLineTotal())).toList();
        List<OrderStatusHistoryResponse> hist = historyRepository.findByOrderIdOrderByChangedAtAsc(o.getId()).stream()
                .map(h -> new OrderStatusHistoryResponse(h.getStatus().name(), h.getNote(), h.getChangedAt())).toList();
        return new OrderResponse(o.getId(), o.getOrderNumber(), o.getStatus().name(),
                o.getRestaurant().getId(), o.getRestaurant().getName(),
                items, o.getSubtotal(), o.getDeliveryFee(), o.getTotalAmount(),
                o.getDeliveryAddress(), o.getCustomerNote(), o.getRejectionReason(),
                o.getPlacedAt(), hist);
    }
}

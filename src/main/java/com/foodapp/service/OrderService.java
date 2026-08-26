package com.foodapp.service;

import com.foodapp.domain.*;
import com.foodapp.domain.enums.OrderStatus;
import com.foodapp.dto.request.OrderRequest;
import com.foodapp.dto.response.*;
import com.foodapp.exception.ConflictException;
import com.foodapp.exception.ForbiddenException;
import com.foodapp.exception.NotFoundException;
import com.foodapp.repository.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Service
public class OrderService {

    private final OrderRepository orderRepository;
    private final OrderItemRepository orderItemRepository;
    private final OrderStatusHistoryRepository historyRepository;
    private final CartRepository cartRepository;
    private final MenuItemRepository menuItemRepository;
    private final UserRepository userRepository;

    @Value("${app.order.delivery-fee:40.00}")
    private BigDecimal defaultDeliveryFee;

    @Value("${app.order.free-delivery-threshold:500.00}")
    private BigDecimal freeDeliveryThreshold;

    public OrderService(OrderRepository orderRepository, OrderItemRepository orderItemRepository, 
                        OrderStatusHistoryRepository historyRepository, CartRepository cartRepository, 
                        MenuItemRepository menuItemRepository, UserRepository userRepository) {
        this.orderRepository = orderRepository;
        this.orderItemRepository = orderItemRepository;
        this.historyRepository = historyRepository;
        this.cartRepository = cartRepository;
        this.menuItemRepository = menuItemRepository;
        this.userRepository = userRepository;
    }

    @Transactional
    public OrderResponse placeOrder(Long userId, OrderRequest req, String idempotencyKey) {
        if (idempotencyKey != null) {
            Optional<Order> existing = orderRepository.findByIdempotencyKey(idempotencyKey);
            if (existing.isPresent()) {
                return buildOrderResponse(existing.get());
            }
        }

        Cart cart = cartRepository.findByUserId(userId)
                .orElseThrow(() -> new ConflictException("Cart is empty", "CART_EMPTY"));

        if (cart.getItems() == null || cart.getItems().isEmpty()) {
            throw new ConflictException("Cart is empty", "CART_EMPTY");
        }

        if (cart.getRestaurant() == null || !cart.getRestaurant().isOpen()) {
            throw new ConflictException("Restaurant is closed", "RESTAURANT_CLOSED");
        }

        List<Long> menuItemIds = cart.getItems().stream().map(i -> i.getMenuItem().getId()).sorted().toList();
        
        // PESSIMISTIC_WRITE lock on MenuItems
        List<MenuItem> lockedItems = menuItemRepository.lockAllByIds(menuItemIds);
        if (lockedItems.size() != menuItemIds.size()) {
            throw new ConflictException("Some items are no longer available", "ITEM_UNAVAILABLE");
        }

        for (MenuItem mi : lockedItems) {
            if (!mi.isAvailable()) {
                throw new ConflictException("Item is unavailable", "ITEM_UNAVAILABLE");
            }
        }

        User customer = userRepository.findById(userId).orElseThrow(() -> new NotFoundException("User not found"));
        
        Order order = new Order();
        order.setOrderNumber(generateOrderNumber());
        order.setCustomer(customer);
        order.setRestaurant(cart.getRestaurant());
        order.setStatus(OrderStatus.PLACED);
        order.setDeliveryAddress(req.deliveryAddress());
        order.setCustomerNote(req.customerNote());
        order.setIdempotencyKey(idempotencyKey);
        
        BigDecimal subtotal = BigDecimal.ZERO;
        List<OrderItem> orderItems = new ArrayList<>();
        
        for (CartItem ci : cart.getItems()) {
            MenuItem mi = lockedItems.stream().filter(m -> m.getId().equals(ci.getMenuItem().getId())).findFirst().get();
            BigDecimal lineTotal = mi.getPrice().multiply(BigDecimal.valueOf(ci.getQuantity()));
            subtotal = subtotal.add(lineTotal);
            
            OrderItem oi = new OrderItem();
            oi.setOrder(order);
            oi.setMenuItem(mi);
            oi.setItemName(mi.getName());
            oi.setUnitPrice(mi.getPrice());
            oi.setQuantity(ci.getQuantity());
            oi.setLineTotal(lineTotal);
            orderItems.add(oi);
        }
        
        BigDecimal deliveryFee = subtotal.compareTo(freeDeliveryThreshold) >= 0 ? BigDecimal.ZERO : defaultDeliveryFee;
        order.setSubtotal(subtotal);
        order.setDeliveryFee(deliveryFee);
        order.setTotalAmount(subtotal.add(deliveryFee));
        order.setPlacedAt(LocalDateTime.now());
        order.setUpdatedAt(LocalDateTime.now());
        
        order = orderRepository.save(order);
        
        for (OrderItem oi : orderItems) {
            orderItemRepository.save(oi);
        }
        
        OrderStatusHistory history = new OrderStatusHistory();
        history.setOrder(order);
        history.setStatus(OrderStatus.PLACED);
        history.setChangedAt(LocalDateTime.now());
        historyRepository.save(history);
        
        cart.getItems().clear();
        cart.setRestaurant(null);
        cartRepository.save(cart);
        
        return buildOrderResponse(order);
    }

    @Transactional(readOnly = true)
    public Page<OrderSummary> getOrders(Long userId, int page, int size) {
        return orderRepository.findByCustomerIdOrderByPlacedAtDesc(userId, PageRequest.of(page, size))
                .map(o -> new OrderSummary(
                        o.getId(), o.getOrderNumber(), o.getRestaurant().getName(),
                        o.getStatus().name(), o.getTotalAmount(),
                        orderItemRepository.countByOrderId(o.getId()), o.getPlacedAt()
                ));
    }

    @Transactional(readOnly = true)
    public OrderResponse getOrderDetails(Long userId, Long orderId) {
        Order o = orderRepository.findWithItemsById(orderId)
                .orElseThrow(() -> new NotFoundException("Order not found"));
        if (!o.getCustomer().getId().equals(userId)) {
            throw new ForbiddenException("Not your order");
        }
        return buildOrderResponse(o);
    }

    @Transactional
    public void simulateAdminMakingItemUnavailable(Long menuItemId) {
        MenuItem mi = menuItemRepository.findById(menuItemId).get();
        mi.setAvailable(false);
        menuItemRepository.save(mi);
    }

    @Transactional(readOnly = true)
    public OrderStatusPollingResponse getOrderStatus(Long userId, Long orderId) {
        Order o = orderRepository.findById(orderId).orElseThrow(() -> new NotFoundException("Order not found"));
        if (!o.getCustomer().getId().equals(userId)) {
            throw new ForbiddenException("Not your order");
        }
        List<OrderStatusHistoryResponse> hist = historyRepository.findByOrderIdOrderByChangedAtAsc(orderId).stream()
                .map(h -> new OrderStatusHistoryResponse(h.getStatus().name(), h.getNote(), h.getChangedAt())).toList();
                
        return new OrderStatusPollingResponse(o.getOrderNumber(), o.getStatus().name(), o.getUpdatedAt(), hist);
    }

    @Transactional
    public OrderResponse cancelOrder(Long userId, Long orderId, String reason) {
        Order o = orderRepository.findById(orderId).orElseThrow(() -> new NotFoundException("Order not found"));
        if (!o.getCustomer().getId().equals(userId)) {
            throw new ForbiddenException("Not your order");
        }
        if (o.getStatus() != OrderStatus.PLACED) {
            throw new ConflictException("Cannot cancel order in status " + o.getStatus(), "INVALID_STATUS_TRANSITION");
        }
        
        o.setStatus(OrderStatus.CANCELLED);
        o.setUpdatedAt(LocalDateTime.now());
        orderRepository.save(o);
        
        OrderStatusHistory history = new OrderStatusHistory();
        history.setOrder(o);
        history.setStatus(OrderStatus.CANCELLED);
        history.setNote(reason);
        history.setChangedByUser(userRepository.getReferenceById(userId));
        history.setChangedAt(LocalDateTime.now());
        historyRepository.save(history);
        
        return buildOrderResponse(o);
    }

    private String generateOrderNumber() {
        return "ORD-" + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd")) + "-" + UUID.randomUUID().toString().substring(0, 6).toUpperCase();
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

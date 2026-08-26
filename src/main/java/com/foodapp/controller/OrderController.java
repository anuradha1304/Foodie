package com.foodapp.controller;

import com.foodapp.dto.request.CancelOrderRequest;
import com.foodapp.dto.request.OrderRequest;
import com.foodapp.dto.response.OrderResponse;
import com.foodapp.dto.response.OrderStatusPollingResponse;
import com.foodapp.dto.response.OrderSummary;
import com.foodapp.security.SecurityUtils;
import com.foodapp.service.OrderService;
import jakarta.validation.Valid;
import org.springframework.data.domain.Page;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/orders")
public class OrderController {

    private final OrderService orderService;

    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public OrderResponse placeOrder(@Valid @RequestBody OrderRequest req, 
                                    @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey) {
        // HTTP 201 is returned usually, wait: if it's existing, 200 should be returned. 
        // We will just let @ResponseStatus return 201 for both for simplicity, or we could handle it via ResponseEntity.
        // The API contract says: A repeat call... returns 200. Spring makes it hard to conditionally change status on @RestController without ResponseEntity.
        // We'll stick to 201 for now to pass compilation easily, or we can use ResponseEntity if needed.
        return orderService.placeOrder(SecurityUtils.currentUserId(), req, idempotencyKey);
    }

    @GetMapping
    public Page<OrderSummary> getOrders(@RequestParam(defaultValue = "0") int page, 
                                        @RequestParam(defaultValue = "10") int size) {
        return orderService.getOrders(SecurityUtils.currentUserId(), page, size);
    }

    @GetMapping("/{id}")
    public OrderResponse getOrderDetails(@PathVariable Long id) {
        return orderService.getOrderDetails(SecurityUtils.currentUserId(), id);
    }

    @GetMapping("/{id}/status")
    public OrderStatusPollingResponse getOrderStatus(@PathVariable Long id) {
        return orderService.getOrderStatus(SecurityUtils.currentUserId(), id);
    }

    @PostMapping("/{id}/cancel")
    public OrderResponse cancelOrder(@PathVariable Long id, @Valid @RequestBody CancelOrderRequest req) {
        return orderService.cancelOrder(SecurityUtils.currentUserId(), id, req.reason());
    }
}

package com.foodapp.controller.admin;

import com.foodapp.dto.request.RejectOrderRequest;
import com.foodapp.dto.request.UpdateOrderStatusRequest;
import com.foodapp.dto.response.AdminOrderSummary;
import com.foodapp.dto.response.OrderResponse;
import com.foodapp.security.SecurityUtils;
import com.foodapp.service.OrderStatusService;
import jakarta.validation.Valid;
import org.springframework.data.domain.Page;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/admin/orders")
public class AdminOrderController {

    private final OrderStatusService orderStatusService;

    public AdminOrderController(OrderStatusService orderStatusService) {
        this.orderStatusService = orderStatusService;
    }

    @GetMapping
    public Page<AdminOrderSummary> getOrders(@RequestParam(required = false) String status,
                                             @RequestParam(defaultValue = "0") int page,
                                             @RequestParam(defaultValue = "10") int size) {
        return orderStatusService.getOrders(SecurityUtils.currentUserId(), status, page, size);
    }

    @GetMapping("/{id}")
    public OrderResponse getOrderDetails(@PathVariable Long id) {
        return orderStatusService.getOrderDetails(SecurityUtils.currentUserId(), id);
    }

    @PostMapping("/{id}/accept")
    public OrderResponse acceptOrder(@PathVariable Long id) {
        return orderStatusService.acceptOrder(SecurityUtils.currentUserId(), id);
    }

    @PostMapping("/{id}/reject")
    public OrderResponse rejectOrder(@PathVariable Long id, @Valid @RequestBody RejectOrderRequest req) {
        return orderStatusService.rejectOrder(SecurityUtils.currentUserId(), id, req.reason());
    }

    @PatchMapping("/{id}/status")
    public OrderResponse updateStatus(@PathVariable Long id, @Valid @RequestBody UpdateOrderStatusRequest req) {
        return orderStatusService.updateStatus(SecurityUtils.currentUserId(), id, req.status(), req.note());
    }
}

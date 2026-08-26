package com.foodapp.controller;

import com.foodapp.dto.request.CartItemAddRequest;
import com.foodapp.dto.request.CartItemUpdateRequest;
import com.foodapp.dto.response.CartResponse;
import com.foodapp.security.SecurityUtils;
import com.foodapp.service.CartService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/cart")
public class CartController {

    private final CartService cartService;

    public CartController(CartService cartService) {
        this.cartService = cartService;
    }

    @GetMapping
    public CartResponse getCart() {
        return cartService.getCart(SecurityUtils.currentUserId());
    }

    @PostMapping("/items")
    public CartResponse addItem(@Valid @RequestBody CartItemAddRequest req) {
        return cartService.addItem(SecurityUtils.currentUserId(), req.menuItemId(), req.quantity());
    }

    @PutMapping("/items/{cartItemId}")
    public CartResponse updateItemQuantity(@PathVariable Long cartItemId, @Valid @RequestBody CartItemUpdateRequest req) {
        return cartService.updateItemQuantity(SecurityUtils.currentUserId(), cartItemId, req.quantity());
    }

    @DeleteMapping("/items/{cartItemId}")
    public CartResponse removeItem(@PathVariable Long cartItemId) {
        return cartService.removeItem(SecurityUtils.currentUserId(), cartItemId);
    }

    @DeleteMapping
    public CartResponse clearCart() {
        return cartService.clearCart(SecurityUtils.currentUserId());
    }
}

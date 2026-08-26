package com.foodapp.service;

import com.foodapp.domain.Cart;
import com.foodapp.domain.CartItem;
import com.foodapp.domain.MenuItem;
import com.foodapp.domain.User;
import com.foodapp.dto.response.CartItemResponse;
import com.foodapp.dto.response.CartResponse;
import com.foodapp.exception.ConflictException;
import com.foodapp.exception.NotFoundException;
import com.foodapp.exception.ValidationException;
import com.foodapp.repository.CartItemRepository;
import com.foodapp.repository.CartRepository;
import com.foodapp.repository.MenuItemRepository;
import com.foodapp.repository.UserRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Service
public class CartService {

    private final CartRepository cartRepository;
    private final CartItemRepository cartItemRepository;
    private final MenuItemRepository menuItemRepository;
    private final UserRepository userRepository;

    @Value("${app.order.delivery-fee:40.00}")
    private BigDecimal defaultDeliveryFee;

    @Value("${app.order.free-delivery-threshold:500.00}")
    private BigDecimal freeDeliveryThreshold;

    @Value("${app.cart.max-quantity:20}")
    private int maxQuantity;

    public CartService(CartRepository cartRepository, CartItemRepository cartItemRepository, MenuItemRepository menuItemRepository, UserRepository userRepository) {
        this.cartRepository = cartRepository;
        this.cartItemRepository = cartItemRepository;
        this.menuItemRepository = menuItemRepository;
        this.userRepository = userRepository;
    }

    @Transactional(readOnly = true)
    public CartResponse getCart(Long userId) {
        Cart cart = getOrCreateCartEntity(userId);
        return buildCartResponse(cart);
    }

    @Transactional
    public CartResponse addItem(Long userId, Long menuItemId, int quantity) {
        if (quantity <= 0 || quantity > maxQuantity) {
            throw new ValidationException("Quantity must be between 1 and " + maxQuantity);
        }

        MenuItem menuItem = menuItemRepository.findById(menuItemId)
                .orElseThrow(() -> new NotFoundException("Menu item not found"));

        if (!menuItem.isAvailable() || menuItem.isDeleted()) {
            throw new ConflictException("Item is unavailable", "ITEM_UNAVAILABLE");
        }

        Cart cart = getOrCreateCartEntity(userId);

        if (cart.getRestaurant() != null && !cart.getRestaurant().getId().equals(menuItem.getRestaurant().getId())) {
            throw new ConflictException("Cannot add items from multiple restaurants", "CART_RESTAURANT_MISMATCH");
        }

        if (cart.getRestaurant() == null) {
            cart.setRestaurant(menuItem.getRestaurant());
        }

        Optional<CartItem> existingItem = cart.getItems().stream()
                .filter(i -> i.getMenuItem().getId().equals(menuItemId))
                .findFirst();

        if (existingItem.isPresent()) {
            CartItem item = existingItem.get();
            int newQuantity = item.getQuantity() + quantity;
            if (newQuantity > maxQuantity) newQuantity = maxQuantity;
            item.setQuantity(newQuantity);
        } else {
            CartItem newItem = CartItem.builder()
                    .cart(cart)
                    .menuItem(menuItem)
                    .quantity(quantity)
                    .build();
            cart.addItem(newItem);
        }

        cartRepository.save(cart);
        return buildCartResponse(cart);
    }

    @Transactional
    public CartResponse updateItemQuantity(Long userId, Long cartItemId, int quantity) {
        Cart cart = getOrCreateCartEntity(userId);
        
        CartItem item = cart.getItems().stream()
                .filter(i -> i.getId().equals(cartItemId))
                .findFirst()
                .orElseThrow(() -> new NotFoundException("Cart item not found"));

        if (quantity <= 0) {
            cart.removeItem(item);
        } else {
            if (quantity > maxQuantity) quantity = maxQuantity;
            item.setQuantity(quantity);
        }
        
        checkAndResetRestaurant(cart);
        cartRepository.save(cart);
        return buildCartResponse(cart);
    }

    @Transactional
    public CartResponse removeItem(Long userId, Long cartItemId) {
        Cart cart = getOrCreateCartEntity(userId);
        CartItem item = cart.getItems().stream()
                .filter(i -> i.getId().equals(cartItemId))
                .findFirst()
                .orElseThrow(() -> new NotFoundException("Cart item not found"));

        cart.removeItem(item);
        checkAndResetRestaurant(cart);
        cartRepository.save(cart);
        return buildCartResponse(cart);
    }

    @Transactional
    public CartResponse clearCart(Long userId) {
        Cart cart = getOrCreateCartEntity(userId);
        cart.getItems().clear();
        checkAndResetRestaurant(cart);
        cartRepository.save(cart);
        return buildCartResponse(cart);
    }

    private void checkAndResetRestaurant(Cart cart) {
        if (cart.getItems().isEmpty()) {
            cart.setRestaurant(null);
        }
    }

    private Cart getOrCreateCartEntity(Long userId) {
        return cartRepository.findByUserId(userId).orElseGet(() -> {
            User user = userRepository.findById(userId).orElseThrow(() -> new NotFoundException("User not found"));
            Cart newCart = Cart.builder().user(user).build();
            return cartRepository.save(newCart);
        });
    }

    private CartResponse buildCartResponse(Cart cart) {
        if (cart.getItems() == null || cart.getItems().isEmpty()) {
            return new CartResponse(cart.getId(), null, null, new ArrayList<>(), 0,
                    BigDecimal.ZERO.setScale(2, RoundingMode.HALF_UP),
                    BigDecimal.ZERO.setScale(2, RoundingMode.HALF_UP),
                    BigDecimal.ZERO.setScale(2, RoundingMode.HALF_UP));
        }

        BigDecimal subtotal = BigDecimal.ZERO;
        int itemCount = 0;
        List<CartItemResponse> itemResponses = new ArrayList<>();

        for (CartItem item : cart.getItems()) {
            BigDecimal lineTotal = item.getMenuItem().getPrice().multiply(BigDecimal.valueOf(item.getQuantity()));
            subtotal = subtotal.add(lineTotal);
            itemCount += item.getQuantity();

            itemResponses.add(new CartItemResponse(
                    item.getId(),
                    item.getMenuItem().getId(),
                    item.getMenuItem().getName(),
                    item.getMenuItem().getPrice(),
                    item.getQuantity(),
                    lineTotal,
                    item.getMenuItem().isAvailable(),
                    item.getMenuItem().getImageUrl()
            ));
        }

        BigDecimal deliveryFee = subtotal.compareTo(freeDeliveryThreshold) >= 0 ? BigDecimal.ZERO : defaultDeliveryFee;
        BigDecimal total = subtotal.add(deliveryFee);

        return new CartResponse(
                cart.getId(),
                cart.getRestaurant().getId(),
                cart.getRestaurant().getName(),
                itemResponses,
                itemCount,
                subtotal.setScale(2, RoundingMode.HALF_UP),
                deliveryFee.setScale(2, RoundingMode.HALF_UP),
                total.setScale(2, RoundingMode.HALF_UP)
        );
    }
}

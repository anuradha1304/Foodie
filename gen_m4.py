import os

base_dir = "d:/Downloads/files/src/main/java/com/foodapp"
dto_req_dir = os.path.join(base_dir, "dto", "request")
dto_resp_dir = os.path.join(base_dir, "dto", "response")
service_dir = os.path.join(base_dir, "service")
controller_dir = os.path.join(base_dir, "controller")
test_dir = "d:/Downloads/files/src/test/java/com/foodapp/service"

os.makedirs(test_dir, exist_ok=True)

# DTOs
with open(os.path.join(dto_req_dir, "CartItemAddRequest.java"), "w") as f:
    f.write("""package com.foodapp.dto.request;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
public record CartItemAddRequest(
    @NotNull Long menuItemId,
    @NotNull @Min(1) @Max(20) Integer quantity
) {}
""")

with open(os.path.join(dto_req_dir, "CartItemUpdateRequest.java"), "w") as f:
    f.write("""package com.foodapp.dto.request;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
public record CartItemUpdateRequest(
    @NotNull @Min(0) @Max(20) Integer quantity
) {}
""")

with open(os.path.join(dto_resp_dir, "CartItemResponse.java"), "w") as f:
    f.write("""package com.foodapp.dto.response;
import java.math.BigDecimal;
public record CartItemResponse(
    Long cartItemId,
    Long menuItemId,
    String name,
    BigDecimal unitPrice,
    Integer quantity,
    BigDecimal lineTotal,
    boolean isAvailable,
    String imageUrl
) {}
""")

with open(os.path.join(dto_resp_dir, "CartResponse.java"), "w") as f:
    f.write("""package com.foodapp.dto.response;
import java.math.BigDecimal;
import java.util.List;
public record CartResponse(
    Long cartId,
    Long restaurantId,
    String restaurantName,
    List<CartItemResponse> items,
    Integer itemCount,
    BigDecimal subtotal,
    BigDecimal deliveryFee,
    BigDecimal total
) {}
""")

# Service
with open(os.path.join(service_dir, "CartService.java"), "w") as f:
    f.write("""package com.foodapp.service;

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
""")

# Controller
with open(os.path.join(controller_dir, "CartController.java"), "w") as f:
    f.write("""package com.foodapp.controller;

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
""")

# Test
with open(os.path.join(test_dir, "CartServiceTest.java"), "w") as f:
    f.write("""package com.foodapp.service;

import com.foodapp.domain.Cart;
import com.foodapp.domain.MenuItem;
import com.foodapp.domain.Restaurant;
import com.foodapp.domain.User;
import com.foodapp.domain.enums.Role;
import com.foodapp.exception.ConflictException;
import com.foodapp.repository.CartItemRepository;
import com.foodapp.repository.CartRepository;
import com.foodapp.repository.MenuItemRepository;
import com.foodapp.repository.RestaurantRepository;
import com.foodapp.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.math.BigDecimal;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest(properties = {
    "spring.datasource.url=jdbc:h2:mem:testdb-m4;MODE=MySQL;DB_CLOSE_DELAY=-1",
    "spring.datasource.driverClassName=org.h2.Driver",
    "spring.datasource.username=sa",
    "spring.datasource.password=",
    "spring.jpa.database-platform=org.hibernate.dialect.H2Dialect",
    "spring.jpa.hibernate.ddl-auto=create-drop",
    "spring.sql.init.mode=never"
})
public class CartServiceTest {

    @Autowired private CartService cartService;
    @Autowired private UserRepository userRepository;
    @Autowired private RestaurantRepository restaurantRepository;
    @Autowired private MenuItemRepository menuItemRepository;
    @Autowired private CartRepository cartRepository;
    @Autowired private CartItemRepository cartItemRepository;

    private Long userId;
    private Long r1Id;
    private Long r2Id;
    private Long m1Id;
    private Long m2Id;
    private Long m3Id;

    @BeforeEach
    public void setup() {
        cartItemRepository.deleteAll();
        cartRepository.deleteAll();
        menuItemRepository.deleteAll();
        restaurantRepository.deleteAll();
        userRepository.deleteAll();

        User user = userRepository.save(User.builder().fullName("User").email("u@x.com").passwordHash("hash").phone("123").role(Role.CUSTOMER).enabled(true).build());
        userId = user.getId();

        User owner = userRepository.save(User.builder().fullName("Owner").email("o@x.com").passwordHash("hash").phone("123").role(Role.RESTAURANT_ADMIN).enabled(true).build());

        Restaurant r1 = restaurantRepository.save(Restaurant.builder().name("R1").cuisineType("T1").address("A1").phone("1").isOpen(true).owner(owner).build());
        r1Id = r1.getId();
        
        Restaurant r2 = restaurantRepository.save(Restaurant.builder().name("R2").cuisineType("T2").address("A2").phone("2").isOpen(true).owner(User.builder().fullName("O2").email("o2@x.com").passwordHash("h").phone("2").role(Role.RESTAURANT_ADMIN).enabled(true).build()).build());
        r2Id = r2.getId();

        m1Id = menuItemRepository.save(MenuItem.builder().restaurant(r1).name("M1").category("C1").price(new BigDecimal("100.00")).isAvailable(true).isDeleted(false).build()).getId();
        m2Id = menuItemRepository.save(MenuItem.builder().restaurant(r1).name("M2").category("C1").price(new BigDecimal("200.00")).isAvailable(false).isDeleted(false).build()).getId();
        m3Id = menuItemRepository.save(MenuItem.builder().restaurant(r2).name("M3").category("C1").price(new BigDecimal("300.00")).isAvailable(true).isDeleted(false).build()).getId();
    }

    @Test
    public void testAddUnavailableItemThrows() {
        assertThrows(ConflictException.class, () -> cartService.addItem(userId, m2Id, 1));
    }

    @Test
    public void testAddMultipleRestaurantsThrows() {
        cartService.addItem(userId, m1Id, 1);
        ConflictException ex = assertThrows(ConflictException.class, () -> cartService.addItem(userId, m3Id, 1));
        assertEquals("CART_RESTAURANT_MISMATCH", ex.getCode());
    }

    @Test
    public void testQuantityUpdatesAndTotals() {
        var resp = cartService.addItem(userId, m1Id, 2);
        assertEquals(1, resp.items().size());
        assertEquals(2, resp.itemCount());
        assertEquals(new BigDecimal("200.00"), resp.subtotal());
        
        // Update quantity
        Long cartItemId = resp.items().get(0).cartItemId();
        resp = cartService.updateItemQuantity(userId, cartItemId, 5);
        assertEquals(5, resp.itemCount());
        assertEquals(new BigDecimal("500.00"), resp.subtotal());
        
        // Remove item clears restaurant
        resp = cartService.updateItemQuantity(userId, cartItemId, 0);
        assertEquals(0, resp.itemCount());
        assertNull(resp.restaurantId());
    }
}
""")

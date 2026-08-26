package com.foodapp.service;

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
        
        User o2 = userRepository.save(User.builder().fullName("O2").email("o2@x.com").passwordHash("h").phone("2").role(Role.RESTAURANT_ADMIN).enabled(true).build());
        Restaurant r2 = restaurantRepository.save(Restaurant.builder().name("R2").cuisineType("T2").address("A2").phone("2").isOpen(true).owner(o2).build());
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

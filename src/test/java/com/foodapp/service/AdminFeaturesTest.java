package com.foodapp.service;

import com.foodapp.domain.MenuItem;
import com.foodapp.domain.Order;
import com.foodapp.domain.Restaurant;
import com.foodapp.domain.User;
import com.foodapp.domain.enums.OrderStatus;
import com.foodapp.domain.enums.Role;
import com.foodapp.dto.request.MenuItemRequest;
import com.foodapp.exception.ConflictException;
import com.foodapp.exception.ForbiddenException;
import com.foodapp.repository.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.orm.ObjectOptimisticLockingFailureException;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest(properties = {
    "spring.datasource.url=jdbc:h2:mem:testdb-m6;MODE=MySQL;DB_CLOSE_DELAY=-1",
    "spring.datasource.driverClassName=org.h2.Driver",
    "spring.datasource.username=sa",
    "spring.datasource.password=",
    "spring.jpa.database-platform=org.hibernate.dialect.H2Dialect",
    "spring.jpa.hibernate.ddl-auto=create-drop",
    "spring.sql.init.mode=never"
})
public class AdminFeaturesTest {

    @Autowired private MenuService menuService;
    @Autowired private OrderStatusService orderStatusService;
    @Autowired private UserRepository userRepository;
    @Autowired private RestaurantRepository restaurantRepository;
    @Autowired private MenuItemRepository menuItemRepository;
    @Autowired private OrderRepository orderRepository;
    @Autowired private OrderStatusHistoryRepository historyRepository;

    private Long admin1Id;
    private Long admin2Id;
    private Long r1Id;
    private Long orderId;

    @BeforeEach
    public void setup() {
        historyRepository.deleteAll();
        orderRepository.deleteAll();
        menuItemRepository.deleteAll();
        restaurantRepository.deleteAll();
        userRepository.deleteAll();

        User a1 = userRepository.save(User.builder().fullName("A1").email("a1@x.com").passwordHash("hash").phone("123").role(Role.RESTAURANT_ADMIN).enabled(true).build());
        admin1Id = a1.getId();
        User a2 = userRepository.save(User.builder().fullName("A2").email("a2@x.com").passwordHash("hash").phone("123").role(Role.RESTAURANT_ADMIN).enabled(true).build());
        admin2Id = a2.getId();
        User c = userRepository.save(User.builder().fullName("C").email("c@x.com").passwordHash("hash").phone("123").role(Role.CUSTOMER).enabled(true).build());

        Restaurant r1 = restaurantRepository.save(Restaurant.builder().name("R1").cuisineType("T1").address("A1").phone("1").isOpen(true).owner(a1).build());
        r1Id = r1.getId();

        Restaurant r2 = restaurantRepository.save(Restaurant.builder().name("R2").cuisineType("T1").address("A1").phone("1").isOpen(true).owner(a2).build());

        Order o = new Order();
        o.setOrderNumber("ORD-1");
        o.setCustomer(c);
        o.setRestaurant(r1);
        o.setStatus(OrderStatus.PLACED);
        o.setSubtotal(BigDecimal.TEN);
        o.setDeliveryFee(BigDecimal.ZERO);
        o.setTotalAmount(BigDecimal.TEN);
        o.setDeliveryAddress("A");
        o.setPlacedAt(LocalDateTime.now());
        o.setUpdatedAt(LocalDateTime.now());
        orderId = orderRepository.save(o).getId();
    }

    @Test
    public void testAdminSecurity() {
        // a2 DOES own a restaurant (R2)! So addMenuItem should succeed but for R2.
        assertDoesNotThrow(() -> menuService.addMenuItem(admin2Id, new MenuItemRequest("N", "D", "C", BigDecimal.ONE, null, true)));
        
        // However, admin2 updating orderId (which belongs to R1) should fail
        assertThrows(ForbiddenException.class, () -> orderStatusService.acceptOrder(admin2Id, orderId));
    }

    @Test
    public void testStatusTransitions() {
        assertThrows(ConflictException.class, () -> orderStatusService.updateStatus(admin1Id, orderId, "PREPARING", null)); // PLACED -> PREPARING is invalid
        orderStatusService.acceptOrder(admin1Id, orderId);
        assertThrows(ConflictException.class, () -> orderStatusService.rejectOrder(admin1Id, orderId, "Reason")); // ACCEPTED -> REJECTED is invalid
    }

    @Test
    public void testOptimisticLockingOnOrder() {
        // Read order manually to simulate concurrent modification
        Order o = orderRepository.findById(orderId).get();
        orderStatusService.acceptOrder(admin1Id, orderId); // Updates version in DB
        
        // Try to save old object
        o.setStatus(OrderStatus.REJECTED);
        assertThrows(ObjectOptimisticLockingFailureException.class, () -> orderRepository.save(o));
    }
}

package com.foodapp.service;

import com.foodapp.domain.*;
import com.foodapp.domain.enums.OrderStatus;
import com.foodapp.domain.enums.Role;
import com.foodapp.event.OrderPlacedEvent;
import com.foodapp.repository.*;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.SpyBean;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.timeout;
import static org.mockito.Mockito.verify;

@SpringBootTest(properties = {
    "spring.datasource.url=jdbc:h2:mem:testdb-m7;MODE=MySQL;DB_CLOSE_DELAY=-1",
    "spring.datasource.driverClassName=org.h2.Driver",
    "spring.datasource.username=sa",
    "spring.datasource.password=",
    "spring.jpa.database-platform=org.hibernate.dialect.H2Dialect",
    "spring.jpa.hibernate.ddl-auto=create-drop",
    "spring.sql.init.mode=never"
})
public class NotificationAsyncTest {

    @Autowired private ApplicationEventPublisher eventPublisher;
    @Autowired private UserRepository userRepository;
    @Autowired private RestaurantRepository restaurantRepository;
    @Autowired private OrderRepository orderRepository;
    @SpyBean private NotificationService notificationService;

    @Autowired private org.springframework.transaction.support.TransactionTemplate transactionTemplate;

    @Test
    public void testAsyncNotificationAfterCommit() {
        transactionTemplate.execute(status -> {
            User c = userRepository.save(User.builder().fullName("C").email("c_async@x.com").passwordHash("hash").phone("123").role(Role.CUSTOMER).enabled(true).build());
            User a = userRepository.save(User.builder().fullName("A").email("a_async@x.com").passwordHash("hash").phone("123").role(Role.RESTAURANT_ADMIN).enabled(true).build());
            Restaurant r = restaurantRepository.save(Restaurant.builder().name("R").cuisineType("T1").address("A1").phone("1").isOpen(true).owner(a).build());

            Order o = new Order();
            o.setOrderNumber("ORD-TEST");
            o.setCustomer(c);
            o.setRestaurant(r);
            o.setStatus(OrderStatus.PLACED);
            o.setSubtotal(BigDecimal.TEN);
            o.setDeliveryFee(BigDecimal.ZERO);
            o.setTotalAmount(BigDecimal.TEN);
            o.setDeliveryAddress("A");
            o.setPlacedAt(LocalDateTime.now());
            o.setUpdatedAt(LocalDateTime.now());
            orderRepository.save(o);
            
            eventPublisher.publishEvent(new OrderPlacedEvent(o));
            return null;
        });
        
        verify(notificationService, timeout(2000).times(1)).handleOrderPlaced(any(OrderPlacedEvent.class));
    }
}

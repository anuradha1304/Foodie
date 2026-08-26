import os

base_dir = "d:/Downloads/files/src/main/java/com/foodapp"
config_dir = os.path.join(base_dir, "config")
service_dir = os.path.join(base_dir, "service")
event_dir = os.path.join(base_dir, "event")
test_dir = "d:/Downloads/files/src/test/java/com/foodapp/service"

os.makedirs(config_dir, exist_ok=True)
os.makedirs(event_dir, exist_ok=True)
os.makedirs(test_dir, exist_ok=True)

# 1. AsyncConfig
with open(os.path.join(config_dir, "AsyncConfig.java"), "w") as f:
    f.write("""package com.foodapp.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;

import java.util.concurrent.ThreadPoolExecutor;

@Configuration
@EnableAsync
public class AsyncConfig {
    @Bean("taskExecutor")
    public ThreadPoolTaskExecutor taskExecutor() {
        ThreadPoolTaskExecutor ex = new ThreadPoolTaskExecutor();
        ex.setCorePoolSize(4);
        ex.setMaxPoolSize(10);
        ex.setQueueCapacity(50);
        ex.setThreadNamePrefix("foodapp-async-");
        ex.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        ex.initialize();
        return ex;
    }
}
""")

# 2. Events
with open(os.path.join(event_dir, "OrderPlacedEvent.java"), "w") as f:
    f.write("""package com.foodapp.event;
import com.foodapp.domain.Order;
public record OrderPlacedEvent(Order order) {}
""")

with open(os.path.join(event_dir, "OrderStatusChangedEvent.java"), "w") as f:
    f.write("""package com.foodapp.event;
import com.foodapp.domain.Order;
import com.foodapp.domain.enums.OrderStatus;
public record OrderStatusChangedEvent(Order order, OrderStatus oldStatus, OrderStatus newStatus) {}
""")

# 3. NotificationService
with open(os.path.join(service_dir, "NotificationService.java"), "w") as f:
    f.write("""package com.foodapp.service;

import com.foodapp.event.OrderPlacedEvent;
import com.foodapp.event.OrderStatusChangedEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.event.TransactionPhase;
import org.springframework.transaction.event.TransactionalEventListener;

@Service
public class NotificationService {
    
    private static final Logger log = LoggerFactory.getLogger(NotificationService.class);

    @Async("taskExecutor")
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void handleOrderPlaced(OrderPlacedEvent event) {
        log.info("Async Notification: Sending order confirmation for order {} to {}", 
                 event.order().getOrderNumber(), event.order().getCustomer().getEmail());
        // Simulate email sending delay
        try { Thread.sleep(500); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
    }

    @Async("taskExecutor")
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void handleOrderStatusChanged(OrderStatusChangedEvent event) {
        log.info("Async Notification: Order {} status changed from {} to {}. Notifying {}", 
                 event.order().getOrderNumber(), event.oldStatus(), event.newStatus(), 
                 event.order().getCustomer().getEmail());
        // Simulate email sending delay
        try { Thread.sleep(500); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
    }
}
""")

# 4. Update OrderService
with open(os.path.join(service_dir, "OrderService.java"), "r") as f:
    os_content = f.read()

if "ApplicationEventPublisher" not in os_content:
    os_content = os_content.replace("import org.springframework.stereotype.Service;", "import org.springframework.stereotype.Service;\nimport org.springframework.context.ApplicationEventPublisher;\nimport com.foodapp.event.OrderPlacedEvent;\nimport com.foodapp.event.OrderStatusChangedEvent;")
    os_content = os_content.replace("private final UserRepository userRepository;", "private final UserRepository userRepository;\n    private final ApplicationEventPublisher eventPublisher;")
    os_content = os_content.replace("UserRepository userRepository) {", "UserRepository userRepository, ApplicationEventPublisher eventPublisher) {")
    os_content = os_content.replace("this.userRepository = userRepository;", "this.userRepository = userRepository;\n        this.eventPublisher = eventPublisher;")
    os_content = os_content.replace("cartRepository.save(cart);", "cartRepository.save(cart);\n        eventPublisher.publishEvent(new OrderPlacedEvent(order));")
    
    cancel_target = "orderRepository.save(o);\n        \n        OrderStatusHistory history"
    os_content = os_content.replace(cancel_target, "orderRepository.save(o);\n        eventPublisher.publishEvent(new OrderStatusChangedEvent(o, OrderStatus.PLACED, OrderStatus.CANCELLED));\n        \n        OrderStatusHistory history")
    
    with open(os.path.join(service_dir, "OrderService.java"), "w") as f:
        f.write(os_content)

# 5. Update OrderStatusService
with open(os.path.join(service_dir, "OrderStatusService.java"), "r") as f:
    oss_content = f.read()

if "ApplicationEventPublisher" not in oss_content:
    oss_content = oss_content.replace("import org.springframework.stereotype.Service;", "import org.springframework.stereotype.Service;\nimport org.springframework.context.ApplicationEventPublisher;\nimport com.foodapp.event.OrderStatusChangedEvent;")
    oss_content = oss_content.replace("private final UserRepository userRepository;", "private final UserRepository userRepository;\n    private final ApplicationEventPublisher eventPublisher;")
    oss_content = oss_content.replace("UserRepository userRepository) {", "UserRepository userRepository, ApplicationEventPublisher eventPublisher) {")
    oss_content = oss_content.replace("this.userRepository = userRepository;", "this.userRepository = userRepository;\n        this.eventPublisher = eventPublisher;")
    
    # In rejectOrder
    oss_content = oss_content.replace("o.setStatus(OrderStatus.REJECTED);", "OrderStatus oldStatus = o.getStatus();\n        o.setStatus(OrderStatus.REJECTED);")
    oss_content = oss_content.replace("addHistory(o, OrderStatus.REJECTED, reason, adminId);", "addHistory(o, OrderStatus.REJECTED, reason, adminId);\n        eventPublisher.publishEvent(new OrderStatusChangedEvent(o, oldStatus, OrderStatus.REJECTED));")
    
    # In advanceStatus
    oss_content = oss_content.replace("o.setStatus(newStatus);", "OrderStatus oldStatus = o.getStatus();\n        o.setStatus(newStatus);")
    oss_content = oss_content.replace("addHistory(o, newStatus, note, adminId);", "addHistory(o, newStatus, note, adminId);\n        eventPublisher.publishEvent(new OrderStatusChangedEvent(o, oldStatus, newStatus));")

    with open(os.path.join(service_dir, "OrderStatusService.java"), "w") as f:
        f.write(oss_content)

# 6. Async Test
with open(os.path.join(test_dir, "NotificationAsyncTest.java"), "w") as f:
    f.write("""package com.foodapp.service;

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

    @Test
    public void testAsyncNotificationAfterCommit() {
        // We simulate saving an order and firing an event.
        // We will do it in a transaction so AFTER_COMMIT fires.
        
        saveOrderAndFireEvent();
        
        // The event listener is AFTER_COMMIT and @Async, so we must wait up to 2 seconds for it to be called.
        verify(notificationService, timeout(2000).times(1)).handleOrderPlaced(any(OrderPlacedEvent.class));
    }
    
    @Transactional
    public void saveOrderAndFireEvent() {
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
    }
}
""")

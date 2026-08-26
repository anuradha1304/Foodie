import os

base_dir = "d:/Downloads/files/src/main/java/com/foodapp"
dto_req_dir = os.path.join(base_dir, "dto", "request")
dto_resp_dir = os.path.join(base_dir, "dto", "response")
service_dir = os.path.join(base_dir, "service")
controller_dir = os.path.join(base_dir, "controller", "admin")
test_dir = "d:/Downloads/files/src/test/java/com/foodapp/service"

os.makedirs(controller_dir, exist_ok=True)

# DTOs
with open(os.path.join(dto_req_dir, "MenuItemRequest.java"), "w") as f:
    f.write("""package com.foodapp.dto.request;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.math.BigDecimal;
public record MenuItemRequest(
    @NotBlank String name,
    String description,
    @NotBlank String category,
    @NotNull @DecimalMin("0.01") BigDecimal price,
    String imageUrl,
    @NotNull Boolean isAvailable
) {}
""")

with open(os.path.join(dto_req_dir, "AvailabilityRequest.java"), "w") as f:
    f.write("""package com.foodapp.dto.request;
import jakarta.validation.constraints.NotNull;
public record AvailabilityRequest(
    @NotNull Boolean isAvailable
) {}
""")

with open(os.path.join(dto_req_dir, "RestaurantStatusRequest.java"), "w") as f:
    f.write("""package com.foodapp.dto.request;
import jakarta.validation.constraints.NotNull;
public record RestaurantStatusRequest(
    @NotNull Boolean isOpen
) {}
""")

with open(os.path.join(dto_req_dir, "RejectOrderRequest.java"), "w") as f:
    f.write("""package com.foodapp.dto.request;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
public record RejectOrderRequest(
    @NotBlank @Size(min = 5, max = 300) String reason
) {}
""")

with open(os.path.join(dto_req_dir, "UpdateOrderStatusRequest.java"), "w") as f:
    f.write("""package com.foodapp.dto.request;
import jakarta.validation.constraints.NotBlank;
public record UpdateOrderStatusRequest(
    @NotBlank String status,
    String note
) {}
""")

with open(os.path.join(dto_resp_dir, "MenuItemAdminResponse.java"), "w") as f:
    f.write("""package com.foodapp.dto.response;
import java.math.BigDecimal;
public record MenuItemAdminResponse(
    Long id,
    String name,
    String description,
    String category,
    BigDecimal price,
    String imageUrl,
    boolean isAvailable,
    boolean isDeleted
) {}
""")

with open(os.path.join(dto_resp_dir, "AdminOrderSummary.java"), "w") as f:
    f.write("""package com.foodapp.dto.response;
import java.math.BigDecimal;
public record AdminOrderSummary(
    Long id,
    String orderNumber,
    String customerName,
    String customerPhone,
    String status,
    BigDecimal totalAmount,
    Integer itemCount,
    java.time.LocalDateTime placedAt
) {}
""")

# Services
with open(os.path.join(service_dir, "MenuService.java"), "w") as f:
    f.write("""package com.foodapp.service;

import com.foodapp.domain.MenuItem;
import com.foodapp.domain.Restaurant;
import com.foodapp.dto.request.MenuItemRequest;
import com.foodapp.dto.response.MenuItemAdminResponse;
import com.foodapp.dto.response.RestaurantDetail;
import com.foodapp.exception.ConflictException;
import com.foodapp.exception.ForbiddenException;
import com.foodapp.exception.NotFoundException;
import com.foodapp.repository.MenuItemRepository;
import com.foodapp.repository.RestaurantRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class MenuService {

    private final MenuItemRepository menuItemRepository;
    private final RestaurantRepository restaurantRepository;

    public MenuService(MenuItemRepository menuItemRepository, RestaurantRepository restaurantRepository) {
        this.menuItemRepository = menuItemRepository;
        this.restaurantRepository = restaurantRepository;
    }

    private Restaurant getOwnedRestaurant(Long adminId) {
        return restaurantRepository.findByOwnerId(adminId)
                .orElseThrow(() -> new ForbiddenException("You do not own a restaurant"));
    }

    @Transactional(readOnly = true)
    public List<MenuItemAdminResponse> getMenuItems(Long adminId) {
        Restaurant r = getOwnedRestaurant(adminId);
        return menuItemRepository.findByRestaurantId(r.getId()).stream()
                .map(m -> new MenuItemAdminResponse(
                        m.getId(), m.getName(), m.getDescription(), m.getCategory(),
                        m.getPrice(), m.getImageUrl(), m.isAvailable(), m.isDeleted()
                )).toList();
    }

    @Transactional
    public MenuItemAdminResponse addMenuItem(Long adminId, MenuItemRequest req) {
        Restaurant r = getOwnedRestaurant(adminId);
        MenuItem mi = new MenuItem();
        mi.setRestaurant(r);
        mi.setName(req.name());
        mi.setDescription(req.description());
        mi.setCategory(req.category());
        mi.setPrice(req.price());
        mi.setImageUrl(req.imageUrl());
        mi.setAvailable(req.isAvailable());
        mi.setDeleted(false);
        mi = menuItemRepository.save(mi);
        return mapToAdminResponse(mi);
    }

    @Transactional
    public MenuItemAdminResponse updateMenuItem(Long adminId, Long id, MenuItemRequest req) {
        MenuItem mi = getOwnedMenuItem(adminId, id);
        mi.setName(req.name());
        mi.setDescription(req.description());
        mi.setCategory(req.category());
        mi.setPrice(req.price());
        mi.setImageUrl(req.imageUrl());
        mi.setAvailable(req.isAvailable());
        mi = menuItemRepository.save(mi);
        return mapToAdminResponse(mi);
    }

    @Transactional
    public MenuItemAdminResponse updateAvailability(Long adminId, Long id, boolean isAvailable) {
        MenuItem mi = getOwnedMenuItem(adminId, id);
        mi.setAvailable(isAvailable);
        mi = menuItemRepository.save(mi);
        return mapToAdminResponse(mi);
    }

    @Transactional
    public void deleteMenuItem(Long adminId, Long id) {
        MenuItem mi = getOwnedMenuItem(adminId, id);
        mi.setDeleted(true);
        mi.setAvailable(false);
        menuItemRepository.save(mi);
    }

    @Transactional
    public RestaurantDetail updateRestaurantStatus(Long adminId, boolean isOpen) {
        Restaurant r = getOwnedRestaurant(adminId);
        r.setOpen(isOpen);
        r = restaurantRepository.save(r);
        return new RestaurantDetail(r.getId(), r.getName(), r.getCuisineType(), r.getAddress(), r.getPhone(), r.getImageUrl(), r.isOpen());
    }

    private MenuItem getOwnedMenuItem(Long adminId, Long menuItemId) {
        Restaurant r = getOwnedRestaurant(adminId);
        MenuItem mi = menuItemRepository.findById(menuItemId)
                .orElseThrow(() -> new NotFoundException("Menu item not found"));
        if (!mi.getRestaurant().getId().equals(r.getId())) {
            throw new ForbiddenException("Not your menu item");
        }
        return mi;
    }

    private MenuItemAdminResponse mapToAdminResponse(MenuItem m) {
        return new MenuItemAdminResponse(m.getId(), m.getName(), m.getDescription(), m.getCategory(),
                m.getPrice(), m.getImageUrl(), m.isAvailable(), m.isDeleted());
    }
}
""")

with open(os.path.join(service_dir, "OrderStatusService.java"), "w") as f:
    f.write("""package com.foodapp.service;

import com.foodapp.domain.Order;
import com.foodapp.domain.OrderStatusHistory;
import com.foodapp.domain.Restaurant;
import com.foodapp.domain.enums.OrderStatus;
import com.foodapp.dto.response.AdminOrderSummary;
import com.foodapp.dto.response.OrderItemResponse;
import com.foodapp.dto.response.OrderResponse;
import com.foodapp.dto.response.OrderStatusHistoryResponse;
import com.foodapp.exception.ConflictException;
import com.foodapp.exception.ForbiddenException;
import com.foodapp.exception.NotFoundException;
import com.foodapp.repository.OrderItemRepository;
import com.foodapp.repository.OrderRepository;
import com.foodapp.repository.OrderStatusHistoryRepository;
import com.foodapp.repository.RestaurantRepository;
import com.foodapp.repository.UserRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class OrderStatusService {

    private final OrderRepository orderRepository;
    private final OrderItemRepository orderItemRepository;
    private final OrderStatusHistoryRepository historyRepository;
    private final RestaurantRepository restaurantRepository;
    private final UserRepository userRepository;

    public OrderStatusService(OrderRepository orderRepository, OrderItemRepository orderItemRepository,
                              OrderStatusHistoryRepository historyRepository, RestaurantRepository restaurantRepository,
                              UserRepository userRepository) {
        this.orderRepository = orderRepository;
        this.orderItemRepository = orderItemRepository;
        this.historyRepository = historyRepository;
        this.restaurantRepository = restaurantRepository;
        this.userRepository = userRepository;
    }

    private Restaurant getOwnedRestaurant(Long adminId) {
        return restaurantRepository.findByOwnerId(adminId)
                .orElseThrow(() -> new ForbiddenException("You do not own a restaurant"));
    }

    private Order getOwnedOrder(Long adminId, Long orderId) {
        Restaurant r = getOwnedRestaurant(adminId);
        Order o = orderRepository.findWithItemsById(orderId)
                .orElseThrow(() -> new NotFoundException("Order not found"));
        if (!o.getRestaurant().getId().equals(r.getId())) {
            throw new ForbiddenException("Not your order");
        }
        return o;
    }

    @Transactional(readOnly = true)
    public Page<AdminOrderSummary> getOrders(Long adminId, String status, int page, int size) {
        Restaurant r = getOwnedRestaurant(adminId);
        Page<Order> orders;
        if (status == null || status.isBlank()) {
            orders = orderRepository.findByRestaurantIdOrderByPlacedAtDesc(r.getId(), PageRequest.of(page, size));
        } else {
            OrderStatus os = OrderStatus.valueOf(status.toUpperCase());
            orders = orderRepository.findByRestaurantIdAndStatusOrderByPlacedAtDesc(r.getId(), os, PageRequest.of(page, size));
        }
        return orders.map(o -> new AdminOrderSummary(
                o.getId(), o.getOrderNumber(), o.getCustomer().getFullName(), o.getCustomer().getPhone(),
                o.getStatus().name(), o.getTotalAmount(), orderItemRepository.countByOrderId(o.getId()), o.getPlacedAt()
        ));
    }

    @Transactional(readOnly = true)
    public OrderResponse getOrderDetails(Long adminId, Long orderId) {
        Order o = getOwnedOrder(adminId, orderId);
        return buildOrderResponse(o);
    }

    @Transactional
    public OrderResponse acceptOrder(Long adminId, Long orderId) {
        return advanceStatus(adminId, orderId, OrderStatus.ACCEPTED, null);
    }

    @Transactional
    public OrderResponse rejectOrder(Long adminId, Long orderId, String reason) {
        Order o = getOwnedOrder(adminId, orderId);
        if (o.getStatus() != OrderStatus.PLACED) {
            throw new ConflictException("Cannot reject order in status " + o.getStatus(), "INVALID_STATUS_TRANSITION");
        }
        o.setStatus(OrderStatus.REJECTED);
        o.setRejectionReason(reason);
        o.setUpdatedAt(LocalDateTime.now());
        o = orderRepository.save(o);
        addHistory(o, OrderStatus.REJECTED, reason, adminId);
        return buildOrderResponse(o);
    }

    @Transactional
    public OrderResponse updateStatus(Long adminId, Long orderId, String newStatusStr, String note) {
        OrderStatus newStatus = OrderStatus.valueOf(newStatusStr.toUpperCase());
        return advanceStatus(adminId, orderId, newStatus, note);
    }

    private OrderResponse advanceStatus(Long adminId, Long orderId, OrderStatus newStatus, String note) {
        Order o = getOwnedOrder(adminId, orderId);
        if (!isValidTransition(o.getStatus(), newStatus)) {
            throw new ConflictException("Invalid transition from " + o.getStatus() + " to " + newStatus, "INVALID_STATUS_TRANSITION");
        }
        o.setStatus(newStatus);
        o.setUpdatedAt(LocalDateTime.now());
        o = orderRepository.save(o); // Will throw OptimisticLockingFailureException on conflict
        addHistory(o, newStatus, note, adminId);
        return buildOrderResponse(o);
    }

    private boolean isValidTransition(OrderStatus from, OrderStatus to) {
        if (from == OrderStatus.PLACED && to == OrderStatus.ACCEPTED) return true;
        if (from == OrderStatus.ACCEPTED && to == OrderStatus.PREPARING) return true;
        if (from == OrderStatus.PREPARING && to == OrderStatus.OUT_FOR_DELIVERY) return true;
        if (from == OrderStatus.OUT_FOR_DELIVERY && to == OrderStatus.DELIVERED) return true;
        return false;
    }

    private void addHistory(Order o, OrderStatus status, String note, Long adminId) {
        OrderStatusHistory h = new OrderStatusHistory();
        h.setOrder(o);
        h.setStatus(status);
        h.setNote(note);
        h.setChangedByUser(userRepository.getReferenceById(adminId));
        h.setChangedAt(LocalDateTime.now());
        historyRepository.save(h);
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
""")

# Controllers
with open(os.path.join(controller_dir, "AdminMenuController.java"), "w") as f:
    f.write("""package com.foodapp.controller.admin;

import com.foodapp.dto.request.AvailabilityRequest;
import com.foodapp.dto.request.MenuItemRequest;
import com.foodapp.dto.request.RestaurantStatusRequest;
import com.foodapp.dto.response.MenuItemAdminResponse;
import com.foodapp.dto.response.RestaurantDetail;
import com.foodapp.security.SecurityUtils;
import com.foodapp.service.MenuService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/admin")
public class AdminMenuController {

    private final MenuService menuService;

    public AdminMenuController(MenuService menuService) {
        this.menuService = menuService;
    }

    @GetMapping("/menu")
    public List<MenuItemAdminResponse> getMenuItems() {
        return menuService.getMenuItems(SecurityUtils.currentUserId());
    }

    @PostMapping("/menu")
    @ResponseStatus(HttpStatus.CREATED)
    public MenuItemAdminResponse addMenuItem(@Valid @RequestBody MenuItemRequest req) {
        return menuService.addMenuItem(SecurityUtils.currentUserId(), req);
    }

    @PutMapping("/menu/{id}")
    public MenuItemAdminResponse updateMenuItem(@PathVariable Long id, @Valid @RequestBody MenuItemRequest req) {
        return menuService.updateMenuItem(SecurityUtils.currentUserId(), id, req);
    }

    @PatchMapping("/menu/{id}/availability")
    public MenuItemAdminResponse updateAvailability(@PathVariable Long id, @Valid @RequestBody AvailabilityRequest req) {
        return menuService.updateAvailability(SecurityUtils.currentUserId(), id, req.isAvailable());
    }

    @DeleteMapping("/menu/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deleteMenuItem(@PathVariable Long id) {
        menuService.deleteMenuItem(SecurityUtils.currentUserId(), id);
    }

    @PatchMapping("/restaurant/status")
    public RestaurantDetail updateRestaurantStatus(@Valid @RequestBody RestaurantStatusRequest req) {
        return menuService.updateRestaurantStatus(SecurityUtils.currentUserId(), req.isOpen());
    }
}
""")

with open(os.path.join(controller_dir, "AdminOrderController.java"), "w") as f:
    f.write("""package com.foodapp.controller.admin;

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
""")

# Updates to Repositories
repo_dir = os.path.join(base_dir, "repository")

with open(os.path.join(repo_dir, "MenuItemRepository.java"), "r") as f:
    menu_content = f.read()
if "findByRestaurantId" not in menu_content:
    new_method = "java.util.List<com.foodapp.domain.MenuItem> findByRestaurantId(Long restaurantId);"
    menu_content = menu_content.replace("}", new_method + "\n}")
    with open(os.path.join(repo_dir, "MenuItemRepository.java"), "w") as f:
        f.write(menu_content)

with open(os.path.join(repo_dir, "OrderRepository.java"), "r") as f:
    order_content = f.read()
if "findByRestaurantIdOrderByPlacedAtDesc" not in order_content:
    new_method = """
    org.springframework.data.domain.Page<com.foodapp.domain.Order> findByRestaurantIdOrderByPlacedAtDesc(Long restaurantId, org.springframework.data.domain.Pageable pageable);
    org.springframework.data.domain.Page<com.foodapp.domain.Order> findByRestaurantIdAndStatusOrderByPlacedAtDesc(Long restaurantId, com.foodapp.domain.enums.OrderStatus status, org.springframework.data.domain.Pageable pageable);
"""
    order_content = order_content.replace("}", new_method + "\n}")
    with open(os.path.join(repo_dir, "OrderRepository.java"), "w") as f:
        f.write(order_content)

# Tests
with open(os.path.join(test_dir, "AdminFeaturesTest.java"), "w") as f:
    f.write("""package com.foodapp.service;

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
        assertThrows(ForbiddenException.class, () -> menuService.addMenuItem(admin2Id, new MenuItemRequest("N", "D", "C", BigDecimal.ONE, null, true)));
        // Wait, a2 DOES own a restaurant (R2)! So addMenuItem should succeed but for R2.
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
""")

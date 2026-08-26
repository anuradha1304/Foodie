import os

base_dir = "d:/Downloads/files/src/main/java/com/foodapp"
domain_dir = os.path.join(base_dir, "domain")
enums_dir = os.path.join(domain_dir, "enums")
repo_dir = os.path.join(base_dir, "repository")

os.makedirs(enums_dir, exist_ok=True)
os.makedirs(repo_dir, exist_ok=True)

# Enums
with open(os.path.join(enums_dir, "Role.java"), "w") as f:
    f.write("""package com.foodapp.domain.enums;
public enum Role { CUSTOMER, RESTAURANT_ADMIN }
""")

with open(os.path.join(enums_dir, "OrderStatus.java"), "w") as f:
    f.write("""package com.foodapp.domain.enums;
public enum OrderStatus { PLACED, ACCEPTED, REJECTED, PREPARING, OUT_FOR_DELIVERY, DELIVERED, CANCELLED }
""")

# Entities
with open(os.path.join(domain_dir, "User.java"), "w") as f:
    f.write("""package com.foodapp.domain;

import com.foodapp.domain.enums.Role;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import java.time.LocalDateTime;

@Entity
@Table(name = "users", uniqueConstraints = {
    @UniqueConstraint(name = "uk_users_email", columnNames = "email")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "full_name", length = 120, nullable = false)
    private String fullName;

    @Column(length = 180, nullable = false)
    private String email;

    @Column(name = "password_hash", length = 100, nullable = false)
    private String passwordHash;

    @Column(length = 20, nullable = false)
    private String phone;

    @Enumerated(EnumType.STRING)
    @Column(length = 30, nullable = false)
    private Role role;

    @Column(nullable = false)
    private boolean enabled = true;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
}
""")

with open(os.path.join(domain_dir, "Restaurant.java"), "w") as f:
    f.write("""package com.foodapp.domain;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import java.time.LocalDateTime;

@Entity
@Table(name = "restaurants", indexes = {
    @Index(name = "idx_restaurant_cuisine", columnList = "cuisine_type")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Restaurant {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(length = 150, nullable = false)
    private String name;

    @Column(length = 500)
    private String description;

    @Column(name = "cuisine_type", length = 60, nullable = false)
    private String cuisineType;

    @Column(length = 300, nullable = false)
    private String address;

    @Column(length = 20, nullable = false)
    private String phone;

    @Column(name = "image_url", length = 500)
    private String imageUrl;

    @Column(name = "is_open", nullable = false)
    private boolean isOpen = true;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "owner_id", nullable = false, unique = true)
    private User owner;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
}
""")

with open(os.path.join(domain_dir, "MenuItem.java"), "w") as f:
    f.write("""package com.foodapp.domain;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "menu_items", indexes = {
    @Index(name = "idx_menu_restaurant_avail", columnList = "restaurant_id, is_available, is_deleted")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MenuItem {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "restaurant_id", nullable = false)
    private Restaurant restaurant;

    @Column(length = 150, nullable = false)
    private String name;

    @Column(length = 500)
    private String description;

    @Column(length = 60, nullable = false)
    private String category;

    @Column(nullable = false, columnDefinition = "DECIMAL(10,2) CHECK (price > 0)")
    private BigDecimal price;

    @Column(name = "image_url", length = 500)
    private String imageUrl;

    @Column(name = "is_available", nullable = false)
    private boolean isAvailable = true;

    @Column(name = "is_deleted", nullable = false)
    private boolean isDeleted = false;

    @Version
    @Column(nullable = false)
    private Long version = 0L;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;
}
""")

with open(os.path.join(domain_dir, "Cart.java"), "w") as f:
    f.write("""package com.foodapp.domain;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.UpdateTimestamp;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "carts")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Cart {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false, unique = true)
    private User user;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "restaurant_id")
    private Restaurant restaurant;

    @OneToMany(mappedBy = "cart", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<CartItem> items = new ArrayList<>();

    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;
    
    public void addItem(CartItem item) {
        items.add(item);
        item.setCart(this);
    }
    
    public void removeItem(CartItem item) {
        items.remove(item);
        item.setCart(null);
    }
}
""")

with open(os.path.join(domain_dir, "CartItem.java"), "w") as f:
    f.write("""package com.foodapp.domain;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "cart_items", uniqueConstraints = {
    @UniqueConstraint(name = "uk_cart_item", columnNames = {"cart_id", "menu_item_id"})
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CartItem {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "cart_id", nullable = false)
    private Cart cart;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "menu_item_id", nullable = false)
    private MenuItem menuItem;

    @Column(nullable = false, columnDefinition = "INT CHECK (quantity BETWEEN 1 AND 20)")
    private Integer quantity;
}
""")

with open(os.path.join(domain_dir, "Order.java"), "w") as f:
    f.write("""package com.foodapp.domain;

import com.foodapp.domain.enums.OrderStatus;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "orders", indexes = {
    @Index(name = "idx_orders_customer", columnList = "customer_id"),
    @Index(name = "idx_orders_restaurant_status", columnList = "restaurant_id, status, placed_at DESC")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "order_number", length = 20, nullable = false, unique = true)
    private String orderNumber;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "customer_id", nullable = false)
    private User customer;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "restaurant_id", nullable = false)
    private Restaurant restaurant;

    @Enumerated(EnumType.STRING)
    @Column(length = 30, nullable = false)
    private OrderStatus status;

    @Column(nullable = false, columnDefinition = "DECIMAL(10,2)")
    private BigDecimal subtotal;

    @Column(name = "delivery_fee", nullable = false, columnDefinition = "DECIMAL(10,2)")
    private BigDecimal deliveryFee;

    @Column(name = "total_amount", nullable = false, columnDefinition = "DECIMAL(10,2)")
    private BigDecimal totalAmount;

    @Column(name = "delivery_address", length = 300, nullable = false)
    private String deliveryAddress;

    @Column(name = "customer_note", length = 500)
    private String customerNote;

    @Column(name = "rejection_reason", length = 300)
    private String rejectionReason;

    @Column(name = "idempotency_key", length = 64, unique = true)
    private String idempotencyKey;

    @Version
    @Column(nullable = false)
    private Long version = 0L;

    @CreationTimestamp
    @Column(name = "placed_at", nullable = false, updatable = false)
    private LocalDateTime placedAt;

    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<OrderItem> items = new ArrayList<>();

    public void addItem(OrderItem item) {
        items.add(item);
        item.setOrder(this);
    }
}
""")

with open(os.path.join(domain_dir, "OrderItem.java"), "w") as f:
    f.write("""package com.foodapp.domain;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;

@Entity
@Table(name = "order_items")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OrderItem {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id", nullable = false)
    private Order order;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "menu_item_id", nullable = false)
    private MenuItem menuItem;

    @Column(name = "item_name", length = 150, nullable = false)
    private String itemName;

    @Column(name = "unit_price", nullable = false, columnDefinition = "DECIMAL(10,2)")
    private BigDecimal unitPrice;

    @Column(nullable = false)
    private Integer quantity;

    @Column(name = "line_total", nullable = false, columnDefinition = "DECIMAL(10,2)")
    private BigDecimal lineTotal;
}
""")

with open(os.path.join(domain_dir, "OrderStatusHistory.java"), "w") as f:
    f.write("""package com.foodapp.domain;

import com.foodapp.domain.enums.OrderStatus;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import java.time.LocalDateTime;

@Entity
@Table(name = "order_status_history", indexes = {
    @Index(name = "idx_status_hist_order", columnList = "order_id")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OrderStatusHistory {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id", nullable = false)
    private Order order;

    @Enumerated(EnumType.STRING)
    @Column(length = 30, nullable = false)
    private OrderStatus status;

    @Column(length = 300)
    private String note;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "changed_by_user_id")
    private User changedByUser;

    @CreationTimestamp
    @Column(name = "changed_at", nullable = false, updatable = false)
    private LocalDateTime changedAt;
}
""")

# Repositories
with open(os.path.join(repo_dir, "UserRepository.java"), "w") as f:
    f.write("""package com.foodapp.repository;

import com.foodapp.domain.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);
    boolean existsByEmail(String email);
}
""")

with open(os.path.join(repo_dir, "RestaurantRepository.java"), "w") as f:
    f.write("""package com.foodapp.repository;

import com.foodapp.domain.Restaurant;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.util.List;
import java.util.Optional;

public interface RestaurantRepository extends JpaRepository<Restaurant, Long> {
    List<Restaurant> findByIsOpenTrue();
    Optional<Restaurant> findByOwnerId(Long ownerId);
    
    @Query("SELECT r FROM Restaurant r WHERE " +
           "(:cuisine IS NULL OR :cuisine = '' OR r.cuisineType = :cuisine) AND " +
           "(:name IS NULL OR :name = '' OR LOWER(r.name) LIKE LOWER(CONCAT('%', :name, '%'))) AND " +
           "(:openOnly = false OR r.isOpen = true)")
    List<Restaurant> search(@Param("name") String name, @Param("cuisine") String cuisine, @Param("openOnly") boolean openOnly);
    
    @Query("SELECT DISTINCT r.cuisineType FROM Restaurant r ORDER BY r.cuisineType")
    List<String> findDistinctCuisines();
}
""")

with open(os.path.join(repo_dir, "MenuItemRepository.java"), "w") as f:
    f.write("""package com.foodapp.repository;

import com.foodapp.domain.MenuItem;
import jakarta.persistence.LockModeType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.util.List;

public interface MenuItemRepository extends JpaRepository<MenuItem, Long> {
    List<MenuItem> findByRestaurantIdAndIsDeletedFalse(Long restaurantId);
    List<MenuItem> findAllByIdInAndIsDeletedFalse(List<Long> ids);
    
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select m from MenuItem m where m.id in :ids and m.isDeleted = false")
    List<MenuItem> lockAllByIds(@Param("ids") List<Long> ids);
}
""")

with open(os.path.join(repo_dir, "CartRepository.java"), "w") as f:
    f.write("""package com.foodapp.repository;

import com.foodapp.domain.Cart;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface CartRepository extends JpaRepository<Cart, Long> {
    @EntityGraph(attributePaths = {"items", "items.menuItem"})
    Optional<Cart> findByUserId(Long userId);
}
""")

with open(os.path.join(repo_dir, "CartItemRepository.java"), "w") as f:
    f.write("""package com.foodapp.repository;

import com.foodapp.domain.CartItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.util.Optional;

public interface CartItemRepository extends JpaRepository<CartItem, Long> {
    Optional<CartItem> findByCartIdAndMenuItemId(Long cartId, Long menuItemId);
    
    @Modifying
    @Query("DELETE FROM CartItem c WHERE c.cart.id = :cartId")
    void deleteByCartId(@Param("cartId") Long cartId);
}
""")

with open(os.path.join(repo_dir, "OrderRepository.java"), "w") as f:
    f.write("""package com.foodapp.repository;

import com.foodapp.domain.Order;
import com.foodapp.domain.enums.OrderStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface OrderRepository extends JpaRepository<Order, Long> {
    Optional<Order> findByOrderNumber(String orderNumber);
    Page<Order> findByCustomerIdOrderByPlacedAtDesc(Long customerId, Pageable pageable);
    Page<Order> findByRestaurantIdAndStatus(Long restaurantId, OrderStatus status, Pageable pageable);
    Page<Order> findByRestaurantId(Long restaurantId, Pageable pageable);
    
    Optional<Order> findByIdempotencyKey(String idempotencyKey);
    
    @EntityGraph(attributePaths = {"items", "customer", "restaurant"})
    Optional<Order> findWithItemsById(Long id);
}
""")

with open(os.path.join(repo_dir, "OrderStatusHistoryRepository.java"), "w") as f:
    f.write("""package com.foodapp.repository;

import com.foodapp.domain.OrderStatusHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface OrderStatusHistoryRepository extends JpaRepository<OrderStatusHistory, Long> {
    List<OrderStatusHistory> findByOrderIdOrderByChangedAtAsc(Long orderId);
}
""")

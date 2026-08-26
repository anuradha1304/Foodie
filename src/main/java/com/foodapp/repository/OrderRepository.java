package com.foodapp.repository;

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

    Page<Order> findByRestaurantIdOrderByPlacedAtDesc(Long restaurantId, Pageable pageable);
    Page<Order> findByRestaurantIdAndStatusOrderByPlacedAtDesc(Long restaurantId, OrderStatus status, Pageable pageable);
}

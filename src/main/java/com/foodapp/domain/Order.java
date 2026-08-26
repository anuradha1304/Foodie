package com.foodapp.domain;

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

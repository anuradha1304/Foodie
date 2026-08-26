package com.foodapp.domain;

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

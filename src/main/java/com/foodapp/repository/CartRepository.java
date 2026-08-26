package com.foodapp.repository;

import com.foodapp.domain.Cart;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface CartRepository extends JpaRepository<Cart, Long> {
    @EntityGraph(attributePaths = {"items", "items.menuItem"})
    Optional<Cart> findByUserId(Long userId);
}

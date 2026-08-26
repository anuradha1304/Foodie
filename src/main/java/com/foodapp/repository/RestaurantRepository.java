package com.foodapp.repository;

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

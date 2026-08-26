package com.foodapp.repository;

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

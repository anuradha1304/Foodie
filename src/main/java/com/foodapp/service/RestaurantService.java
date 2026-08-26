package com.foodapp.service;

import com.foodapp.domain.MenuItem;
import com.foodapp.domain.Restaurant;
import com.foodapp.dto.response.*;
import com.foodapp.exception.NotFoundException;
import com.foodapp.repository.MenuItemRepository;
import com.foodapp.repository.RestaurantRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@Transactional(readOnly = true)
public class RestaurantService {

    private final RestaurantRepository restaurantRepository;
    private final MenuItemRepository menuItemRepository;

    public RestaurantService(RestaurantRepository restaurantRepository, MenuItemRepository menuItemRepository) {
        this.restaurantRepository = restaurantRepository;
        this.menuItemRepository = menuItemRepository;
    }

    public List<RestaurantSummary> searchRestaurants(String name, String cuisine, boolean openOnly) {
        return restaurantRepository.search(name, cuisine, openOnly).stream()
                .map(r -> new RestaurantSummary(
                        r.getId(),
                        r.getName(),
                        r.getCuisineType(),
                        r.getDescription(),
                        r.getImageUrl(),
                        r.isOpen(),
                        menuItemRepository.findByRestaurantIdAndIsDeletedFalse(r.getId()).size()
                ))
                .toList();
    }

    public RestaurantDetail getRestaurantDetails(Long id) {
        Restaurant r = restaurantRepository.findById(id)
                .orElseThrow(() -> new NotFoundException("Restaurant not found"));
        return new RestaurantDetail(
                r.getId(),
                r.getName(),
                r.getCuisineType(),
                r.getAddress(),
                r.getPhone(),
                r.getImageUrl(),
                r.isOpen()
        );
    }

    public RestaurantMenuResponse getRestaurantMenu(Long id) {
        Restaurant r = restaurantRepository.findById(id)
                .orElseThrow(() -> new NotFoundException("Restaurant not found"));
        
        List<MenuItem> items = menuItemRepository.findByRestaurantIdAndIsDeletedFalse(id);
        
        Map<String, List<MenuItemResponse>> grouped = items.stream()
                .collect(Collectors.groupingBy(
                        MenuItem::getCategory,
                        Collectors.mapping(item -> new MenuItemResponse(
                                item.getId(),
                                item.getName(),
                                item.getDescription(),
                                item.getPrice(),
                                item.getImageUrl(),
                                item.isAvailable()
                        ), Collectors.toList())
                ));
        
        List<MenuCategoryResponse> categories = grouped.entrySet().stream()
                .map(e -> new MenuCategoryResponse(e.getKey(), e.getValue()))
                .toList();
                
        return new RestaurantMenuResponse(r.getId(), r.getName(), r.isOpen(), categories);
    }

    public List<String> getCuisines() {
        return restaurantRepository.findDistinctCuisines();
    }
}

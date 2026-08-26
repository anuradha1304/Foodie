package com.foodapp.service;

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

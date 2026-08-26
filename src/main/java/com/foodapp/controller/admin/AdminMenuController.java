package com.foodapp.controller.admin;

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

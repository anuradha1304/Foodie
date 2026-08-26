package com.foodapp.controller;

import com.foodapp.dto.response.RestaurantDetail;
import com.foodapp.dto.response.RestaurantMenuResponse;
import com.foodapp.dto.response.RestaurantSummary;
import com.foodapp.service.RestaurantService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/restaurants")
public class RestaurantController {

    private final RestaurantService restaurantService;

    public RestaurantController(RestaurantService restaurantService) {
        this.restaurantService = restaurantService;
    }

    @GetMapping
    public List<RestaurantSummary> search(
            @RequestParam(required = false, defaultValue = "") String search,
            @RequestParam(required = false, defaultValue = "") String cuisine,
            @RequestParam(required = false, defaultValue = "false") boolean openOnly) {
        return restaurantService.searchRestaurants(search, cuisine, openOnly);
    }

    @GetMapping("/{id}")
    public RestaurantDetail getDetails(@PathVariable Long id) {
        return restaurantService.getRestaurantDetails(id);
    }

    @GetMapping("/{id}/menu")
    public RestaurantMenuResponse getMenu(@PathVariable Long id) {
        return restaurantService.getRestaurantMenu(id);
    }

    @GetMapping("/cuisines")
    public List<String> getCuisines() {
        return restaurantService.getCuisines();
    }
}

import os

base_dir = "d:/Downloads/files/src/main/java/com/foodapp"
dto_dir = os.path.join(base_dir, "dto", "response")
service_dir = os.path.join(base_dir, "service")
controller_dir = os.path.join(base_dir, "controller")
test_dir = "d:/Downloads/files/src/test/java/com/foodapp/controller"

os.makedirs(dto_dir, exist_ok=True)

# DTOs
with open(os.path.join(dto_dir, "RestaurantSummary.java"), "w") as f:
    f.write("""package com.foodapp.dto.response;
public record RestaurantSummary(
    Long id,
    String name,
    String cuisineType,
    String description,
    String imageUrl,
    boolean isOpen,
    int itemCount
) {}
""")

with open(os.path.join(dto_dir, "RestaurantDetail.java"), "w") as f:
    f.write("""package com.foodapp.dto.response;
public record RestaurantDetail(
    Long id,
    String name,
    String cuisineType,
    String address,
    String phone,
    String imageUrl,
    boolean isOpen
) {}
""")

with open(os.path.join(dto_dir, "MenuItemResponse.java"), "w") as f:
    f.write("""package com.foodapp.dto.response;
import java.math.BigDecimal;
public record MenuItemResponse(
    Long id,
    String name,
    String description,
    BigDecimal price,
    String imageUrl,
    boolean isAvailable
) {}
""")

with open(os.path.join(dto_dir, "MenuCategoryResponse.java"), "w") as f:
    f.write("""package com.foodapp.dto.response;
import java.util.List;
public record MenuCategoryResponse(
    String category,
    List<MenuItemResponse> items
) {}
""")

with open(os.path.join(dto_dir, "RestaurantMenuResponse.java"), "w") as f:
    f.write("""package com.foodapp.dto.response;
import java.util.List;
public record RestaurantMenuResponse(
    Long restaurantId,
    String restaurantName,
    boolean isOpen,
    List<MenuCategoryResponse> categories
) {}
""")

# Service
with open(os.path.join(service_dir, "RestaurantService.java"), "w") as f:
    f.write("""package com.foodapp.service;

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
""")

# Controller
with open(os.path.join(controller_dir, "RestaurantController.java"), "w") as f:
    f.write("""package com.foodapp.controller;

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
""")

# Test
with open(os.path.join(test_dir, "RestaurantControllerTest.java"), "w") as f:
    f.write("""package com.foodapp.controller;

import com.foodapp.domain.MenuItem;
import com.foodapp.domain.Restaurant;
import com.foodapp.domain.User;
import com.foodapp.domain.enums.Role;
import com.foodapp.repository.MenuItemRepository;
import com.foodapp.repository.RestaurantRepository;
import com.foodapp.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;

import static org.hamcrest.Matchers.hasSize;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest(properties = {
    "spring.datasource.url=jdbc:h2:mem:testdb-m3;MODE=MySQL;DB_CLOSE_DELAY=-1",
    "spring.datasource.driverClassName=org.h2.Driver",
    "spring.datasource.username=sa",
    "spring.datasource.password=",
    "spring.jpa.database-platform=org.hibernate.dialect.H2Dialect",
    "spring.jpa.hibernate.ddl-auto=create-drop",
    "spring.sql.init.mode=never"
})
@AutoConfigureMockMvc
public class RestaurantControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private RestaurantRepository restaurantRepository;

    @Autowired
    private MenuItemRepository menuItemRepository;

    @BeforeEach
    public void setup() {
        menuItemRepository.deleteAll();
        restaurantRepository.deleteAll();
        userRepository.deleteAll();

        User owner = userRepository.save(User.builder().fullName("Owner").email("owner@x.com").passwordHash("hash").phone("123").role(Role.RESTAURANT_ADMIN).enabled(true).build());
        
        Restaurant r = restaurantRepository.save(Restaurant.builder()
                .name("Test Rest")
                .cuisineType("Italian")
                .address("123 Street")
                .phone("12345")
                .isOpen(true)
                .owner(owner)
                .build());

        menuItemRepository.save(MenuItem.builder().restaurant(r).name("Pizza").category("Mains").price(new BigDecimal("10.00")).isAvailable(true).isDeleted(false).build());
        menuItemRepository.save(MenuItem.builder().restaurant(r).name("Pasta").category("Mains").price(new BigDecimal("12.00")).isAvailable(false).isDeleted(false).build());
        menuItemRepository.save(MenuItem.builder().restaurant(r).name("Coke").category("Drinks").price(new BigDecimal("2.00")).isAvailable(true).isDeleted(false).build());
        menuItemRepository.save(MenuItem.builder().restaurant(r).name("Deleted").category("Mains").price(new BigDecimal("1.00")).isAvailable(true).isDeleted(true).build());
    }

    @Test
    public void getMenuGroupsCorrectlyAndExcludesDeleted() throws Exception {
        Long rId = restaurantRepository.findAll().get(0).getId();
        
        mockMvc.perform(get("/api/restaurants/" + rId + "/menu"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.restaurantName").value("Test Rest"))
                .andExpect(jsonPath("$.categories", hasSize(2))) // Mains, Drinks
                .andExpect(jsonPath("$.categories[?(@.category == 'Mains')].items[0]", hasSize(2))) // Pizza, Pasta. Deleted is excluded.
                .andExpect(jsonPath("$.categories[?(@.category == 'Mains')].items[0][?(@.name == 'Pasta')].isAvailable").value(false)); // Unavailable included
    }

    @Test
    public void searchRestaurants() throws Exception {
        mockMvc.perform(get("/api/restaurants?search=Test&cuisine=Italian"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].name").value("Test Rest"))
                .andExpect(jsonPath("$[0].itemCount").value(3)); // 3 active items (Pizza, Pasta, Coke)
    }
}
""")

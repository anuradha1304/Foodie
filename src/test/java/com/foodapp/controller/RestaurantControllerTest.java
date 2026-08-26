package com.foodapp.controller;

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
                .andDo(org.springframework.test.web.servlet.result.MockMvcResultHandlers.print())
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.restaurantName").value("Test Rest"))
                .andExpect(jsonPath("$.categories[?(@.category == 'Mains')].items[0]", org.hamcrest.Matchers.notNullValue()))
                .andExpect(jsonPath("$.categories[?(@.category == 'Mains')].items[0].name").value("Pizza"))
                .andExpect(jsonPath("$.categories[?(@.category == 'Mains')].items[1].name").value("Pasta"))
                .andExpect(jsonPath("$.categories[?(@.category == 'Mains')].items[1].isAvailable").value(false));
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

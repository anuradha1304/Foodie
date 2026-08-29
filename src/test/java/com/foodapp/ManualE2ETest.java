package com.foodapp;

import com.foodapp.domain.MenuItem;
import com.foodapp.domain.Restaurant;
import com.foodapp.domain.User;
import com.foodapp.domain.enums.Role;
import com.foodapp.repository.MenuItemRepository;
import com.foodapp.repository.RestaurantRepository;
import com.foodapp.repository.UserRepository;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.math.BigDecimal;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.DEFINED_PORT, properties = {
    "server.port=8080",
    "spring.datasource.url=jdbc:h2:mem:testdb;MODE=MySQL;DB_CLOSE_DELAY=-1",
    "spring.datasource.driverClassName=org.h2.Driver",
    "spring.datasource.username=sa",
    "spring.datasource.password=",
    "spring.jpa.database-platform=org.hibernate.dialect.H2Dialect",
    "spring.jpa.hibernate.ddl-auto=create-drop"
})
public class ManualE2ETest {

    @Autowired private UserRepository userRepository;
    @Autowired private RestaurantRepository restaurantRepository;
    @Autowired private MenuItemRepository menuItemRepository;

    @Test
    @Disabled("Run manually for E2E testing")
    public void runServer() throws InterruptedException {
        // Seed users
        User admin1 = userRepository.save(User.builder().fullName("Admin One").email("admin1@foodapp.com").passwordHash("$2b$12$4GJ6BzP644JHkNdqNH2IOOvtKgmjlC0NgimGJCsHvPVk6QeJLpXcS").phone("111").role(Role.RESTAURANT_ADMIN).enabled(true).build());
        User admin2 = userRepository.save(User.builder().fullName("Admin Two").email("admin2@foodapp.com").passwordHash("$2b$12$4GJ6BzP644JHkNdqNH2IOOvtKgmjlC0NgimGJCsHvPVk6QeJLpXcS").phone("222").role(Role.RESTAURANT_ADMIN).enabled(true).build());
        User cust = userRepository.save(User.builder().fullName("Test Customer").email("customer@foodapp.com").passwordHash("$2b$12$4GJ6BzP644JHkNdqNH2IOOvtKgmjlC0NgimGJCsHvPVk6QeJLpXcS").phone("333").role(Role.CUSTOMER).enabled(true).build());

        // Seed restaurants
        Restaurant r1 = restaurantRepository.save(Restaurant.builder().name("Spice Route").cuisineType("North Indian").address("123 Curry Ln").phone("111").isOpen(true).owner(admin1).build());
        Restaurant r2 = restaurantRepository.save(Restaurant.builder().name("Bella Italia").cuisineType("Italian").address("456 Pizza St").phone("222").isOpen(true).owner(admin2).build());

        // Seed menu items
        menuItemRepository.save(MenuItem.builder().restaurant(r1).name("Paneer Tikka").category("Starters").price(new BigDecimal("250.00")).isAvailable(true).isDeleted(false).build());
        menuItemRepository.save(MenuItem.builder().restaurant(r1).name("Chicken Samosa").category("Starters").price(new BigDecimal("150.00")).isAvailable(true).isDeleted(false).build());
        menuItemRepository.save(MenuItem.builder().restaurant(r1).name("Butter Chicken").category("Main Course").price(new BigDecimal("450.00")).isAvailable(true).isDeleted(false).build());
        menuItemRepository.save(MenuItem.builder().restaurant(r1).name("Dal Makhani").category("Main Course").price(new BigDecimal("300.00")).isAvailable(false).isDeleted(false).build());
        
        menuItemRepository.save(MenuItem.builder().restaurant(r2).name("Garlic Bread").category("Starters").price(new BigDecimal("180.00")).isAvailable(true).isDeleted(false).build());
        menuItemRepository.save(MenuItem.builder().restaurant(r2).name("Margherita Pizza").category("Main Course").price(new BigDecimal("499.00")).isAvailable(true).isDeleted(false).build());

        System.out.println("SERVER RUNNING ON http://localhost:8080");
        System.out.println("Customer login: customer@foodapp.com / Password123");
        
        // Block thread to keep server alive
        Thread.sleep(Long.MAX_VALUE);
    }
}

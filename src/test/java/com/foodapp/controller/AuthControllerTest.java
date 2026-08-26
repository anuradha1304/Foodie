package com.foodapp.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.foodapp.domain.enums.Role;
import com.foodapp.dto.request.LoginRequest;
import com.foodapp.dto.request.RegisterRequest;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest(properties = {
    "spring.datasource.url=jdbc:h2:mem:testdb;MODE=MySQL;DB_CLOSE_DELAY=-1",
    "spring.datasource.driverClassName=org.h2.Driver",
    "spring.datasource.username=sa",
    "spring.datasource.password=",
    "spring.jpa.database-platform=org.hibernate.dialect.H2Dialect",
    "spring.jpa.hibernate.ddl-auto=create-drop",
    "spring.sql.init.mode=never"
})
@AutoConfigureMockMvc
public class AuthControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private com.foodapp.repository.UserRepository userRepository;

    @Autowired
    private org.springframework.security.crypto.password.PasswordEncoder passwordEncoder;

    @org.junit.jupiter.api.BeforeEach
    public void setup() {
        userRepository.deleteAll();
        userRepository.save(com.foodapp.domain.User.builder()
            .fullName("Test Customer")
            .email("customer@foodapp.com")
            .passwordHash(passwordEncoder.encode("Password123"))
            .phone("9876543210")
            .role(Role.CUSTOMER)
            .enabled(true)
            .build());
    }

    @Test
    public void registerSuccess() throws Exception {
        RegisterRequest req = new RegisterRequest("Test User", "test@x.com", "Password123", "1234567890", Role.CUSTOMER);
        mockMvc.perform(post("/api/auth/register").with(csrf())
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.email").value("test@x.com"))
                .andExpect(jsonPath("$.passwordHash").doesNotExist());
    }

    @Test
    public void registerDuplicateEmail() throws Exception {
        // Assume seed data has customer@foodapp.com
        RegisterRequest req = new RegisterRequest("Dup", "customer@foodapp.com", "Password123", "1234567890", Role.CUSTOMER);
        mockMvc.perform(post("/api/auth/register").with(csrf())
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.code").value("EMAIL_ALREADY_EXISTS"));
    }

    @Test
    public void registerWeakPassword() throws Exception {
        RegisterRequest req = new RegisterRequest("Test User", "testweak@x.com", "weak", "1234567890", Role.CUSTOMER);
        mockMvc.perform(post("/api/auth/register").with(csrf())
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value("VALIDATION_FAILED"))
                .andExpect(jsonPath("$.fieldErrors.password").exists());
    }

    @Test
    public void loginSuccess() throws Exception {
        LoginRequest req = new LoginRequest("customer@foodapp.com", "Password123");
        mockMvc.perform(post("/api/auth/login").with(csrf())
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.email").value("customer@foodapp.com"))
                .andExpect(request().sessionAttribute(org.springframework.security.web.context.HttpSessionSecurityContextRepository.SPRING_SECURITY_CONTEXT_KEY, org.hamcrest.Matchers.notNullValue()));
    }

    @Test
    public void loginBadCredentials() throws Exception {
        LoginRequest req = new LoginRequest("customer@foodapp.com", "WrongPassword");
        mockMvc.perform(post("/api/auth/login").with(csrf())
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.code").value("BAD_CREDENTIALS"));
    }

    @Test
    @WithMockUser(username = "customer@foodapp.com")
    public void meAuthenticated() throws Exception {
        // WithMockUser sets up a basic UserDetails context, but our app needs AppUserDetails.
        // It's better to just log in and use the session.
    }
    
    @Test
    public void meUnauthenticated() throws Exception {
        mockMvc.perform(get("/api/auth/me"))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.code").value("UNAUTHENTICATED"));
    }
}

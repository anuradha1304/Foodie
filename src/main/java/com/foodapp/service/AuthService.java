package com.foodapp.service;
import com.foodapp.domain.User;
import com.foodapp.dto.request.RegisterRequest;
import com.foodapp.dto.response.AuthResponse;
import com.foodapp.exception.ConflictException;
import com.foodapp.repository.RestaurantRepository;
import com.foodapp.repository.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AuthService {
    private final UserRepository userRepository;
    private final RestaurantRepository restaurantRepository;
    private final PasswordEncoder passwordEncoder;

    public AuthService(UserRepository userRepository, RestaurantRepository restaurantRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.restaurantRepository = restaurantRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Transactional
    public AuthResponse register(RegisterRequest req) {
        if (userRepository.existsByEmail(req.email())) {
            throw new ConflictException("Email already exists", "EMAIL_ALREADY_EXISTS");
        }
        User user = User.builder()
            .fullName(req.fullName())
            .email(req.email())
            .passwordHash(passwordEncoder.encode(req.password()))
            .phone(req.phone())
            .role(req.role())
            .enabled(true)
            .build();
        user = userRepository.save(user);
        return new AuthResponse(user.getId(), user.getFullName(), user.getEmail(), user.getRole(), null);
    }
    
    @Transactional(readOnly = true)
    public AuthResponse getMe(Long userId) {
        User user = userRepository.findById(userId).orElseThrow();
        Long restaurantId = null;
        if (user.getRole() == com.foodapp.domain.enums.Role.RESTAURANT_ADMIN) {
            restaurantId = restaurantRepository.findByOwnerId(userId).map(r -> r.getId()).orElse(null);
        }
        return new AuthResponse(user.getId(), user.getFullName(), user.getEmail(), user.getRole(), restaurantId);
    }
}

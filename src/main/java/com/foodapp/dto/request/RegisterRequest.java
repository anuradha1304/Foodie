package com.foodapp.dto.request;
import com.foodapp.domain.enums.Role;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

public record RegisterRequest(
    @NotBlank @Size(min = 2, max = 120) String fullName,
    @NotBlank @Email @Size(max = 180) String email,
    @NotBlank @Size(min = 8, max = 100) @Pattern(regexp = "^(?=.*[0-9])(?=.*[a-zA-Z]).{8,}$", message = "must contain at least one letter and one digit") String password,
    @NotBlank @Pattern(regexp = "^\\d{10}$", message = "must be 10 digits") String phone,
    @NotNull Role role
) {}

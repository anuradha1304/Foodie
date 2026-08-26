package com.foodapp;

import org.junit.jupiter.api.Test;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

public class HashGenTest {
    @Test
    public void printHash() {
        System.out.println("BCRYPT_HASH=" + new BCryptPasswordEncoder().encode("Password123"));
    }
}

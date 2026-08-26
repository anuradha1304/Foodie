package com.foodapp.security;
import com.foodapp.exception.ForbiddenException;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;

public class SecurityUtils {
    public static Long currentUserId() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !auth.isAuthenticated() || "anonymousUser".equals(auth.getPrincipal())) {
            throw new ForbiddenException("Not authenticated");
        }
        AppUserDetails details = (AppUserDetails) auth.getPrincipal();
        return details.getId();
    }
}

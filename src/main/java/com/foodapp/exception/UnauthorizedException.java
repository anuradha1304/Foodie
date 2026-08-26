package com.foodapp.exception;

public class UnauthorizedException extends ApiException {
    public UnauthorizedException(String message, String code) {
        super(message, code);
    }
}

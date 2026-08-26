package com.foodapp.exception;
public class ForbiddenException extends ApiException {
    public ForbiddenException(String message) { super(message, "FORBIDDEN"); }
}

package com.foodapp.exception;
public class ConflictException extends ApiException {
    public ConflictException(String message, String code) { super(message, code); }
}

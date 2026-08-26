package com.foodapp.exception;
import lombok.Getter;
@Getter
public abstract class ApiException extends RuntimeException {
    private final String code;
    public ApiException(String message, String code) { super(message); this.code = code; }
}

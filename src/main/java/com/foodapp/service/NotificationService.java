package com.foodapp.service;

import com.foodapp.event.OrderPlacedEvent;
import com.foodapp.event.OrderStatusChangedEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.event.TransactionPhase;
import org.springframework.transaction.event.TransactionalEventListener;

@Service
public class NotificationService {
    
    private static final Logger log = LoggerFactory.getLogger(NotificationService.class);

    @Async("taskExecutor")
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void handleOrderPlaced(OrderPlacedEvent event) {
        log.info("Async Notification: Sending order confirmation for order {} to {}", 
                 event.order().getOrderNumber(), event.order().getCustomer().getEmail());
        // Simulate email sending delay
        try { Thread.sleep(500); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
    }

    @Async("taskExecutor")
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void handleOrderStatusChanged(OrderStatusChangedEvent event) {
        log.info("Async Notification: Order {} status changed from {} to {}. Notifying {}", 
                 event.order().getOrderNumber(), event.oldStatus(), event.newStatus(), 
                 event.order().getCustomer().getEmail());
        // Simulate email sending delay
        try { Thread.sleep(500); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
    }
}

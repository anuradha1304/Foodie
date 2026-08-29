package com.foodapp;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;

import java.util.List;
import java.util.Map;

import org.junit.jupiter.api.Disabled;

@SpringBootTest(properties = {
    "spring.datasource.url=jdbc:h2:mem:food_ordering_dev;MODE=MySQL;DB_CLOSE_DELAY=-1",
    "spring.datasource.username=sa",
    "spring.datasource.password=",
    "spring.datasource.driver-class-name=org.h2.Driver",
    "spring.jpa.hibernate.ddl-auto=update",
    "spring.sql.init.mode=never"
})
@Disabled("Requires true MySQL to inspect INFORMATION_SCHEMA.COLUMNS.COLUMN_TYPE")
public class SchemaVerificationTest {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Test
    public void printSchema() {
        String sql = "SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY " +
                     "FROM INFORMATION_SCHEMA.COLUMNS " +
                     "WHERE TABLE_SCHEMA = 'food_ordering_dev' " +
                     "ORDER BY TABLE_NAME, ORDINAL_POSITION";
        
        List<Map<String, Object>> rows = jdbcTemplate.queryForList(sql);
        System.out.println("--- SCHEMA START ---");
        for (Map<String, Object> row : rows) {
            System.out.println(String.format("%s | %s | %s | %s | %s",
                row.get("TABLE_NAME"),
                row.get("COLUMN_NAME"),
                row.get("COLUMN_TYPE"),
                row.get("IS_NULLABLE"),
                row.get("COLUMN_KEY")));
        }
        System.out.println("--- SCHEMA END ---");
    }
}

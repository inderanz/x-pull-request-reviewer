// Test Java file with multiple issues for XPRR testing
// This file contains intentional code quality issues and best practice violations

package com.example;

import java.io.*;
import java.sql.*;
import java.util.*;

// Missing class documentation
public class Application {
    
    // Security issue: hardcoded credentials
    private static final String DB_PASSWORD = "admin123";
    private static final String API_KEY = "secret_key_123";
    
    // Code quality issue: magic number
    private static final int TIMEOUT = 30;
    
    // Code quality issue: missing access modifier
    String unprotectedField = "this should be private";
    
    // Code quality issue: inconsistent formatting
    public void methodWithBadFormatting(){
        if(true){
            System.out.println("bad formatting");
        }
    }
    
    // Security issue: SQL injection vulnerability
    public void vulnerableMethod(String userInput) {
        String query = "SELECT * FROM users WHERE id = " + userInput;
        // Missing proper parameterization
    }
    
    // Code quality issue: missing documentation
    public void undocumentedMethod() {
        // Missing JavaDoc
    }
    
    // Code quality issue: long line
    public void methodWithVeryLongLineThatExceedsTheMaximumLineLengthAndShouldBeReportedByCheckstyle() {
        System.out.println("This is a very long line that should be reported by the static analysis tools");
    }
    
    // Code quality issue: unused variable
    public void unusedVariableMethod() {
        String unusedVar = "this is unused";
        System.out.println("Hello World");
    }
    
    // Code quality issue: missing error handling
    public void methodWithoutErrorHandling() {
        File file = new File("nonexistent.txt");
        file.delete();
    }
} 
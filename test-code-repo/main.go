// Test Go file with multiple issues for XPRR testing
// This file contains intentional code quality issues and security vulnerabilities

package main

import (
	"fmt"
	"os"
	"os/exec"
)

// Missing package comment
// Missing function documentation

func main() {
	// Security issue: command injection
	cmd := exec.Command("ls", "-la")
	output, err := cmd.Output()
	if err != nil {
		fmt.Println(err)
	}
	fmt.Println(string(output))

	// Security issue: hardcoded credentials
	password := "secret123"
	fmt.Println("Password:", password)

	// Code quality issue: unused variable
	unusedVar := "this is unused"

	// Code quality issue: magic number
	timeout := 30

	// Code quality issue: long line
	veryLongVariableNameThatExceedsTheMaximumLineLengthAndShouldBeReportedByGolint := "this is a very long string that makes the line too long"
	fmt.Println(veryLongVariableNameThatExceedsTheMaximumLineLengthAndShouldBeReportedByGolint)

	// Code quality issue: missing error handling
	os.Remove("temp.txt")

	// Code quality issue: inconsistent formatting
	if timeout > 20 {
		fmt.Println("timeout is high")
	}
}

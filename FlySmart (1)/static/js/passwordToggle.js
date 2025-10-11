document.addEventListener("DOMContentLoaded", function () {
    const passwordInput = document.getElementById("password");
    const confirmPasswordInput = document.getElementById("confirm-password");
    const togglePassword = document.getElementById("togglePassword");
    const toggleConfirmPassword = document.getElementById("toggleConfirmPassword");
    const passwordError = document.getElementById("password-error");
    const confirmPasswordError = document.getElementById("confirm-password-error");
    const registerForm = document.querySelector("form");
    const registerButton = document.getElementById("register-btn");

    // Regular expression for strong password (8+ chars, 1 uppercase, 1 number, 1 special character)
    const passwordRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

    // Toggle Password Visibility Function
    function toggleVisibility(input, icon) {
        if (input.type === "password") {
            input.type = "text";
            icon.innerHTML = '<i class="fa fa-eye-slash"></i>';
        } else {
            input.type = "password";
            icon.innerHTML = '<i class="fa fa-eye"></i>';
        }
    }

    // Event Listener for Password Toggle
    togglePassword.addEventListener("click", function () {
        toggleVisibility(passwordInput, togglePassword);
    });

    toggleConfirmPassword.addEventListener("click", function () {
        toggleVisibility(confirmPasswordInput, toggleConfirmPassword);
    });

    // Validate Password Complexity
    function validatePassword() {
        const passwordValue = passwordInput.value;
        if (!passwordRegex.test(passwordValue)) {
            passwordError.textContent = "Password must be at least 8 characters, include 1 uppercase letter, 1 number, and 1 special character (@$!%*?&).";
            passwordInput.style.border = "2px solid red";
            return false;
        } else {
            passwordError.textContent = "";
            passwordInput.style.border = "2px solid green";
            return true;
        }
    }

    // Validate Confirm Password Match
    function validateConfirmPassword() {
        if (passwordInput.value !== confirmPasswordInput.value) {
            confirmPasswordError.textContent = "Passwords do not match.";
            confirmPasswordInput.style.border = "2px solid red";
            return false;
        } else {
            confirmPasswordError.textContent = "";
            confirmPasswordInput.style.border = "2px solid green";
            return true;
        }
    }

    // Attach Event Listeners
    passwordInput.addEventListener("input", validatePassword);
    confirmPasswordInput.addEventListener("input", validateConfirmPassword);

    // Prevent Form Submission if Validation Fails
    registerForm.addEventListener("submit", function (e) {
        let isPasswordValid = validatePassword();
        let isConfirmPasswordValid = validateConfirmPassword();

        if (!isPasswordValid || !isConfirmPasswordValid) {
            e.preventDefault(); // Stop form from submitting
        }
    });
});

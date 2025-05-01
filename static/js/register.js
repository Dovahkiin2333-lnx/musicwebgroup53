document.addEventListener('DOMContentLoaded', () => {
    const button = document.getElementById('getVerificationCode');
    console.log("hello")
    button.addEventListener('click', async (event) => {
      event.preventDefault();
      const email = document.querySelector("input[name='email']").value;
      
      try {
        const response = await fetch(`/user/auth/captcha/email?email=${encodeURIComponent(email)}`);
        const result = await response.json();
        
        if (result.code === 200) {
          startCountdown(button);
          alert("Verification code sent successfully");
        } else {
          alert(result.message || "Failed to send code");
        }
      } catch (error) {
        console.error("Request failed:", error);
        alert("Network error occurred");
      }
    });
  });
  
  function startCountdown(button) {
    let countdown = 5;
    const originalText = button.textContent;
    button.disabled = true;
    
    const timer = setInterval(() => {
      button.textContent = countdown;
      countdown--;
      
      if (countdown < 0) {
        clearInterval(timer);
        button.textContent = originalText;
        button.disabled = false;
      }
    }, 1000);
  }
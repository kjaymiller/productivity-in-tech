// Create an instance of Elements
var elements = stripe.elements();
// Custom styling can be passed to options when creating an Element.
// (Note that this demo uses a wider set of styles than the guide below.)
var style = {
  base: {
    color: '#3f3f3f',
    lineHeight: '32px',
    fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
    fontSmoothing: 'antialiased',
    fontSize: '20px',
    '::placeholder': {
      color: '#3394FA'
    }
  },
  invalid: {
    color: '#fa755a',
    iconColor: '#fa755a'
  }
};

// Create an instance of the card Element
var card = elements.create('card', {style: style});

// Add an instance of the card Element into the `card-element` <div>
card.mount('#card-element');

// Handle form submission
var button = document.getElementById('payment-button'); 
var form = document.getElementById('payment-form');

var process_payment = function() {
  stripe.createToken(card).then(function(result) {
    if (result.error) {
      // Inform the user if there was an error
      var errorElement = document.getElementById('card-errors');
      errorElement.textContent = result.error.message;
    } else {
      
      // Add token to form
      var token_field = document.createElement('input');
      token_field.type = "hidden";
      token_field.value = result.token.id;
      token_field.name = "token_field";
      document.getElementById("payment-form").appendChild(token_field);

      //Submit Form
      var submit_button = document.createElement('input');
      submit_button.type = "submit";
      submit_button.style = "display: none;"
      document.getElementById('payment-form').appendChild(submit_button
)

      var password = document.getElementsByName('password')[0];
      var confirmPassword = document.getElementsByName('confirm-password')[0]

      if (password.value != confirmPassword.value) {
	password.setCustomValidity('Passwords Do Not Match')
	confirmPassword.classList.add('error-box')
	} else {
	password.setCustomValidity('');
	};

      	submit_button.click();
    }
  });
}


document.getElementById('membership-option').onchange = function() {
  var mentorship = document.getElementById('mentorship');
  var earlyAccess = document.getElementById('early-access');

  if (document.getElementById('membership-option').value == 'community') {
   mentorship.classList.add('greyed');
   earlyAccess.classList.add('greyed');
   console.log('ADD ELEMENT')
   } else {
   mentorship.classList.remove('greyed');
   earlyAccess.classList.remove('greyed');
   console.log('REMOVE ELEMENT')
     };
  };

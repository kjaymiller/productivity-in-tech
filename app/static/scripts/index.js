//Wait 5 seconds and then hide

var counter = $(".friends-items").length;
var iter = 1;

while (iter < counter) {
var friends = ".friends-items:nth-child(" + iter +")";
$(friends).fadeOut(4);
if (iter < counter) {
  iter += 1;
  }
else {
  iter = 1;
  };
$(friends).delay(1000).fadeIn(1000);
};

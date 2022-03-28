
var app = {

   init() {
      alert("app.init")
   }

};


/* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
/* attach page loaded event */
window.addEventListener("DOMContentLoaded", app.init);

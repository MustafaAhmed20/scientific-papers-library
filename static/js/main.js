$(document).ready(function(){
    //Adjust Slider Height
    var winh = $(window).innerHeight(),
    uph  = $('.upper-bar').innerHeight(),
    navh = $('.navbar').innerHeight();
    $('.slider, .carousel-item').height(winh - (uph + navh));
    
});
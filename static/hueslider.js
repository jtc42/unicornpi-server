$(document).ready(function(){
    
    //alert("Script has started!");

    //Define background to change
    var bg = $(".colorDisplay");

    //Get initial slider values
    var hueVal = $("#hueslider").val();
    var lightVal = $("#lightslider").val();

    //Construct initial colour code
    var whatIs = 'hsl(' + hueVal + ',' + '100% ,' + lightVal + '%)';

    //Set initial colour
    bg.css('background-color', whatIs);


    $("#hueslider").change(function() {
        
        //Update slider values
        var hueVal = $("#hueslider").val();
        var lightVal = $("#lightslider").val();

        //Update colour code
        var whatIs = 'hsl(' + hueVal + ',' + '100% ,' + lightVal + '%)';

        //Update colour
        bg.css('background-color', whatIs);
    });

    $("#lightslider").change(function() {
        
        //Update slider values
        var hueVal = $("#hueslider").val();
        var lightVal = $("#lightslider").val();

        //Update colour code
        var whatIs = 'hsl(' + hueVal + ',' + '100% ,' + lightVal + '%)';

        //Update colour
        bg.css('background-color', whatIs);
    });
    
})


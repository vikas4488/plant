
$(document).ready(function(){
    $(".okbtn").click(function(){
      console.log("ok is clicked");
    });
    $(".cancelbtn").click(function(){
        console.log("cancel is clicked");
        $(".popupbody").hide();
      });
  });
$(document).ready(function(){
    $(".l_s_message_cross_text").click(function(){
        $(".l_s_message_wrap").attr('class', 'l_s_message_wrap');
        $(".l_s_message_content").text("");
    });
    $(".l_s_singup").click(function(){
        if(!$(".l_s_singup").hasClass("l_s_singup_toggle")){
            $(".l_s_message_wrap").attr('class', 'l_s_message_wrap');
            $(".l_s_message_content").text("");
            $(".l_s_form_signup").css({display:"block"});
            $(".l_s_form_signin").css({display:"none"});
            $(".l_s_singup").addClass("l_s_singup_toggle");
            $(".l_s_singin").addClass("l_s_singin_toggle");
            $('.clr_signin').val('');
            $('.clr_signup').val('');
        }
    });
    $(".l_s_singin").click(function(){
        if($(".l_s_singin").hasClass("l_s_singin_toggle")){
            $(".l_s_message_wrap").attr('class', 'l_s_message_wrap');
            $(".l_s_message_content").text("");
            $(".l_s_form_signup").css({display:"none"});
            $(".l_s_form_signin").css({display:"block"});
            $(".l_s_singin").removeClass("l_s_singin_toggle");
            $(".l_s_singup").removeClass("l_s_singup_toggle");
            $('.clr_signin').val('');
            $('.clr_signup').val('');
        }
    });

    $('#signin_form_id').submit(function(event) {
        event.preventDefault();
        $(".lbg").show();
        var formData = $(this).serialize();
        $.ajax({
            type: 'POST',
            url: signinurl, // Replace 'your_url_name' with the actual URL name
            data: formData,
            success: function(response) {
                $(".l_s_message_wrap").attr('class', 'l_s_message_wrap');
                $(".l_s_message_wrap").addClass("l_s_should_"+response.message.color_code);
                $(".l_s_message_content").text(response.message.text);
                $('.clr_signin').val('');
                $('.clr_signup').val('');
                $(".lbg").hide();
                
                if(response.message.color_code==="success"){
                    setTimeout(function() {
                        location.reload(true);
                       }, 1000);
                    
                }
            },
            error: function(xhr, status, error) {
                $(".l_s_message_wrap").attr('class', 'l_s_message_wrap');
                $(".l_s_message_wrap").addClass("l_s_should_danger");
                $(".l_s_message_content").text("unknown Error occured please try again");
                $(".lbg").hide();
                console.error(xhr.responseText);
            }
        });
    });

    $(".l_s_form_button_cancel").click(function(){
        $(".l_s_message_wrap").attr('class', 'l_s_message_wrap');
        $(".l_s_message_content").text("");
        $(".l_s_wrap").css({display:"none"});
    });
    $('.l_s_wrap').on('click', function(e) {
        if (e.target !== this)
          return;
        $(".l_s_message_wrap").attr('class', 'l_s_message_wrap');
        $(".l_s_message_content").text("");
        $(".l_s_wrap").css({display:"none"});

      });

      $('#signup_form_id').submit(function(event) {
        event.preventDefault();
        $(".lbg").show();
        var formData = $(this).serialize();
        $.ajax({
            type: 'POST',
            url: signupurl, // Replace 'your_url_name' with the actual URL name
            data: formData,
            success: function(response) {
                $(".l_s_message_wrap").addClass("l_s_should_"+response.message.color_code);
                $(".l_s_message_content").text(response.message.text);
                if(response.message.color_code==="success"){
                    $(".l_s_form_signup").css({display:"none"});
                    $(".l_s_form_signin").css({display:"block"});
                    $(".l_s_singin").removeClass("l_s_singin_toggle");
                    $(".l_s_singup").removeClass("l_s_singup_toggle");
                    $('.clr_signin').val('');
                    $('.clr_signup').val('');
                }
                $(".lbg").hide();
            },
            error: function(xhr, status, error) {
                $(".l_s_message_wrap").attr('class', 'l_s_message_wrap');
                $(".l_s_message_wrap").addClass("l_s_should_danger");
                $(".l_s_message_content").text("unknown Error occured please try again");
                $(".lbg").hide();
                console.error(xhr.responseText);
            }
        });
    });
      

});
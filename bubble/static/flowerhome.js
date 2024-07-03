
$(document).ready(function(){
  if(catss!==""){
    $(".f_h_home_nav_greater_icon").show();
    $(".f_h_home_nav_name_cat").html(catss);
  }
  if(subcatss!==""){
    $(".f_h_home_nav_greater_icon_mid").show();
    $(".f_h_home_nav_name_subcat").html(subcatss);
  }
    $(".f_h_menu_icon").click(function(){
      $(".f_h_side_menu_wrap").css({display:"flex"});
      setTimeout(function() {
        $(".f_h_side_menu_background").css({left:"0"});
       }, 0);
     
    });
    $(document).on("click",".f_h_page_item_single_product_info , .f_h_page_item_single_image,.myo_list_single_image",function(){
      $(this).parent().submit();
    });
function display_l_s(){
  $(".l_s_wrap").css({display:"flex"});
}
function hide_l_s(){
  $(".l_s_wrap").css({display:"none"});
}
    $(".f_h_plc_p_wrp").click(function(){
      display_l_s();
    });
    
    $(".f_h_plc_l_wrp").click(function(){
      console.log(user_authenticated);
      if(user_authenticated==='False')
      display_l_s();
      else
      document.location.href = fav_page_url;
    });
    $(".f_h_plc_c_wrp").click(function(){
      console.log(user_authenticated);
      if(user_authenticated==='False')
      display_l_s();
      else
      document.location.href = cart_page_url;
    });
    $('.f_h_side_menu_wrap').on('click', function(e) {
        if (e.target !== this)
          return;
        $(".f_h_side_menu_background").css({left:"-300px"});
        setTimeout(function() {
            $(".f_h_side_menu_wrap").css({display:"none"});
        }, 300);
      });
      $(".f_h_side_menu_close").click(function(){
        $(".f_h_side_menu_background").css({left:"-300px"});
        setTimeout(function() {
            $(".f_h_side_menu_wrap").css({display:"none"});
        }, 300);
      });
      $('.f_h_side_menu_row_head_icon').on('click', function(e) {
        //alert("hello");
        $(this).parent().parent().find(".f_h_side_menu_row_sub_menu").toggleClass("f_h_side_menu_row_sub_menu_toggle")
      });



      $('.f_h_page_item_single_like').on('click',function() {
        //event.preventDefault();
        $(".lbg").show();
        var formData = $(this).parent().serialize();
        var $this=$(this);
        $.ajax({
            type: 'POST',
            url: fav_form_url, // Replace 'your_url_name' with the actual URL name
            data: formData,
            success: function(response) {
                if(response.message==="liked"){
                  $this.parent().find(".f_h_page_item_single_like").addClass("liked");
                }else if(response.message==="like_removed"){
                  $this.parent().find(".f_h_page_item_single_like").removeClass("liked");
                }else if(response.message==="not_loggedin"){
                  display_l_s();
                }
                //$(".l_s_message_content").text(response.message.text);
                $(".lbg").hide();
                
            },
            error: function(xhr, status, error) {
                
                $(".lbg").hide();
                console.error(xhr.responseText);
            }
        });
    });

    $('.f_h_page_item_single_add_to_cart_wrap').on('click',function() {
      //event.preventDefault();
      $(".lbg").show();
      var formData = $(this).parent().serialize();
      var $this=$(this);
      $.ajax({
          type: 'POST',
          url: cart_form_url, // Replace 'your_url_name' with the actual URL name
          data: formData,
          success: function(response,status) {
              if(response.message==="carted"){
                $this.parent().find(".f_h_page_item_single_add_to_cart_wrap").addClass("carted");
              }else if(response.message==="carted_removed"){
                $this.parent().find(".f_h_page_item_single_add_to_cart_wrap").removeClass("carted");
              }else if(response.message==="not_loggedin"){
                display_l_s();
              }
              //$(".l_s_message_content").text(response.message.text);
              $(".lbg").hide();
              console.log(status)
              
          }, 
          error: function(xhr, status, error) {
              $(".lbg").hide();
              console.log(status)
              console.log(error)
              console.error(xhr.responseText);
          }
      });
  });


  });
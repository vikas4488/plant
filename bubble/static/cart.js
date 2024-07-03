$(document).ready(function(){
   
    $(".plus_or_minus_cart").on('click',function(){
        
        var doaction=$(this).attr("doaction");
        var oldQty = parseInt($(this).closest(".c_list_single").find(".c_list_single_price_total_qty").html());
        console.log(oldQty+" "+doaction);
        if(oldQty<2 && doaction==="minus")
        return;
        var flowerId=$(this).attr("flowerId");
        var $this=$(this);
        $.ajax({
            type:'POST',
            url: updateCartUrl,
            data: {
                'doaction': doaction,
                'flowerId': flowerId,
                'csrfmiddlewaretoken': csrftoken,
            },
            success:function(response){
               $this.siblings('.c_list_single_content_qty_number').html(response.new_quantity);
               $this.closest(".c_list_single").find(".c_list_single_price_total_qty").html(response.new_quantity);
               var newPrice=parseInt($this.attr("newPrice"));
               var new_qty=parseInt(response.new_quantity);
               var newTotoal=newPrice*new_qty;
               $this.closest(".c_list_single").find(".c_list_single_price_total").html("= "+newTotoal);
               var billValue=parseInt($(".c_final_price_value").html());
               if(doaction==="plus")
               billValue=billValue+newPrice;
               else if(doaction==="minus")
               billValue=billValue-newPrice;

               $(".c_final_price_value").html(billValue)
                //alert(response.new_quantity);
            },
            error:function(xhr, status, error){
                alert("unknown error occured please try again");
                
            }
        });
    });
});
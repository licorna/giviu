$(document).ready(function(e){

    reviewListLikes();
    reviewLike();

	$(".select").msDropDown();//custom drop down

    $(".like").click(function(){
        if($(this).hasClass('disabled')){
            alertMessage('Debes hacer login','likeLoginMessage');
        }else{
            var sourceId = $(this).attr('data-source-id');
            var sourceType = $(this).attr('data-source-type');
            newLike(sourceId,sourceType);
            $(this).addClass('active');    
        }
    });

    $('.close').on('click',closeModal);




	 $('.giftcardsDesign').carouFredSel({
        auto: false,
        circular: true,
        infinite: false,
        responsive: true,
		scroll		: {
			
			onAfter : function( data ) { 
				var actualPosition = parseInt($('.selected').html());
				var actualPosition = actualPosition+1;
				$('[name="giftcard-design"').val($('.giftcardsDesign li').attr('id'));
			}
		},
	    pagination  : "#pag",
        prev: $('#prev'),
        next: $('#next')
    });


});

function alertMessage(title,content){
    $('#alertTitle').html(title);
    $('#alertContent').html($('#'+content).html());
    $('#alertMessage').fadeIn('fast');

}


function closeModal(e){
    var closeTo = $(this).attr('data-close');
    $('#'+closeTo).fadeOut();
}

function separador(valor) {
    var nums = new Array();
    var simb = "."; //Éste es el separador
    valor = valor.toString();
    valor = valor.replace(/\D/g, "");   //Ésta expresión regular solo permitira ingresar números
    nums = valor.split(""); //Se vacia el valor en un arreglo
    var long = nums.length - 1; // Se saca la longitud del arreglo
    var patron = 3; //Indica cada cuanto se ponen las comas
    var prox = 2; // Indica en que lugar se debe insertar la siguiente coma
    var res = "";
 
    while (long > prox) {
        nums.splice((long - prox),0,simb); //Se agrega la coma
        prox += patron; //Se incrementa la posición próxima para colocar la coma
    }
 
    for (var i = 0; i <= nums.length-1; i++) {
        res += nums[i]; //Se crea la nueva cadena para devolver el valor formateado
    }
 
    return res;
}

function reviewLike(){
    sourceId =$('.like.big').attr('data-source-id');
    $.get( "/likes/review", { sourceId:sourceId } )
        .done(function( data ) {
        var obj = jQuery.parseJSON(data);
        switch (obj.status) { 
            case "1": 
                $('.like.big').addClass('active');
                break 
            break 
        }
    }); 
}


function reviewListLikes(){
    $('.giftCardModule').each(function(){
        var sourceId = $(this).attr('data-source-id');
        $.get( "/likes/review", { sourceId:sourceId } )
          .done(function( data ) {
            var obj = jQuery.parseJSON(data);
            switch (obj.status) { 
                case "1": 
                    $('.giftCardModule[data-source-id="'+sourceId+'"] .like').addClass('active');
                    break 
                case "0": 
                    $('.giftCardModule[data-source-id="'+sourceId+'"] .like').addClass('nolike');
                    break 
            }

        });
    });
    $('.nolike').tipsy();
}

function newLike(sourceId, sourceType,success,error){
    $.post( "/likes/newLike", { sourceId: sourceId, sourceType:sourceType })
      .done(function(data) {
        var obj = jQuery.parseJSON(data);
        if(obj.status=="sucess"){
            if(success!=""){
                success();
            }
        }else{
            if(error!=""){
                error();
            }

        }

      });
}
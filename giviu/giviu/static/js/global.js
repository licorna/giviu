$(document).ready(function(e){

    //reviewListLikes();
    //reviewLike();
    reviewSpecialOut();
    reviewModalCampaign();
    $('.lb-close').on('click',setCampaign);

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

    $('.special .close').on('click',specialOut);

    $('.close').on('click',closeModal);

    $//('#logout').on('click',logout);
    $('.share').on('click',share);

    $('.mobileActions').on('click',menuDisplay);

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

function reviewSpecialOut(){
    if(localStorage.special_status){
        specialStatus = localStorage.special_status.split(',');
        var campaign = specialStatus[0];
        status = specialStatus[1];
        if(status=='out'){
            $('#'+campaign).addClass('out');
        }
    }
}

function specialOut(){
    var campaign = $(this).parent().attr('id');
    var campaign = [campaign,'out']
    localStorage.setItem('special_status', campaign);
    $('.special').addClass('out');
}

function setCampaign(){
    var d = new Date(); 
    var hoy= new Date(d.getFullYear()+ "/" + (d.getMonth() + 1 ) + "/" + d.getDate());            
    var campaign = [hoy,'out']
    localStorage.setItem('special_modal_status',campaign);
}

function reviewModalCampaign(){
    if(localStorage.special_modal_status){
        var modalStatus = localStorage.special_modal_status.split(',');
        var d = new Date(); 
        var fechaInicio= new Date(modalStatus[0]);
        var hoy= new Date(d.getFullYear()+ "/" + (d.getMonth() + 1 ) + "/" + d.getDate());            
        var fechaResta= hoy-fechaInicio;
        fechaResta=(((fechaResta/1000)/60)/60)/24;   
        fechaResta = parseInt(fechaResta);         
        if(fechaResta>=2) {
            $('[data-lightbox="campaign"]').trigger('click');
        }
    }else{
        $('[data-lightbox="campaign"]').trigger('click');
    }

}

function sendInviteFriends(e){
    console.log(e.to);
    FB.ui({method: 'send',
        message: 'Busca, personaliza y envia regalos a quien quieras cuando quieras. www.giviu.com',
        to: 'cristina.aravena.sanchez,esteldesign',
        title:'Ven a conocer giviu',
        link:'https://www.giviu.com'        
    }, confirmSendInviteFriends);

}

function confirmSendInviteFriends(e){
    $('#alertMessage').fadeOut();
}

function share(e){
    e.preventDefault();
    var url =   $(this).attr('href');
    window.open(url, '', 'menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=400,width=650');
}

function menuDisplay(e){
    $('.mobile').slideToggle('fast');
}

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

function logout(e){
    e.preventDefault();    
    var url = $(this).attr('href');

    if(typeof FB.logout == 'function'){
        if (FB.getAuthResponse()) {
         FB.logout(function(response) { window.location.href =url; }); 
         return;
        }  
    };

}

function moneyFormat(nStr)
{
    nStr += '';
    x = nStr.split('.');
    x1 = x[0];
    x2 = x.length > 1 ? '.' + x[1] : '';
    var rgx = /(\d+)(\d{3})/;
    while (rgx.test(x1)) {
        x1 = x1.replace(rgx, '$1' + '.' + '$2');
    }
    return x1 + x2;
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
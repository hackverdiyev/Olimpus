document.addEventListener("DOMContentLoaded", function(){
    news_contexts=document.getElementsByClassName("news_cont");
    for(var i=0; i<news_contexts.length; i++){
        var news_cont_str=news_contexts[i].innerHTML;
        console.log(news_cont_str);
        if(news_cont_str.length>208){
            news_contexts[i].innerHTML=news_cont_str.substring(0, 209)+" . . .";
        }
    }
})
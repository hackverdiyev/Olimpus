document.addEventListener("DOMContentLoaded", function(){
    numbers=document.getElementsByClassName("number0");
    page=document.getElementsByClassName("go_page_container")[0].dataset.pageId;
    limit=document.getElementsByClassName("go_page_container")[0].dataset.limitId;
    for(var i=limit*(page-1)+1;i<limit*page+1;i++) numbers[i-limit*(page-1)-1].innerHTML=i;
});

var all_prob=document.getElementsByClassName("all_problems")[0];
var solved_prob=document.getElementsByClassName("solved_problems")[0];
var unsolved_prob=document.getElementsByClassName("unsolved_problems")[0];
var type=document.getElementsByClassName("all_problems")[0].dataset.typeId;

if(type=='all'){
    all_prob.style.background='white';
    all_prob.style.color='#4a4abd';
}
if(type=='solved'){
    solved_prob.style.background='white';
    solved_prob.style.color='#4a4abd';
}
if(type=='unsolved'){
    unsolved_prob.style.background='white';
    unsolved_prob.style.color='#4a4abd';
}

function open_view(k){
    var view_div = document.querySelector('.view_page'+k.toString());
    view_div.style.display = "block";
    view_div.animate([{opacity:'0.0'}, {opacity:'1.0'}],
    {duration: 500, fill:'forwards'});

}
function close_view(k){
    var view_div = document.querySelector('.view_page'+k.toString());
    view_div.style.display = "none";
}

document.addEventListener('DOMContentLoaded', function () {
    const viewButtons = document.querySelectorAll('.view_problem');
    const closeButtons = document.querySelectorAll('.close_viewpage');
    viewButtons.forEach(button => {
        button.addEventListener('click', function () {
            const problemId = this.dataset.problemId;
            open_view(problemId);
        });
    });
    closeButtons.forEach(button => {
        button.addEventListener('click', function () {
            const problemId = this.dataset.problemId;
            close_view(problemId);
        });
    });
});

document.addEventListener("keydown", function(event){
    if(event.key == "Escape"){
        if(document.getElementById("view_div").style.display == "block"){
            document.getElementById("view_div").style.display = "none";
        }
    }
});

document.getElementsByClassName("search_btn")[0].addEventListener("click", function(event){
    var search_btn=document.getElementsByClassName("search_btn")[0];
    var inp=document.getElementsByClassName("search_text")[0];
    search_btn.setAttribute("href",search_btn.href+inp.value);
});

document.getElementsByClassName("search_text")[0].addEventListener("keydown", function(event){
    if(event.key=="Enter"){
        var search_btn=document.getElementsByClassName("search_btn")[0];
        search_btn.click();
    }
});
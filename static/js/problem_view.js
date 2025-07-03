other_report=document.getElementById("other_report_cont");
textarea=document.getElementById("report_other_textarea");

other_report.addEventListener("change", function(){
    if(other_report.checked){
        textarea.disabled=false;
    }
    else{
        textarea.disabled=true;
    }
})

let solution_btn = document.querySelector(".solution_context_btn_open");
let solution_span = document.querySelector(".solution_cont_span");
let solution_icn = document.querySelector("#feature_icon");
let solution_div = document.querySelector('.solution_context_container');

var say=0;

if (solution_btn!=null) solution_btn.onclick = () => {
    if(say==0){
        solution_span.innerHTML="Həlli gizlət"
        say=1;
    }
    else{
        solution_span.innerHTML="Həlli göstər"
        say=0;
    }
    solution_icn.classList.toggle("bi-chevron-up");
    solution_div.classList.toggle("opened_solution");
};

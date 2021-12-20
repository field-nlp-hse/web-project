let plainbutton = document.getElementById("plaintext")
let xmlbutton = document.getElementById("xml")
let jsonbutton = document.getElementById("json")
const outputType = $("#output")
const fileInput = $("#FileUploadForm");
const textInput = $("#Input")

function submitToParser(event) {
    event.preventDefault();
    let fileAttached = Boolean(fileInput.prop('files').length === 1);
    let inputPresent = Boolean(textInput.val().length > 0)
    if ($("#transducer").val() === null) {
        alert("Пожалуйста, выберите язык из списка")
        return
    }
    if (fileAttached && inputPresent) {
        alert("Одновременная загрузка через файл и строку ввода недоступна. Удалите файл или очистите строку ввода.")
        return
    } else if (!fileAttached && !inputPresent) {
        alert("Введите текст в строку ввода или прикрепите файл в формате .txt")
        return
    }
    let targetId = event.target.id;
    outputType.val(targetId);
    $( '#parserForm' ).submit();
}



$( document ).ready(function() {
    plainbutton.addEventListener("click", submitToParser)
    xmlbutton.addEventListener("click", submitToParser)
    jsonbutton.addEventListener("click", submitToParser)
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    });
})
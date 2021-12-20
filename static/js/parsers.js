const plainbutton = $("#plaintext");
const xmlbutton = $("#xml");
const jsonbutton = $("#json");
const outputType = $("#output")

plainbutton.on("click", function(event) {
    return true;
});

xmlbutton.on("click", function(event) {
    outputType.val = "xml"
    return true;
});

jsonbutton.on("click", function(event) {
    outputType.val = "json"
    return true;
});
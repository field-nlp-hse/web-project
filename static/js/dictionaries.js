function searchTable() {
  var input, filter, table, tr, td_name, i, txtValue_name, td_country, txtValue_country, td_third, txtValue_third;
  input = document.getElementById("myInput");
  filter = input.value.toUpperCase();
  table = document.getElementById("myTable");
  tr = table.getElementsByTagName("tr");
  for (i = 0; i < tr.length; i++) {
    td_name = tr[i].getElementsByTagName("td")[0];
    td_country = tr[i].getElementsByTagName("td")[1];
    if (td_name && td_country) {
      txtValue_name = td_name.textContent || td_name.innerText;
      txtValue_country = td_country.textContent || td_country.innerText;
      if ((txtValue_name.toUpperCase().indexOf(filter) > -1) || (txtValue_country.toUpperCase().indexOf(filter) > -1)) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  }
}

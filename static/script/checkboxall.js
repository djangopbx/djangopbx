function SelectAll() {
  const a = document.getElementById("pbx-action-toggle");
  const b = document.getElementsByClassName("pbx-action-select");
  const c = b.length;
  var  d;
  for (d=0; d<c; d++) {
    if (a.checked == true) {
      b[d].checked = true;
    } else {
      b[d].checked = false;
    }
  }
}

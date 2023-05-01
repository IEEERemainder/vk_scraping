// init
function save(filename, data) {
    const blob = new Blob([data], {type: 'text/csv'});
    if(window.navigator.msSaveOrOpenBlob) {
        window.navigator.msSaveBlob(blob, filename);
    }
    else{
        const elem = window.document.createElement('a');
        elem.href = window.URL.createObjectURL(blob);
        elem.download = filename;        
        document.body.appendChild(elem);
        elem.click();        
        document.body.removeChild(elem);
    }
}
a = [];
state = true;
CHUNC_SIZE = 500;

// iteration. automatically downloads part of size defined in CHUNC_SIZE
for (el of document.querySelectorAll("._post")) {
	a.push(el.innerHTML); 
	el.parentElement.removeChild(el); 
} 
state = !state;
window.scroll(0, state ? 100 : 200);
if (a.length > CHUNC_SIZE) {
	save("group_name_part.json",JSON.stringify(a));
	a = [];
	state = true;
}

// download rest of posts then end reached
save("group_name_part.json",JSON.stringify(a));

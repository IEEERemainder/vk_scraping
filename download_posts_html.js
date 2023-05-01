// init
a = [];
state = true;

// iteration
for (el of document.querySelectorAll("._post")) {
	a.push(el.innerHTML); 
	el.parentElement.removeChild(el); 
} 
state = !state;
window.scroll(0, state ? 100 : 200);

// finalizer/download part (recommended with > 100 posts)
save("group_name_posts.json",JSON.stringify(a));
a = [];
state = true;

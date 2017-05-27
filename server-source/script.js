function set_date_and_time() {
	if (document.getElementById("inserttime").value != '') {
	// Prefilled on edit page, don't change
		return
	}
	now = new Date()
	h = now.getHours()
	m = now.getMinutes()
	if (h <= 9) { h = "0" + h }
	if (m <= 9) { m = "0" + m }
	document.getElementById("inserttime").value = h + ":" + m
	day = now.getDate()
	month = now.getMonth() + 1
	year = now.getFullYear()
	document.getElementById("insertdate").value = day + "/" + month + "/" + year
}

function reset_form() {
	document.getElementById("drain_data_form").reset()
	set_date_and_time()
	return false
}

function on_focus_tip() {
	this.parentNode.childNodes[2].style.display = 'inherit';
}

function on_blur_tip() {
	this.parentNode.childNodes[2].style.display = 'none';
}


function register_events(object) {
	object.addEventListener('blur', on_blur_tip, false)
	object.addEventListener('focus', on_focus_tip, false)
	object.addEventListener('mouseover', on_focus_tip, false)
	object.addEventListener('mouseout', on_blur_tip, false)
}

function calibrate() {
	tooltip_items = ["additionalnotes", "earlycomplications", "indication", "patientposition", "drainsite", "sutureclosuretechnique"]
	for (i=0;i<tooltip_items.length;i++)
	{
		register_events(document.getElementById(tooltip_items[i]))
	}
	set_date_and_time()
	prefill_details()
}

function check_form() {
	missing_data = false
	cant_be_blank = ["Name", "CHInumber", "indication", "inserteename", "speciality", "grade"]
	for (i=0;i<cant_be_blank.length;i++) {
		if (document.getElementById(cant_be_blank[i]).value == '') {
			document.getElementById(cant_be_blank[i]).className = "missing_data"
			missing_data = true
		}
	}
	if (missing_data) {
		alert("Please fill in the form completely!\n(Especially the highlighted fields)")
		return false
	}
	if (readCookie("saved_details") != "no") {
		remember_me()
	}
	return true
}

function prefill_details() {
	document.getElementById("admin_box").className = "admin_box"
	if (readCookie("saved_details") == "yes")
	{
		cookie_load = ["inserteename", "speciality", "grade"]
		for (i=0;i<cookie_load.length;i++) {
			document.getElementById(cookie_load[i]).value = readCookie(cookie_load[i])
		}
		document.getElementById("remember_me").className = "hidden"
	} else {
		document.getElementById("clear_cookies").className = "hidden"
		document.getElementById("dont_remember_me").className = "hidden"
	}
	
}

function clear_cookies() {
	cookies = ["saved_details", "inserteename", "speciality", "grade"]
	for (i=0;i<cookies.length;i++) {
		eraseCookie(cookies[i])
	}
	document.getElementById("clear_cookies").className = "hidden"
}

function remember_me() {
	cookie_save = ["inserteename", "speciality", "grade"]
	createCookie("saved_details", "yes")
	for (i=0;i<cookie_save.length;i++) {
		createCookie(cookie_save[i], document.getElementById(cookie_save[i]).value, 365)
	}
	document.getElementById("clear_cookies").className = ""
	document.getElementById("remember_me").className = "hidden"
	document.getElementById("dont_remember_me").className = ""
}

function dont_remember_me() {
	clear_cookies()
	createCookie("saved_details", "no")
	document.getElementById("clear_cookies").className = "hidden"
	document.getElementById("dont_remember_me").className = "hidden"
	document.getElementById("remember_me").className = ""
}


 

/*****	FROM:	http://www.quirksmode.org/js/cookies.html *****/


function createCookie(name,value,days) {
	if (days) {
		var date = new Date();
		date.setTime(date.getTime()+(days*24*60*60*1000));
		var expires = "; expires="+date.toGMTString();
	}
	else var expires = "";
	document.cookie = name+"="+value+expires+"; path=/";
}

function readCookie(name) {
	var nameEQ = name + "=";
	var ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++) {
		var c = ca[i];
		while (c.charAt(0)==' ') c = c.substring(1,c.length);
		if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
	}
	return false;
}

function eraseCookie(name) {
	createCookie(name,"",-1);
}

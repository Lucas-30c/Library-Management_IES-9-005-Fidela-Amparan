document.getElementById("btn_menu").addEventListener("click", mostrar_menu);

document.getElementById("back_menu").addEventListener("click", ocultar_menu);

nav = document.getElementById("nav");
background_menu = document.getElementById("back_menu");

function mostrar_menu() {

	nav.style.right = "0px";
	background_menu.style.display = "block";
}

function ocultar_menu() {

	nav.style.right = "-250px";
	background_menu.style.display = "none";
}







$(document).ready(function () {
	$(".open").click(function () {
		$(".nameUser").css('display', 'block');

	});
	$(".close").click(function () {
		$(".nameUser").css('display', 'none');
	});
});





var swiper = new Swiper('.mySwiper', {
	navigation: {
		nextEl: '.swiper-button-next',
		prevEl: '.swiper-button-prev'
	},
	effect: "slider",
	slidesPerView: 3,
	spaceBetween: 25,
	grabCursor: true,
	centeredSlides: true,
	slidesPerView: "auto",
	// init: false,
	pagination: {
		el: '.swiper-pagination',
		clickable: true,
	},
});


window.onload = () => {

	if (window.scrollY > 80) {
		document.querySelector('.heading').classList.add('active');
	} else {
		document.querySelector('.heading').classList.remove('active');
	}

	fadeOut();

}

$(document).ready(function () {
	$("table.display tfoot th").each(function () {
		var title = $(this).text();
	});
	var table = $("table.display").DataTable({
		"dom": 'B<"float-right"f>t<"float-left"l><"float-right"p><"clearfix">',
		"language": {
			"url": "https://cdn.datatables.net/plug-ins/1.10.19/i18n/Spanish.json",
			"searchPlaceholder": "Buscar un socio"
		},
		autoWidth: false,
	});

	$("table.display thead").on("keyup", "input", function () {
		table.column($(this).parent().index())
			.search(this.value)
			.draw();
	});
});

const button = document.querySelector(".button");
button.addEventListener("mousedown", () => button.classList.add("clicked"));




// pwShowHide.forEach(eyeIcon => {
// 	eyeIcon.addEventListener("click", () => {
// 		pwFields.forEach(pwField => {
// 			if (pwField.type === "password") {
// 				pwField.type = "text";

// 				pwShowHide.forEach(icon => {
// 					icon.classList.replace("uil-eye-slash", "uil-eye");
// 				})
// 			} else {
// 				pwField.type = "password";

// 				pwShowHide.forEach(icon => {
// 					icon.classList.replace("uil-eye", "uil-eye-slash");
// 				})
// 			}
// 		})
// 	})
// })


// window.addEventListener("loader-container", function(){
// 	document.getElementById("loader-container")
// })




// function loader() {
// 	document.querySelector('.loader-container').classList.add('active');
// }

/*
function fadeOut() {
	setTimeout(loader, 2600);
}
*/





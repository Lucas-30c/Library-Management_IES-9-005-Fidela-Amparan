$('#socio').select2({
	theme: "bootstrap-5",
	width: $(this).data('width') ? $(this).data('width') : $(this).hasClass('w-100') ? '100%' : 'style',
	placeholder: $(this).data('placeholder'),
	"language": {
		"noResults": function () {
			return "<a href='#' class='btn btn-danger'>No hay resultados</a>";
		}
	},
	escapeMarkup: function (markup) {
		return markup;
	}
});



let formPrestamo = document.querySelector("#formPrestamo");
let botonRegistrar = document.querySelector("#botonRegistrar");

function validar() {

	let desabilitar = false;

	if (formPrestamo.socio.value == "") {
		desabilitar = true;
	}

	if (desabilitar == true) {
		botonRegistrar.disabled = true;
	} else {
		botonRegistrar.disabled = false;
	}
}
$('#socio').on('select2:select', function (e) {
	validar()
});
formPrestamo.addEventListener("keyup", validar)


























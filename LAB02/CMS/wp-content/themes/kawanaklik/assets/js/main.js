/* KawaNaKlik – rozwijane menu na telefonach. */
( function () {
	const header = document.querySelector( '.site-header' );
	const toggle = document.querySelector( '.nav-toggle' );

	if ( ! header || ! toggle ) {
		return;
	}

	toggle.addEventListener( 'click', function () {
		const open = header.classList.toggle( 'is-open' );
		toggle.setAttribute( 'aria-expanded', open ? 'true' : 'false' );
	} );
} )();

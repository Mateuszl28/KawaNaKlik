<?php
/**
 * Obszary widgetów.
 *
 * @package KawaNaKlik
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Akcja widgets_init – rejestruje obszar widgetów w stopce.
 */
function kawanaklik_widgets(): void {
	register_sidebar(
		array(
			'name'          => __( 'Stopka', 'kawanaklik' ),
			'id'            => 'footer-1',
			'description'   => __( 'Widgety wyświetlane w stopce strony.', 'kawanaklik' ),
			'before_widget' => '<div id="%1$s" class="widget %2$s">',
			'after_widget'  => '</div>',
			'before_title'  => '<h3 class="widget__title">',
			'after_title'   => '</h3>',
		)
	);
}
add_action( 'widgets_init', 'kawanaklik_widgets' );

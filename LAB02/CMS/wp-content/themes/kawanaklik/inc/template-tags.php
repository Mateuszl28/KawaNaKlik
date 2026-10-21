<?php
/**
 * Pomocnicze funkcje szablonów.
 *
 * @package KawaNaKlik
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Wyświetla datę publikacji, autora i kategorie wpisu.
 */
function kawanaklik_post_meta(): void {
	printf(
		'<p class="post-meta"><time datetime="%1$s">%2$s</time> · %3$s %4$s</p>',
		esc_attr( get_the_date( 'c' ) ),
		esc_html( get_the_date() ),
		esc_html__( 'autor:', 'kawanaklik' ),
		esc_html( get_the_author() )
	);

	$categories = get_the_category_list( ', ' );
	if ( $categories ) {
		printf( '<p class="post-cats">%1$s %2$s</p>', esc_html__( 'Kategorie:', 'kawanaklik' ), wp_kses_post( $categories ) );
	}
}
